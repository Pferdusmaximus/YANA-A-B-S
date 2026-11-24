# Verwaltungsportal: Tests und bestätigte Ergebnisse

**Stand: 24. November 2026 · Standortschutz und Geoapify-Integration getestet**

## 1. Testumgebung und wichtige Einschränkung

| Ort | Pfad / System | Aufgabe |
|---|---|---|
| Quellcode | Windows / VS Code / `YANA-A-B-S/services/api` | Entwicklung |
| GitHub-Arbeitskopie | `~/yana-deploy-source` | Bereitstellung |
| Testkopie | `~/yana-portal-test` | Lokaler `TestClient` ohne Dienst-Neustart |
| Produktivcode | `~/yana-backend` | Systemd-Dienst `yana-api` |
| Datenbank | PostgreSQL `app_db` | **Gemeinsam von Test- und Produktivcode benutzt** |

**Kritisch:** Ein TestClient-Schreibtest in `~/yana-portal-test` ändert dieselbe Datenbank, aus der die öffentliche API liest. Daher ausschließlich eindeutig markierte fiktive Testeinträge verwenden, Ausgangswerte notieren, Audit und API kontrollieren und Testwerte wiederherstellen. Perspektivisch eigene Testdatenbank einrichten.

## 2. Syntax und Import

```bash
cd ~/yana-portal-test
source ~/yana-backend/.venv/bin/activate
python -m py_compile main.py portal.py portal_access.py \
  portal_facilities.py portal_facilities_create.py \
  portal_facilities_status.py portal_facility_changes.py \
  portal_partners.py portal_password.py portal_locations.py \
  geocoding_service.py
python -c "from main import app; print('FastAPI-Import erfolgreich')"
```

Das prüft nur Syntax und Importierbarkeit, **keine** vollständige Funktion oder Berechtigung.

## 3. Rückblick auf bestätigte Tests

| Arbeitspaket | Nachweis / Ergebnis im Projektverlauf |
|---|---|
| Login / Logout / CSRF | Admin-Login, geschützte Seiten, Sitzung, Logout und fehlerhafter Token geprüft |
| Hilfestelle bearbeiten | `FOR UPDATE`, SQL-Update, Audit-Eintrag, Wiederherstellung von Testwerten |
| Hilfestelle neu anlegen | Zehn Formular-/Sicherheitstests; anschließender Speichertest mit ID, Audit und API erfolgreich |
| Veröffentlichungsfilter | Nur `published`-IDs in `GET /hilfestellen` gegenüber DB abgeglichen |
| Statusfreigabe | `submit`, `approve`, `reject`, `unpublish`, unzulässige Übergänge, Audit und API-Verhalten getestet |
| Partnerrechte | Simulierte Negativtests für fremde Hilfestellen; anschließend Test-Partneraccount mit eigener Zuordnung und Browserlogin |
| Änderungsvorschläge | Schreibfreie Endpunkttests und End-to-End-Test: Entwurf, Einreichung, Freigabe, Originalwert wiederhergestellt, Audit-Ereignisse |
| Produktiv-Deployment | Website und Portal nach jeweils relevanten Deployments im Browser geprüft |

Die Tests belegen den Entwicklungsstand **mit fiktiven Datensätzen**, ersetzen aber weder isolierte CI-Tests noch einen unabhängigen Sicherheitstest.

## 4. Relevante HTTP-Negativtests

| Fall | Erwartung |
|---|---|
| Geschütztes Portal ohne Anmeldung | Login-Redirect bei GET oder HTTP 401 je nach Route |
| Ungültiger CSRF-Wert bei POST | HTTP 403 |
| Partner öffnet fremde Hilfestelle direkt | HTTP 404 |
| Partner versucht Freigabe / Admin-Prüfseite | HTTP 403 |
| Partner versucht selbst neue Hilfestelle anzulegen | HTTP 403 |
| Entwurf direkt ohne Einreichung freigeben | HTTP 409 |
| Veröffentlichten Datensatz direkt über `/edit` ändern | HTTP 409 |
| Änderungsantrag mit inzwischen veralteter öffentlicher Basis | HTTP 409 bei Freigabe |
| Ungültige Eingabe im Erstellungs-/Änderungsformular | HTTP 422 |

