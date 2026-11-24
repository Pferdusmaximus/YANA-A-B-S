# Verwaltungsportal: Deployment auf dem IONOS-VPS

**Stand: 24. November 2026 · Standortverwaltung/Design produktiv; Geoapify-Neuanlage in Testumgebung geprüft, Deployment ausstehend**

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

## 8. Nachtrag 23.11.2026: Partnerverwaltung deployen

Für die neuen Funktionen wurden im Projektverlauf folgende Dateien nach erfolgreichen TestClient- und Integrationstests gemeinsam übernommen:

```text
main.py                        # Bindet partners_router und password_router ein
portal.py                      # Pflicht-Passwortwechsel und Login-Weiterleitung
portal_partners.py             # Partner-CRUD im eingeschränkten Schulprojekt-Umfang
portal_password.py             # Eigenes Passwort ändern
templates/portal/partner.html
templates/portal/partner_erstellt.html
templates/portal/passwort_aendern.html
templates/portal/dashboard.html
static/css/style.css
```

**Wichtig:** `portal.py`, `portal_password.py`, `main.py` und die Kontoerstellung müssen als kompatibler Stand bereitgestellt werden. Andernfalls kann ein neu angelegter Account mit `must_change_password=TRUE` nicht regulär arbeiten. Die DB-Spalte `portal_account.must_change_password` muss vor dem Deployment existieren. Die vier Dateien des anschließenden Lifecycle-Updates (`portal_partners.py`, `partner.html`, `partner_erstellt.html`, `style.css`) wurden nach zwölf erfolgreichen Integrationstests separat übernommen.

```bash
cd ~/yana-backend
source .venv/bin/activate
python -m py_compile main.py portal.py portal_partners.py portal_password.py
python -c "from main import app; print('FastAPI-Import erfolgreich')"
sudo systemctl restart yana-api
sudo systemctl status yana-api --no-pager
```

Für Tests ausschließlich fiktive Accounts verwenden und daran denken, dass Test- und Produktivcode **dieselbe Datenbank** benutzen. Die manuelle Erstellung eines Testpartners muss nach dem Test einschließlich Sessions/Zuordnungen bereinigt werden. Bei einem Code-Rollback ist das bereits migrierte Datenbankschema gesondert zu betrachten; kein blindes Zurückspielen von SQL-Dateien.

Detaillierter Ablauf und Ergebnisse: [Benutzerverwaltung](teamportal-benutzerverwaltung.md) und [Tests](teamportal-tests.md).

## Ergänzung: Geoapify-Neuanlage produktiv schalten (noch NICHT bestätigt)

**Checkpoint 24.11.2026:** Die neue Adressmaske, echte Geoapify-Abfrage, signierte Standortbestätigung, Entwurf mit/ohne Koordinaten, Audit und Manipulationsschutz wurden erfolgreich unter `~/yana-portal-test` getestet. Die **Bereitstellung auf `~/yana-backend` wurde danach nur angeleitet, nicht als ausgeführt bestätigt**.

Zum nächsten Termin, nach einem Backup und der Prüfung der systemd-Konfiguration, diese **sechs** zusammengehörigen Dateien aus dem getesteten Verzeichnis übernehmen:

```text
geocoding_service.py
portal_facilities_create.py
templates/portal/hilfestellen_neu.html
static/js/yana-geocoding.js
static/css/style.css
templates/base.html
```

Den Schlüssel nur als `GEOAPIFY_API_KEY` in der geschützten produktiven `.env` konfigurieren; vorher den für `yana-api` verwendeten Ladepfad verifizieren. **Nicht** `.env` aus der Testkopie kopieren. Danach Syntax/Import prüfen, schreibfreie Smoke-Tests durchführen, `yana-api` neu starten und das Formular `/portal/hilfestellen/neu` im Browser mit einer bekannten **öffentlichen** Testadresse kontrollieren. Bei Fehlern Logdateien prüfen und nicht blind Migrationen oder den gesamten API-Ordner überschreiben.

Die PostgreSQL-Schemaänderung für nullable Koordinaten und die Freigabetabelle sind bereits durchgeführt. Die API für die **öffentliche Anzeige** bleibt unabhängig von Geoapify durch den eigenen [Standortschutz](standort-datenschutz.md) abgesichert. Für volle Schritte: [Wiedereinstieg](weiterarbeit.md) und [Geocoding](geocoding.md).
