# Entwicklungsstand und Änderungsprotokoll

**Dokumentationsstand: 17. November 2026**

Dieser Verlauf enthält nur Tätigkeiten, die im Projektgespräch als umgesetzt und erfolgreich getestet bestätigt wurden. Der derzeitige Quellcode wurde für diese Dokumentationsaktualisierung nicht erneut live vom GitHub-Repository abgerufen. Technische Aussagen basieren auf den gemeinsam implementierten Schritten und den vom Team berichteten Testresultaten. Für eine neue Veröffentlichung sind aktuelle Commits und Tests gesondert nachzuweisen.

## 1. Zeitlicher Verlauf

| Zeitraum | Entwicklung | Verifizierter Stand |
|---|---|---|
| Oktober 2026 | IONOS-VPS mit Ubuntu 24.04 LTS, GNOME, Backup-Agent | Ubuntu-GUI und Agent eingerichtet |
| Oktober 2026 | PostgreSQL 16, pgAdmin 4, ursprüngliches Schema mit acht Tabellen | SQL-Schema, zwei fiktive Hilfestellen, zwei Kategorien |
| 20.10.2026 | FastAPI, Uvicorn, systemd `yana-api`, Nginx/HTTPS, Let's Encrypt | Öffentliche GET-API, Certbot-Erneuerungstest erfolgreich |
| Bis Ende Oktober / Anfang November | Flutter SDK, Dart, Android-Debug-Build; Models, Repositories, Controller | Drei Live-Verbindungstests und automatisierte Controller-Tests erfolgreich |
| November 2026 | Öffentliche HTML-/CSS-Website mit Jinja2 und FastAPI | Im Browser auf IONOS veröffentlicht und geprüft |
| November 2026 | Gemeinsame GitHub-Versionierung für `services/api` und lokale VPS-Arbeitskopie | Manuelles Deployment eingerichtet; `main.py`, `website.py`, Templates und Styles versioniert |
| November 2026 | Flutter Web – CORS für lokale Browserentwicklung | `CORSMiddleware` ergänzt und Backend neu gestartet; Browserproblem behoben gemeldet |
| November 2026 | Teamportal-Landing, Login-HTML und drei zusätzliche SQL-Tabellen | `portal_account`, `portal_session`, `portal_facility_audit` |
| November 2026 | Argon2-Authentifizierung, Sessions, CSRF, Logout | Echter Admin-Login, Dashboard und Logout erfolgreich getestet |
| November 2026 | Nginx-Login-Rate-Limit | Konfiguration/Reload erfolgreich; Website und API weiter HTTP 200 |
| November 2026 | Dashboard und geschützte Hilfestellenübersicht | TestClient-Tests und Browserprüfung erfolgreich |
| **17.11.2026** | Bearbeitung bestehender Hilfestellen | POST-Update, Audit-Eintrag, Wiederherstellung fiktiver Testdaten und produktiver Browser-Test erfolgreich |
| **17.11.2026 – Pause** | Dokumentation des aktuellen Stands | Nächstes Feature: **Neue Hilfestelle anlegen** |

## 2. Fachlicher Funktionsstatus

| Funktion | Status |
|---|---|
| Öffentliche YANA-Website | **Implementiert** |
| App-Downloadlink | Noch nicht veröffentlicht |
| Allgemeine GET-API | **Implementiert** (mit Testdaten) |
| Admin-Login, Logout, Session-Schutz, CSRF | **Implementiert, Basis- und Browser-Tests erfolgreich** |
| Hilfestellenliste für `admin`/`team` | **Implementiert** |
| Hilfestellen bearbeiten: Name, Telefon, E-Mail, Öffnungszeiten | **Implementiert** |
| Audit-Log der Änderungen | **Implementiert** |
| Neue Hilfestellen anlegen | **Noch nicht implementiert** |
| Hilfestellen löschen / deaktivieren / freigeben | Noch nicht implementiert |
| Externe Hilfestellenaccounts mit eigenen Datensätzen | Noch nicht implementiert |
| Vertrauliche Adressen in öffentlicher API schützen | Sicherheitsaufgabe **offen** |
| Flutter-UI vollständig verknüpft | Nicht abschließend bestätigt; Team arbeitet parallel daran |
| Verifizierte Notfallkontakte / anonyme Beratung | Noch nicht bereitgestellt |

## 3. Wesentliche Fehler und Korrekturen

| Problem | Korrektur |
|---|---|
| `git push` mehrfach `non-fast-forward` | `git pull --rebase origin main` bei sauberem Arbeitsstand, danach Push |
| Python-`__pycache__/*.pyc` im Git-Status | `.gitignore` ergänzen und getrackte Cache-Dateien entfernen |
| Flutter Web blockiert API mangels CORS | Korrekte lokale Origin-Regex in `CORSMiddleware`, Backend-Neustart |
| `EOFError` bei interaktivem Python-Heredoc | `login_test_local.py` als separate Datei ausführen |
| Beim Skript statt ID `TEST` eingegeben | Zuerst numerische `facility_id`, erst danach Bestätigung `TEST` |
| `TemplateNotFound: portal/hilfestelle_bearbeiten.html` | Richtigen Pluralnamen `hilfestellen_bearbeiten.html` konsistent einsetzen |
| Versehentlich `journalctl` ausgeführt | Nur Loglesebefehl, keine Veränderung des Systems |

Einzelheiten finden sich unter [Portal-Fehlerprotokoll](teamportal-troubleshooting.md) und [Flutter-Fehlerprotokoll](flutter-troubleshooting.md).

## 4. Nächster Entwicklungsschritt

**Bei der nächsten Sitzung direkt bei „Neue Hilfestelle anlegen“ fortfahren.** Vor der Implementierung prüfen: Pflichtfelder von `hilfestelle`, Stand der Identity-Sequenz, Behandlung öffentlicher Standortdaten, sichere `INSERT`-Transaktion, Berechtigungen, CSRF, Audit der Erstellung und Tests mit fiktiven Daten. Den genauen Projekt-Checkpoint enthält [Wiedereinstieg](weiterarbeit.md).

## 5. Nachweise für künftige Änderungen

Nach jedem größeren Feature ergänzen: Datum, betroffene Dateien, Git-Commit-ID, geänderte Datenbankstruktur, Testfälle mit Ergebnissen, Produktions-Deployment und offene Sicherheitsrisiken. Ein erfolgreicher manueller Browser-Test ist keine vollständige Sicherheitsprüfung.
