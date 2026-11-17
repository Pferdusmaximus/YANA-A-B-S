# Teamportal: Tests und bestätigte Ergebnisse

**Dokumentationsstand: 17.11.2026**

Die Dokumentation trennt **Syntax-/Importtests**, **HTTP-Tests mit `TestClient`**, **echte Schreibtests mit gemeinsamer PostgreSQL-Datenbank** und **Browser-Smoke-Tests auf dem VPS**. Ein grüner Syntaxcheck ist keine Sicherheitsprüfung.

## 1. Testumgebung

| Umgebung | Pfad auf dem IONOS-VPS | Zweck |
|---|---|---|
| Produktiver Code | `~/yana-backend/` | Vom systemd-Dienst `yana-api` genutzt |
| GitHub-Arbeitskopie | `~/yana-deploy-source/` | Quelle für neue Versionen |
| Testkopie | `~/yana-portal-test/` | Unabhängiger Python-Code ohne produktiven Dienstneustart |
| PostgreSQL | `app_db` | **Von Test- und Produktivcode gemeinsam genutzt** |

Die Testkopie verweist für die Konfiguration auf die produktive `.env`. Dadurch sind Authentifizierung und Datenbankzugang realitätsnah, aber **nicht vollständig isoliert**. Der Testbetrieb darf daher keine echten sensiblen Datensätze verändern. Ziel für die Zukunft ist eine separate Test-DB.

## 2. Syntax und Imports

Auf dem VPS:

```bash
cd ~/yana-portal-test
source ~/yana-backend/.venv/bin/activate
python -m py_compile main.py website.py portal.py portal_facilities.py database.py
python -c "from main import app; print('FastAPI-Import erfolgreich')"
```

Bei einem frühen Test wurde ausdrücklich bestätigt, dass `database.py` die Funktion `get_connection()` bereitstellt; andernfalls hätte der neue Login-Code nicht importiert werden können. Für die Tests wurden `httpx` und die weiteren [Login-Abhängigkeiten](teamportal-login.md) eingerichtet.

## 3. TestClient-Prüfung: öffentliche und geschützte Seiten

```python
from fastapi.testclient import TestClient
from main import app

with TestClient(app, base_url="https://testserver", follow_redirects=False) as client:
    for path, expected in {
        "/": 200,
        "/health": 200,
        "/hilfestellen": 200,
        "/kategorien": 200,
        "/notfallnummern": 200,
        "/portal/login": 200,
        "/portal/dashboard": 303,
        "/portal/hilfestellen": 303,
    }.items():
        response = client.get(path)
        assert response.status_code == expected, (path, response.status_code)
```

Die erwarteten HTTP-Statuscodes wurden im Verlauf bestätigt. Die Statuscodes `303` bedeuten hier **gewollte Weiterleitung zum Login**, nicht Funktionsfehler. Für den TestClient mit `Secure`-Cookie wird `https://testserver` verwendet.

## 4. Authentifizierung und CSRF

Für den ersten echten Admin-Login wurde `login_test_local.py` unter `~/yana-portal-test/` angelegt. Es liest die E-Mail per `input()` und das Passwort per `getpass()` ein, extrahiert den CSRF-Wert aus dem Login-HTML und führt Login → Dashboard → Logout → erneut Dashboard aus. Keine Passwörter werden im Code gespeichert.

| Test | Beobachtetes Ergebnis |
|---|---|
| Login-Seite | 200 |
| Gültiger Admin-Login | 303 |
| Dashboard mit Session | 200 |
| Logout | 303 |
| Dashboard nach Logout | 303 |
| Dashboard ohne Login | 303 |
| Gefälschtes Login-CSRF | 403 |
| Gefälschtes Logout-CSRF | 403 |
| Bestehende `/hilfestellen`-API | 200 |

