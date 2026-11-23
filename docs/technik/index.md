# Technische Dokumentation

Diese Seiten dokumentieren den **nachgewiesenen Stand vom 23. November 2026**. Vorhandene Dokumente zur Servereinrichtung und Flutter-Schicht wurden erhalten; die Website, das Teamportal und die Datenpflege sind hinzugekommen. *Geplant* bedeutet ausdrücklich **nicht implementiert**.

## System, Server und Datenbank

- [Systemarchitektur](architektur.md) – öffentliche Website, Browserportal, Flutter, FastAPI, Nginx und PostgreSQL.
- [REST-API und Portal-Routen](api-referenz.md) – öffentliche JSON- und geschützte HTML-Endpunkte.
- [Relationales Datenmodell](datenmodell.md) – ursprüngliches ER-Modell mit acht Tabellen.
- [Zusätzliche Portal-Datenbanktabellen](teamportal-datenbank.md) – Accounts, Sessions, Audit, Partnerzuordnung und Änderungsanträge.
- [Betrieb, Backups und Sicherheit](betrieb-sicherheit.md) – Ist-Stand, Risiken und offene Schutzmaßnahmen.
- [Technische Entscheidungen](entscheidungen.md) – Begründung für die Architektur.

## Website, Teamportal und Datenpflege

- [Öffentliche Website](website.md) – Inhalte, Templates und bisherige Bereitstellung.
- [Teamportal-Architektur und Rollen](teamportal-architektur.md) – Struktur, URLs und Verantwortlichkeiten.
- [Login, Sessions und CSRF](teamportal-login.md) – PostgreSQL-Authentifizierung, Cookie-Sicherheit und Pflicht-Passwortwechsel.
- [Partner- und Benutzerverwaltung](teamportal-benutzerverwaltung.md) – Admin erstellt und verwaltet Partner inklusive Startpasswort, Zuordnungen und Account-Lebenszyklus.
- [Hilfestellenverwaltung](teamportal-hilfestellen.md) – Neuaufnahme, Entwürfe und Veröffentlichung.
- [Änderungsvorschläge und Freigabe](teamportal-aenderungsfreigabe.md) – Änderungen an bereits veröffentlichten Einträgen und Adminprüfung.
- [Portal-Tests](teamportal-tests.md) – tatsächliche HTTP-Statuscodes und Speichertest.
- [Portal-Fehlerbehebung](teamportal-troubleshooting.md) – beobachtete Probleme und Korrekturen.
- [GitHub und Deployment](git-deployment.md) – Entwicklung/Server-Dateikopien, Git-Konflikte und `.gitignore`.
- [Produktive Bereitstellung](teamportal-deployment.md) – Backup, Testumgebung, Neustart und Rollback.
- [Wiedereinstieg und nächste Aufgaben](weiterarbeit.md) – **Datenschutz, isolierte Testdatenbank und Qualitätsverbesserungen**.

## Flutter / Dart

- [Drei-Schichtenmodell](flutter-architektur.md) – Model, Repository, Controller und Präsentation.
- [Flutter: API-Anbindung](flutter-api-anbindung.md) – HTTP-Client, Models und Repositories.
- [Flutter: Controller](flutter-controller.md) – `ChangeNotifier` und UI-Zustände.
- [Flutter: Tests](flutter-tests.md) – Live- und Unit-Tests.
- [Flutter: Fehlerbehebung](flutter-troubleshooting.md) – Android SDK, OneDrive, Dart-Typen, HTTP 400 und CORS.
- [Flutter: Teamübergabe](flutter-teamworkflow.md) – Zusammenarbeit bei der UI.

## Verlauf und Grundlagen

- [Entwicklungsstand und Änderungsprotokoll](entwicklungsstand.md) – Meilensteine bis 23.11.2026.
- [Server-Fehlerbehebung](troubleshooting.md) – Infrastruktur- und Betriebsprobleme.
- [Quellen](quellen.md) – Offizielle technische Referenzen.

Für eine Reproduktion mit Testdaten siehe [Installation und Quick Start](../installation/index.md). Für die Portalbedienung siehe [Benutzung des Teamportals](../nutzung/teamportal.md).