## 5. Ende-zu-Ende-Test der Änderungsfreigabe

Der zuletzt ausgeführte `change_requests_e2e_test.py` testete den fiktiven Partner mit einer zugewiesenen, veröffentlichten Test-Hilfestelle. Das gemeldete erfolgreiche Ergebnis umfasst:

1. Partner und Administrator anmelden sowie Rechte prüfen.
2. Neue Telefonnummer als Entwurf speichern; öffentliche API zeigt weiter die ursprüngliche Nummer.
3. Zur Prüfung einreichen; die öffentliche API bleibt unverändert.
4. Als Administrator freigeben; erst jetzt wird die neue Nummer über `/hilfestellen` ausgegeben.
5. Ursprüngliche Telefonnummer durch einen weiteren genehmigten Änderungsvorschlag wiederherstellen.
6. Erwartete Audit-Ereignisse prüfen.

Das Skript ist ein **Schreibtest**, darf nicht blind gegen reale Einrichtungen laufen und wird nicht im produktiven Backend benötigt. Die Testskripte können als methodische Nachweise unter `services/api/tests/` im Repository liegen; Installationshilfen und ZIP-Transportpakete sind keine notwendigen Laufzeitbestandteile.

## 6. Wiederholbare schreibfreie Probe

```python
from fastapi.testclient import TestClient
from main import app

with TestClient(app, base_url="https://testserver", follow_redirects=False) as client:
    for path in ("/", "/health", "/hilfestellen", "/portal/login"):
        assert client.get(path).status_code == 200
    assert client.get("/portal/hilfestellen").status_code == 303
    assert client.get("/portal/dashboard").status_code == 303
```

Für `Secure`-Sessions verwendet der `TestClient` die HTTPS-Basisadresse. Unter aktuellen FastAPI-Versionen kann eine reine Iteration über `app.routes` eingebundene Router übersehen; ein tatsächlicher HTTP-Test ist die zuverlässigere Prüfung.

## 7. Weitere Testziele

- Separate Testdatenbank und automatisierte Test-Isolation/Transaktions-Rollbacks.
- Weitere Parallelitäts-/Race-Condition-Tests bei mehreren zugeordneten Partnern.
- Tests für abgelaufene Sessions, deaktivierte Accounts, Rate-Limiting und manipulierbare Formularwerte.
- Datenschutz-/Freigabetests für sensible Standortfelder vor Realbetrieb.
- Reproduzierbare CI-Pipeline und versionierte DB-Migrationen.

## 8. Ergänzung: Partnerverwaltung und Account-Lebenszyklus (23.11.2026)

Die folgenden Testgruppen wurden im Projektverlauf als erfolgreich gemeldet. Die Python-Tests verwendeten `TestClient(app, base_url="https://testserver", follow_redirects=False)` sowie fiktive Accounts und markierte Test-Hilfestellen.

| Testgruppe | Ergebnis |
|---|---|
| Partner-/Admin-Zugriff | Sechs Rollen- und Login-Prüfungen bestanden; Partner erhält für Verwaltungsaktionen `403` |
| Zuweisung und Entzug | Testhilfestelle zugewiesen, Zugriff geprüft, Zuordnung entfernt und bereinigt |
| Neue Account-Erstellung | Schreibfreie Endpunkttests und **7 E2E-Prüfungen** bestanden: erzeugter Account, Hash, Pflichtwechsel, erneuter Login, Adminsperre |
| Deaktivieren / Reaktivieren / Reset | **6 schreibfreie Prüfungen**, danach **12 Integrationstests** bestanden |
| Session-Invalidierung | Nach Deaktivieren und Reset alte Sitzung ungültig; nach Passwortwechsel erneuter Login erforderlich |
| Produktivprüfung | Nach Nutzerangabe nach erfolgreichem Deployment und Browserkontrolle funktionsfähig |

