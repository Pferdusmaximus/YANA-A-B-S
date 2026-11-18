# Verwaltungsportal: Deployment auf dem IONOS-VPS

**Stand: 18. November 2026 · Freigabe- und Partnerfunktionen erfolgreich produktiv bereitgestellt**

## 1. Ziel und Umgebungen

Das Repository wird lokal unter Windows/VS Code gepflegt und nach GitHub übertragen. Auf dem VPS sind die Kopien bewusst getrennt:

| Zweck | Verzeichnis |
|---|---|
| GitHub-Arbeitskopie | `~/yana-deploy-source` |
| Testcode | `~/yana-portal-test` |
| Produktiver FastAPI-Code | `~/yana-backend` |
| Python-Umgebung | `~/yana-backend/.venv` |
| Produktive Konfiguration | `~/yana-backend/.env` |
| Systemd-Dienst | `yana-api` |

**Achtung:** Test- und Produktivcode greifen derzeit auf dieselbe PostgreSQL-Datenbank `app_db` zu. Ein Test ist also nicht automatisch datenbankisoliert. Keine echten oder sensiblen Datensätze für Tests verwenden.

## 2. Entwicklung und GitHub

Neue Python-Dateien, Jinja2-Templates und CSS werden **manuell in VS Code** erstellt und geprüft. Temporäre ZIP-Transportpakete und Integrationshelfer sind nicht Teil des benötigten Backends.

```powershell
git status
python -m py_compile services/api/main.py services/api/portal_facility_changes.py
git add services/api/main.py services/api/portal_facility_changes.py
git diff --cached
git commit -m "Describe implemented feature"
git pull --rebase origin main
git push origin main
```

Beim `git add` immer nur tatsächlich geänderte und überprüfte Dateien verwenden. `.env`, Passwörter, Datenbankdumps und private Schlüssel gehören nicht ins Repository.

## 3. GitHub-Code auf dem VPS testen

```bash
cd ~/yana-deploy-source
git pull --ff-only origin main

# Die tatsächlich geänderten Dateien bewusst in den Testordner kopieren:
cp services/api/main.py ~/yana-portal-test/main.py
cp services/api/portal_facility_changes.py ~/yana-portal-test/portal_facility_changes.py
cp services/api/templates/portal/aenderung_bearbeiten.html \
  ~/yana-portal-test/templates/portal/aenderung_bearbeiten.html
cp services/api/templates/portal/aenderungen_pruefen.html \
  ~/yana-portal-test/templates/portal/aenderungen_pruefen.html

cd ~/yana-portal-test
source ~/yana-backend/.venv/bin/activate
python -m py_compile main.py portal_facility_changes.py
python -c "from main import app; print('FastAPI-Import erfolgreich')"
```

Die Beispiele betreffen den zuletzt eingeführten Änderungsrouter. Bei jeder Veröffentlichung müssen **alle tatsächlich geänderten** Dateien, einschließlich `hilfestellen.html`, `style.css` oder anderer Module, übertragen werden. Vor einer Datenbankmigration immer Backup, Schema und benötigte Rechte prüfen. Die Änderungstabelle `portal_facility_change` ist bereits angelegt; ihre Migration darf nicht erneut blind ausgeführt werden.

## 4. Vor dem produktiven Überschreiben sichern

```bash
mkdir -p ~/yana-backups
chmod 700 ~/yana-backups
umask 077
BACKUP="$HOME/yana-backups/pre-deploy-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$BACKUP" --exclude='./.venv' --exclude='./.env' \
  -C "$HOME/yana-backend" .
echo "Backup erstellt: $BACKUP"
```

Das sichert Anwendungsdateien, **nicht** PostgreSQL. Vor DB-Änderungen zusätzlich einen konsistenten `pg_dump` an einen geschützten Ort erstellen. Den Restore nicht auf der produktiven Datenbank testen.

## 5. Produktivübernahme und Prüfung

Nach erfolgreich bestandenen Tests nur die betroffenen Dateien aus `~/yana-portal-test` nach `~/yana-backend` übernehmen. Für die Änderungsfreigabe gehörten dazu:

```bash
cp ~/yana-portal-test/main.py ~/yana-backend/main.py
cp ~/yana-portal-test/portal_facility_changes.py ~/yana-backend/portal_facility_changes.py
cp ~/yana-portal-test/templates/portal/aenderung_bearbeiten.html \
  ~/yana-backend/templates/portal/aenderung_bearbeiten.html
cp ~/yana-portal-test/templates/portal/aenderungen_pruefen.html \
  ~/yana-backend/templates/portal/aenderungen_pruefen.html
cp ~/yana-portal-test/templates/portal/hilfestellen.html \
  ~/yana-backend/templates/portal/hilfestellen.html
cp ~/yana-portal-test/static/css/style.css \
  ~/yana-backend/static/css/style.css
```

Dann:

```bash
cd ~/yana-backend
source .venv/bin/activate
python -m py_compile main.py portal_facility_changes.py
python -c "from main import app; print('FastAPI-Import erfolgreich')"
sudo systemctl restart yana-api
sudo systemctl status yana-api --no-pager
```

**Erst nach erfolgreichen Syntax-, Import- und HTTP-Tests** den Dienst neu starten. Bei Fehlern `sudo journalctl -u yana-api -n 40 --no-pager` auswerten.

## 6. Browser- und API-Smoke-Tests

1. Öffentliche HTTPS-Website sowie `/health`, `/hilfestellen`, `/kategorien` und `/notfallnummern` prüfen.
2. Als Administrator anmelden und die gesamte Hilfestellenübersicht öffnen.
3. Als Partner anmelden und kontrollieren, dass nur zugewiesene Einrichtungen erscheinen.
4. Bei einer **fiktiven veröffentlichten** Einrichtung das Änderungsformular öffnen; keine unbekannten Daten ändern.
5. Als Administrator `/portal/aenderungen` öffnen; als Partner muss diese Seite gesperrt sein.
6. In einer getrennten, ausdrücklich dafür vorgesehenen Testphase mit fiktiven Daten den vollständigen Speichern-/Einreichen-/Freigeben-Ablauf prüfen.
7. Logout und Session-Schutz testen.

Der vollständige fiktive Änderungsworkflow wurde am 18.11.2026 bereits erfolgreich ausgeführt und nach dem Deployment im Browser überprüft.

## 7. Rollback und Grenzen

Bei Problemen zuerst Logs und Versionsstand prüfen. Sicherungsdateien nicht ungeprüft über `.env` oder `.venv` entpacken. Ein Code-Rollback setzt **keine** Datenbankmigration und keine bereits freigegebenen Einträge zurück. Die alte Version von `main.py` darf nicht wieder eine unfilterte öffentliche Hilfestellenliste aktivieren. Bei Unsicherheit die öffentliche Route absichern oder den Fehler gezielt beheben.

Für zukünftige Releases sind separate Staging-Datenbank, getesteter Restore, fest versionierte Migrationsskripte und reproduzierbare Abhängigkeiten sinnvoll.
