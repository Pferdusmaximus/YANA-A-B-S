# YANA – You Are Not Alone

**Hilfe finden. Informationen erhalten. In schwierigen Situationen schneller handeln.**

YANA ist ein Schul-/Entwicklungsprojekt für eine mobile Anwendung, die betroffenen Frauen den Zugang zu Notfallkontakten, Hilfestellen und Informationen zu Gewaltprävention erleichtern soll. Ergänzend zur Flutter-App existiert inzwischen eine **öffentliche Informationswebsite** und ein **geschütztes Webportal** für die Pflege der Hilfestellendaten. Die technische Basis besteht aus Flutter/Dart, FastAPI, PostgreSQL und Nginx auf einem IONOS-VPS.

**Gesamtstand: 17. November 2026.** Die Website und das Teamportal laufen auf dem IONOS-VPS. Ein Administrator kann sich anmelden, Hilfestellen anzeigen und **bestehende** Einträge (Name, Telefon, E-Mail, Öffnungszeiten) bearbeiten. Das Speichern und die Audit-Protokollierung wurden im Test und anschließend im Browser erfolgreich geprüft. Die Funktion **„Neue Hilfestelle anlegen“ ist noch nicht implementiert**; hier setzen wir beim nächsten Mal fort.

> **Entwicklungs- und Sicherheitshinweis:** Die bisherigen Hilfestellen sind fiktive Testdaten. YANA ist noch kein verlässlicher Notfall- oder Beratungsdienst. Keine geheimen Schutzunterkunft-Adressen eintragen, solange die öffentliche API sie ungefiltert ausgibt. In einer akuten Gefahrensituation offizielle Notrufstellen kontaktieren.

## Neu: Website und Teamportal

- [Öffentliche YANA-Website](technik/website.md) – Landingpage, App-Informationen und Download-Hinweis.
- [Teamportal: Architektur und Rollen](technik/teamportal-architektur.md) – Zugang, Dashboard und Verantwortlichkeiten.
- [Anmeldung und Sicherheit](technik/teamportal-login.md) – Argon2, Sessions, CSRF und Nginx-Loginbegrenzung.
- [Hilfestellen anzeigen und bearbeiten](technik/teamportal-hilfestellen.md) – Formular, SQL-Update und Audit.
- [Teamportal bedienen](nutzung/teamportal.md) – Benutzerablauf im Browser.
- [Wiedereinstieg: nächster Schritt](technik/weiterarbeit.md) – Fertiggestellte Funktionen und **„Neue Hilfestelle anlegen“**.

## Gesamtdokumentation

- [Installation und Quick Start](installation/index.md) – Server, Backend, Webportal und Flutter-Umgebung.
- [Technische Dokumentation](technik/index.md) – Architektur, API, Datenbank, Sicherheit und Tests.
- [Systemarchitektur](technik/architektur.md) – Flutter + Website/Portal + FastAPI + Nginx + PostgreSQL.
- [REST-API-Referenz](technik/api-referenz.md) – Öffentliche und geschützte Routen.
- [Flutter: API-Anbindung](technik/flutter-api-anbindung.md) und [Tests](technik/flutter-tests.md).
- [GitHub- und Deployment-Workflow](technik/git-deployment.md).
- [Entwicklungsprotokoll](technik/entwicklungsstand.md).

## Nachgewiesener technischer Stand

| Bereich | Status / Nachweis |
|---|---|
| PostgreSQL / FastAPI / HTTPS | Laufendes Backend; bestehende GET-API weiterhin erreichbar |
| Öffentliche Informationswebsite | Im Browser produktiv aufgerufen; App-Download noch ausstehend |
| Teamportal-Login | Admin-Login, Dashboard, Logout und CSRF-Grundtests bestanden |
| Hilfestellenverwaltung | Geschützte Übersicht, Bearbeitung, UPDATE und Audit; Test-/Browserprüfung bestanden |
| Datenbankteststand | Zwei fiktive Hilfestellen, zwei Kategorien; Notfallnummernliste leer |
| Flutter-Client | Models, Repositories und Controller für drei Bereiche; Dart-CLI- und Unit-Tests |
| Flutter-Web-Zugriff | CORS-Freigabe für lokale Entwicklung ergänzt |
| App-Screens / reale Hilfevermittlung | Entwicklung läuft, nicht als fertig nachgewiesen |

## Veröffentlichung und Medien

App-Download, Screenshots und Projektvideo werden ergänzt, sobald passende freigegebene Inhalte vorliegen. Ein tatsächlicher App-Download ist noch **nicht** bereitgestellt. Eine Teamportal-Anmeldung ersetzt keine öffentliche Registrierung oder Hilfevermittlung.
