# Technische Dokumentation

Diese Seiten dokumentieren die Systemarchitektur sowie die bestätigten Implementierungen des YANA-Projekts. **Stand: 27. Oktober 2026.** Inhalte mit dem Kennzeichen *geplant* oder *noch offen* dürfen nicht als implementierte Funktionen verstanden werden.

## System und Backend

- [Systemarchitektur](architektur.md) – Flutter, FastAPI, Nginx, PostgreSQL und Betriebsdienste.
- [REST-API-Referenz](api-referenz.md) – `/hilfestellen`, `/kategorien`, `/notfallnummern` und Diagnose-Endpunkte.
- [Relationales Datenmodell](datenmodell.md) – ER-Modell, SQL-Schema und fiktive Testdaten.
- [Betrieb, Backups und Sicherheit](betrieb-sicherheit.md) – Vertrauensgrenzen, Secrets und offene Schutzmaßnahmen.
- [Technische Entscheidungen](entscheidungen.md) – Begründete Stack- und Betriebsentscheidungen.

## Flutter / Dart

- [Flutter: Drei-Schichtenmodell](flutter-architektur.md) – Präsentation, Controller und Datenzugriff.
- [Flutter: API-Anbindung](flutter-api-anbindung.md) – HTTP-Client, Model-Parsing und drei Repositories.
- [Flutter: Controller](flutter-controller.md) – `ChangeNotifier` und UI-Zustände.
- [Flutter: Tests](flutter-tests.md) – Erfolgreiche Live- und Unit-Tests, verbleibende Testlücken.
- [Flutter: Fehlerbehebung](flutter-troubleshooting.md) – OneDrive, Android SDK, Dart-Typen, HTTP 400 und Lints.
- [Flutter: Teamübergabe](flutter-teamworkflow.md) – Git-Workflow und Schnittstellen für die UI.

## Projektnachvollziehbarkeit

- [Entwicklungsstand und Änderungsprotokoll](entwicklungsstand.md) – Meilensteine und offene Punkte.
- [Server-Fehlerbehebung](troubleshooting.md) – Tatsächlich aufgetretene Infrastrukturprobleme.
- [Quellen und offizielle Referenzen](quellen.md) – Weiterführende Dokumentation.

Für die lokale Einrichtung siehe [Installation & Quick Start](../installation/index.md). Für Endanwender gilt der aktuelle Status im [Nutzungshandbuch](../nutzung/index.md).