Ein zusätzlicher Aufruf von `curl` mit `Origin: http://localhost:54321` wurde für die CORS-Konfiguration der Flutter-Web-Entwicklung vorgesehen. Der Server wurde mit CORS neu gestartet und die Browser-Nutzung als behoben gemeldet; aktuelle Browser-Regressionschecks sind bei späteren Änderungen erneut nötig.

## 5. Hilfestellenübersicht

Das Skript `facility_test_local.py` kontrollierte ohne Login (303), mit Admin (200), Tabellenzeilen gegen `SELECT COUNT(*) FROM hilfestelle` und die weiterhin erfolgreiche öffentliche `/hilfestellen`-API. Bei der damaligen Testdatenbasis waren es zwei Einrichtungen; die Liste ist inzwischen auf 100 Zeilen begrenzt, deshalb berücksichtigt der Test `min(count, 100)`.

## 6. Bearbeiten, Datenbank und Audit

Das lokale Skript `facility_edit_test_local.py` wurde als Datei angelegt und über `python facility_edit_test_local.py` gestartet. Beim Test wurde eine **ausdrücklich fiktive** Einrichtung ausgewählt, temporär eine Test-Telefonnummer gespeichert, die Datenbank erneut gelesen, der Audit-Eintrag überprüft und die ursprüngliche Telefonnummer wiederhergestellt.

| Prüfschritt | Erwartet und im Verlauf als erfolgreich bestätigt |
|---|---|
| Kein Login | HTTP 303 |
| Admin-Login | HTTP 303 |
| Bearbeitungsformular | HTTP 200 |
| Falsches CSRF | HTTP 403 |
| Ungültiger Name | HTTP 422 |
| Gültiger Speichervorgang | HTTP 303 |
| Datenbankprüfung | Testnummer vorhanden |
| Audit-Prüfung | Protokolleintrag vorhanden |
| Rücksetzen | HTTP 303, alter Wert wieder vorhanden |
| Logout | HTTP 303 |

**Wichtig:** Eine Rücksetzung nach einem Test erzeugt üblicherweise einen **zweiten** Audit-Eintrag. Ein `try/finally` im Testskript reduziert das Risiko, garantiert aber bei Rechnerabsturz oder Abbruch **keine** Wiederherstellung. Bei Unklarheiten unmittelbar den Datensatz in pgAdmin kontrollieren.

**Prüfung in pgAdmin (ohne Audit-Inhalte auszugeben):**

```sql
SELECT facility_id, name, phone, email, opening_hours
FROM public.hilfestelle
WHERE facility_id = 1;

SELECT audit_id, facility_id, account_id, changed_at
FROM public.portal_facility_audit
ORDER BY changed_at DESC LIMIT 10;
```

## 7. Produktive Browserprüfung

Nach jedem erfolgreichen Test wurden die betroffenen Dateien mit Backup in `~/yana-backend/` übernommen, per `python -m py_compile`/Import/HTTP geprüft und `sudo systemctl restart yana-api` ausgeführt. Die Anmeldung, Hilfestellenübersicht und **das Bearbeiten/Speichern samt Rücksetzung** wurden anschließend auch im Browser bestätigt.

## 8. Verbleibende Testlücken

- Separate Testdatenbank; automatisierte DB-Rollbacks und isolierte Integrationstests.
- Negativtests für fremde `facility`-Accounts, inaktive Accounts, abgelaufene Sessions und alle Rollen nach jeder neuen Route.
- Automatisierter Test für Nginx-429-Rate-Limit; Cookie-/CSRF-Prüfung im echten Browser.
- Fuzz-/Sicherheitstests, HTML-Formularvalidierung, Parallelbearbeitung und Fehlerfälle bei DB-Ausfall.
- GitHub Actions/CI für Backend und Flutter; Versions-/Migrationsprüfung.
- Fachlich verifizierte Testdaten und Datenschutz-/Lasttests vor echtem Einsatz.

Zum Nacharbeiten von Fehlern siehe [Portal-Fehlerprotokoll](teamportal-troubleshooting.md).
