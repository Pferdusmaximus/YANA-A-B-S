# Wiedereinstieg: aktueller Stand und nächste Aufgaben

**Projekt-Checkpoint: Dienstag, 24. November 2026 · Bewusste Pause nach erfolgreich abgeschlossenem Geoapify-Speichertest.**

!!! success "Wo wir weitermachen"
    **Die Geoapify-Erweiterung wurde in `~/yana-portal-test` vollständig getestet.** Der letzte bestätigte Schritt ist der Speichertest mit und ohne Koordinaten, manipulierter Bestätigung und anschließendem `ROLLBACK`. **Die Veröffentlichung der neuen Adresseingabe in `~/yana-backend` ist noch nicht als durchgeführt bestätigt.** Beim nächsten Termin beginnen wir daher mit **Produktivkonfiguration, Backup, Übernahme der sechs Dateien, Restart und Browserprüfung** – nicht mit erneuter Implementierung oder Tests von Grund auf.

## 1. Was ist bis zur Pause abgeschlossen?

| Bereich | Verifizierter Stand |
|---|---|
| Server, Website, API | IONOS-VPS mit FastAPI, PostgreSQL, Nginx/HTTPS; erreichbar |
| Website-Design | **Weiß-lila YANA-Design** inklusive Navigation/Logout im Browser produktiv bestätigt |
| Verwaltungsportal | Gemeinsames Login; `admin` und `partner`, CSRF, Argon2, Sessions |
| Hilfestellen und Freigaben | Entwurf/Prüfung/Veröffentlichung, getrennte Änderungsvorschläge, Audit |
| Partnerverwaltung | Account-Erstellung, Zuordnungen, Pflicht-Passwortwechsel, Deaktivierung/Reaktivierung, Reset produktiv |
| Standortdatenschutz | Öffentliche API schützt Adresse/Koordinaten über Einzel- und Typfreigabe; Admin-Tabelle `/portal/standorte` und DB-Trigger getestet und produktiv |
| Geoapify-Anbindung | **Echte externe API-Abfrage und vollständige FastAPI-/Speichertests bestanden** |
| Geoapify-Deployment | **Offen / noch nicht bestätigt** |
| Flutter-App | Daten-/API-Schicht getestet, vollständige UI und Nullable-Koordinaten-Verhalten noch nicht abschließend bestätigt |

## 2. Nächster Termin: genau diese Schritte

1. **Produktivcode sichern**: `~/yana-backend` vor dem Austausch der bestehenden Dateien mit einem Zeitstempel-Backup schützen. Das schützt Dateien, nicht die Datenbank.
2. **Dienstkonfiguration prüfen**: `sudo systemctl show yana-api -p WorkingDirectory`; die geschützte Konfiguration in `~/yana-backend/.env` vorbereiten, insbesondere `GEOAPIFY_API_KEY`. **Keinen Schlüssel in GitHub oder MkDocs eintragen.**
3. **Sechs getestete Dateien übernehmen** (nicht den ganzen API-Ordner überschreiben):
   - `geocoding_service.py`
   - `portal_facilities_create.py`
   - `templates/portal/hilfestellen_neu.html`
   - `static/js/yana-geocoding.js`
   - `static/css/style.css`
   - `templates/base.html`
4. **Import/Smoke-Test**: Syntax, `from main import app`, `GET /`, `GET /hilfestellen`, Login, geschütztes Anlegeformular, JS/CSS prüfen.
5. **Dienst neu starten und kontrollieren**: `sudo systemctl restart yana-api`, `sudo systemctl status yana-api --no-pager`, bei Fehlern `sudo journalctl -u yana-api -n 50 --no-pager`.
6. **Browserprüfung** unter `/portal/hilfestellen/neu`: strukturierte Adresse, Button „Standort ermitteln“, bestätigte Geoapify-Antwort; hierfür ausschließlich eine **öffentlich bekannte Testadresse** verwenden. Nicht ohne Not weitere Datensätze anlegen.
7. **Produktivdeployment in dieser Doku nachtragen**, nachdem es im Browser tatsächlich geprüft wurde.

Die vollständige Architektur, Sicherheitsgrenzen und Testnachweise stehen unter [Geoapify-Geocoding](geocoding.md). Weitere Betriebsdetails unter [Portal-Deployment](teamportal-deployment.md).

## 3. Anschließend geplante Verbesserungen

- Bestehende Hilfestellen ebenfalls per Adresse/Geocoding bearbeiten können; derzeit ist nur **Neuanlage** auf die neue Eingabe vorbereitet.
- Flutter-Kartenmarker und Navigation auf `null`-Koordinaten prüfen und anpassen.
- Vollständiges Website- und Portal-Regressionstestprotokoll ausführen.
- Separates PostgreSQL-Testsystem einrichten: `~/yana-portal-test` und `~/yana-backend` greifen bislang auf **dieselbe** `app_db` zu.
- Vertrauliche Einrichtungen fachlich prüfen: neben Adresse/Koordinaten auch Name, Telefonnummer, E-Mail und Kapazität auf Rückschlüsse untersuchen.
- Audit der Partner-/Accountaktionen, Backup-Restore-Probe, sichere Startpasswortübergabe und ggf. MFA ergänzen.
- Mobile App-Oberfläche und reale Hilfsangebote erst nach fachlicher und rechtlicher Freigabe veröffentlichen.

## 4. Entwicklungsorte

| Zweck | Ort |
|---|---|
| Windows-/VS-Code-Quellordner | `YANA-A-B-S/services/api/` |
| GitHub-Kopie auf VPS | `~/yana-deploy-source/` |
| Getestete Backend-Dateien | `~/yana-portal-test/` |
| Produktiver FastAPI-Code | `~/yana-backend/` |
| Produktive Konfiguration | `~/yana-backend/.env` |
| Produktiver Dienst | `yana-api` |
| Datenbank | `app_db` in PostgreSQL, auch von der Testkopie verwendet |

Es wird über die **grafische IONOS-/Ubuntu-Konsole** gearbeitet. GitHub-Push allein führt noch **kein** produktives Deployment durch.

## 5. Dokumentationskonvention

Neue Dateien und Änderungen in VS Code sind für das Schulprojekt nachvollziehbar zu halten. Vor produktiven Änderungen Backup und Tests; danach Ergebnis, Datum und ggf. Commit dokumentieren. ZIP-Dateien dienen nur zum Transport; `.env`, Passwort, API-Schlüssel oder sensible Standorte dürfen nicht in GitHub bzw. MkDocs geraten.
