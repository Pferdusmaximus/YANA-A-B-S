# Teamportal: Bereitstellung auf dem IONOS-VPS

**Stand: 17.11.2026 · Manuelles Deployment im Projektverlauf mehrfach erfolgreich durchgeführt**

## 1. Ziel und Sicherheitsprinzip

Der produktive Dienst `yana-api` nutzt `~/yana-backend`. Eine separate GitHub-Arbeitskopie (`~/yana-deploy-source`) und ein separater Test-Codeordner (`~/yana-portal-test`) verhindern, dass Änderungen am Python-Code automatisch die laufende Website ersetzen. Der Betreiber arbeitet bislang **über die grafische IONOS-Ubuntu-Konsole**, nicht über SSH vom Windows-Rechner.

**Einschränkung:** Die Testkopie verwendet bisher denselben PostgreSQL-Datenbestand (`app_db`) wie die Produktion. Für Schreibtests daher nur klar ausgewiesene fiktive Datensätze verwenden und Ausgangswerte dokumentieren. Das Verzeichnis ist eine *Code-Testumgebung*, keine echte vollständige Staging-Umgebung.

## 2. Testversion synchronisieren

```bash
cd ~/yana-deploy-source
git status
git pull --ff-only origin main

# Nur nach Prüfung der GitHub-Version:
cp ~/yana-deploy-source/services/api/portal_facilities.py ~/yana-portal-test/portal_facilities.py
cp ~/yana-deploy-source/services/api/templates/portal/hilfestellen.html ~/yana-portal-test/templates/portal/hilfestellen.html
cp ~/yana-deploy-source/services/api/templates/portal/hilfestellen_bearbeiten.html ~/yana-portal-test/templates/portal/hilfestellen_bearbeiten.html
cp ~/yana-deploy-source/services/api/static/css/style.css ~/yana-portal-test/static/css/style.css
```

Falls auch `main.py`, `portal.py` oder `website.py` geändert wurden, die benötigten Dateien **explizit und bewusst** übertragen. Bei noch nicht implementierten Features niemals pauschal den kompletten Ordner überschreiben. Besonders wichtig ist der konsistente Template-Name `hilfestellen_bearbeiten.html`.

## 3. Syntax und Tests vor Deployment

```bash
cd ~/yana-portal-test
source ~/yana-backend/.venv/bin/activate
python -m py_compile main.py website.py portal.py portal_facilities.py database.py
python -c "from main import app; print('FastAPI-Import erfolgreich')"
```

Danach HTTP/Session-/CSRF- und bei Änderungen am Schreibcode gezielte [Portalspeichertests](teamportal-tests.md) durchführen. Ein Schreiben im Testordner verändert die **echte** Datenbank; Rücksetzung und Audit prüfen.

## 4. Sicherung der produktiven Version

Vor jeder Veröffentlichung:

```bash
mkdir -p ~/yana-backups
chmod 700 ~/yana-backups
BACKUP="$HOME/yana-backups/pre-deploy-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$BACKUP" --exclude='./.venv' --exclude='./.env' -C "$HOME/yana-backend" .
echo "$BACKUP"
```

Das sichert den vorhandenen Code und die Templates, **nicht** die PostgreSQL-Datenbank. Den ausgegebenen Backup-Pfad notieren. Für echte DB-Migrationen und produktive Datensätze sind eigene konsistente DB-Backups und getestete Restores erforderlich.

## 5. Getestete Dateien produktiv übernehmen

Nur die tatsächlich geänderten, in der Testumgebung geprüften Dateien kopieren. Für die zuletzt umgesetzte Bearbeitungsfunktion:

```bash
cp ~/yana-portal-test/portal_facilities.py ~/yana-backend/portal_facilities.py
cp ~/yana-portal-test/templates/portal/hilfestellen.html ~/yana-backend/templates/portal/hilfestellen.html
cp ~/yana-portal-test/templates/portal/hilfestellen_bearbeiten.html ~/yana-backend/templates/portal/hilfestellen_bearbeiten.html
cp ~/yana-portal-test/static/css/style.css ~/yana-backend/static/css/style.css
```

`main.py`, `.env`, `database.py` und `.venv` sind für **diesen** reinen Formular-/Audit-Release nicht erneut kopiert worden. Bei zukünftigen Änderungen muss jeder betroffene Codepfad separat bewertet werden.

## 6. Prüfungen im produktiven Verzeichnis

```bash
cd ~/yana-backend
source .venv/bin/activate
python -m py_compile main.py portal.py portal_facilities.py
python -c "from main import app; print('FastAPI-Import erfolgreich')"
grep -n 'hilfestellen_bearbeiten.html' portal_facilities.py
ls templates/portal/hilfestellen_bearbeiten.html
```

Die lokalen GET-Smoke-Tests können mit `TestClient(app, base_url="https://testserver", follow_redirects=False)` durchgeführt werden. Ohne Login liefern `/portal/hilfestellen` und `/portal/hilfestellen/1/edit` erwartungsgemäß HTTP 303. Öffentlich zugängliche Endpunkte sollten weiterhin HTTP 200 liefern.

**Erst bei erfolgreichen Prüfungen** den Dienst neu starten:

```bash
sudo systemctl restart yana-api
sudo systemctl status yana-api --no-pager
```

Bei Fehlern:

```bash
sudo journalctl -u yana-api -n 40 --no-pager
```

**Dieser `journalctl`-Befehl liest ausschließlich Logs.** Er verändert keine Dateien, stoppt keinen Dienst und löscht keine Daten.

## 7. Browserprüfung nach dem Neustart

1. HTTPS-Startseite `/` aufrufen.
2. `/portal/login` öffnen und als Administrator anmelden.
3. `/portal/dashboard` und `/portal/hilfestellen` aufrufen.
4. Bearbeiten-Formular eines **fiktiven** Eintrags testen.
5. Teständerung speichern, Erfolgsmeldung und DB-/Audit-Eintrag kontrollieren; Ursprungswert wiederherstellen.
6. Logout und Weiterleitung geschützter Seiten prüfen.
7. JSON-Endpunkte für Flutter (`/hilfestellen`, `/kategorien`, `/notfallnummern`) erneut prüfen.

Diese Schritte wurden im Projektverlauf für das veröffentlichte Bearbeitungsfeature erfolgreich durchgeführt.

## 8. Rückfall und weitere Verbesserung

Bei fehlgeschlagenem Deploy **zuerst** Logs prüfen. Für die Wiederherstellung das konkret notierte Backup in ein separates Verzeichnis entpacken und benötigte Dateien kontrolliert zurückkopieren; anschließend Dienst neu starten und Endpunkte prüfen. Kein pauschales Entpacken über `.env` oder `.venv` und keine unangekündigten DB-Rollbacks durchführen. Da eine neue UI-Funktion Tabellen verändern kann, ist ein Code-Rollback nicht automatisch ein Datenbank-Rollback.

Zukünftige Verbesserung: eigener Staging-Datenbankcluster, versionierte Migrationsskripte, automatisierte Release-Pipeline, Rollback-Anleitung mit geprüftem Restore sowie TLS-/Backup-Monitoring.