Die interaktiven Testskripte mit `input()`/`getpass()` müssen **als `.py`-Datei** gestartet werden, nicht per `python - <<'PY'`, da sonst `EOFError` auftreten kann. Temporäre Skripte wie `partner_create_e2e_local.py` und `partner_lifecycle_test_local.py` gehören nicht zum erforderlichen Produktivcode.

**Datenbankgrenze:** Test- und Produktivverzeichnis greifen auf dieselbe `app_db` zu. Vor einem erneuten Schreibtest sicherstellen, dass der eindeutig markierte Testaccount noch nicht existiert. Nach dem Test Accounts und ihre Sessions/Zuordnungen kontrolliert bereinigen. Die automatisierten Testfälle ersetzen keinen unabhängigen Sicherheitstest, keine Konkurrenzlastprüfung und keine isolierte Staging-Umgebung.

Details: [Partner- und Benutzerverwaltung](teamportal-benutzerverwaltung.md).

## 9. Ergänzung 24.11.2026: Standortschutz und Administratorseite

| Prüfung | Ergebnis laut durchgeführtem Projektverlauf |
|---|---|
| `GET /hilfestellen` gegen DB-Status und Freigaben | Bestanden: nur veröffentlichte Hilfestellen; nicht freigegebene Adresse/Koordinaten `null` |
| Einrichtungsarten-Positivliste | Bestanden: nur `Beratungsstelle`; Schutzunterkunft ausgeschlossen |
| Anonyme Freigabe / Partnerrecht | Nicht angemeldete POSTs gesperrt; Administratorberechtigung erforderlich |
| Schutzunterkunft per direktem Admin-POST freigeben | HTTP 409, keine Änderung |
| Standortdaten ändern | PostgreSQL-Trigger hat die Standortfreigabe zurückgesetzt; `ROLLBACK` |
| Fiktive öffentliche Beratungsstelle freigeben/sperren | Freigabe in DB und API sichtbar, Sperre danach wieder `null`; `ROLLBACK` |
| Produktiver Browser | Standortfreigabeseite als funktionsfähig bestätigt |

## 10. Ergänzung 24.11.2026: Geoapify-Testabdeckung

**Wichtig: Die folgenden Tests wurden in `~/yana-portal-test` durchgeführt. Die neue Adresseingabe wurde bei diesem Dokumentations-Checkpoint noch nicht als produktiv bereitgestellt bestätigt.**

| Testgruppe | Ergebnis |
|---|---|
| `.env` und API-Schlüssel | Mit explizitem Dateipfad geladen; Schlüssel nicht ausgegeben |
| Externer Geoapify-Aufruf | Öffentlich bekannte Testadresse in Regensburg erfolgreich auf Koordinaten aufgelöst |
| FastAPI-Endpunkt | Admin-Login, Adresseingabefelder, JavaScript, Zustimmung, Geheimtyp-Sperre, Bestätigungscode und öffentliche API erfolgreich |
| Entwurf mit Koordinaten | Bestätigter Standort gespeichert; `draft`, `is_location_public=FALSE`, Audit geprüft |
| Entwurf ohne Koordinaten | Mit beiden Koordinaten `NULL` gespeichert, ohne Veröffentlichung |
| Manipulationsschutz | Geänderte Hausnummer mit altem Bestätigungscode: HTTP `422` |
| Testdatenisolation im Einzeltest | Offene Testtransaktion, `ROLLBACK`, Datensätze für andere DB-Verbindungen nicht sichtbar |

Die Speichertests wurden vom Projektverantwortlichen als **vollständig erfolgreich** bestätigt. Nach dem `ROLLBACK` bleiben keine neuen Test-Hilfestellen dauerhaft bestehen; Sequenzen können dennoch höhere ID-Werte haben. Die gemeinsame Test-/Produktivdatenbank bleibt ein Grund, die Tests künftig auf eine isolierte DB zu verlagern.

**Ausstehend:** Produktive Geoapify-Konfiguration und Browserprüfung, Flutter-Verhalten bei `null`-Koordinaten sowie vollständige End-to-End-Regressionstests aller Website-/Portalabläufe.
