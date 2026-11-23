# YANA – You Are Not Alone

**Hilfe finden. Informationen erhalten. In schwierigen Situationen schneller handeln.**

YANA ist ein Schul- und Entwicklungsprojekt für eine mobile Anwendung, die betroffenen Frauen den Zugang zu Notfallkontakten, Hilfestellen und Informationen zur Gewaltprävention erleichtern soll. Neben der Flutter-App gibt es eine öffentliche Informationswebsite und **ein gemeinsames, geschütztes Verwaltungsportal** für das YANA-Team und externe Partnerorganisationen. Die technische Grundlage bilden Flutter/Dart, FastAPI, PostgreSQL und Nginx auf einem IONOS-VPS.

**Dokumentationsstand: 23. November 2026.** Website, öffentliche GET-API und die nachfolgend beschriebenen Verwaltungsfunktionen sind auf dem VPS produktiv bereitgestellt bzw. im Projektverlauf getestet. Für fiktive Hilfestellen funktionieren Neuaufnahme, Veröffentlichungsstatus, rollenabhängiger Zugriff sowie Änderungsvorschläge mit Administratorfreigabe. Der Änderungsworkflow und die neue Partner-/Benutzerverwaltung wurden mit fiktiven Testaccounts auf Rollen, Datenbankänderungen und Passwortwechsel geprüft; anschließend wurden die Funktionen nach Projektverlauf produktiv bereitgestellt.

> **Entwicklungs- und Sicherheitshinweis:** YANA ist noch kein regulärer Notfall- oder Beratungsdienst. Verwendet werden fiktive **„YANA Test“**-Einträge. Auch veröffentlichte Einträge werden über `/hilfestellen` einschließlich Adresse und Koordinaten öffentlich ausgegeben. Keine vertraulichen Schutzunterkunft-Adressen oder realen personenbezogenen Hilfedaten hinterlegen. Im Notfall offizielle Notrufstellen kontaktieren.

## Portal und zentrale Neuerungen

- [Verwaltungsportal benutzen](nutzung/teamportal.md) – gemeinsamer Login und unterschiedliche Funktionen für `admin` und `partner`.
- [Portalarchitektur und Rollenmodell](technik/teamportal-architektur.md) – ein Portal, Berechtigung pro Einrichtung, Module und Datenfluss.
- [Partner- und Benutzerverwaltung](technik/teamportal-benutzerverwaltung.md) – Partner erstellen, Hilfestellen zuweisen, Accounts deaktivieren/reaktivieren und Startpasswort zurücksetzen.
- [Bedienung der Partnerverwaltung](nutzung/partnerverwaltung.md) – Schritt-für-Schritt-Anleitung für Administratoren und Partner.
- [Hilfestellenverwaltung](technik/teamportal-hilfestellen.md) – erfassen, Entwürfe bearbeiten, einreichen und veröffentlichen.
- [Änderungsvorschläge und Freigaben](technik/teamportal-aenderungsfreigabe.md) – veröffentlichte Daten bleiben bis zur Adminentscheidung bestehen.
- [Datenbank des Portals](technik/teamportal-datenbank.md) – Accounts, Sessions, Zuordnungen, Audit und Änderungsvorschläge.
- [Login und Sicherheit](technik/teamportal-login.md) – Argon2, Sitzungen, Rollen und CSRF.

## Gesamtdokumentation

- [Installation und Quick Start](installation/index.md) – Server, Backend, Datenbank, Website und Flutter.
- [Technische Dokumentation](technik/index.md) – Architektur, Schnittstellen, Tests, Sicherheit und Betrieb.
- [REST-API-Referenz](technik/api-referenz.md) – öffentliche Endpunkte und geschützte Browser-Routen.
- [Flutter-API-Anbindung](technik/flutter-api-anbindung.md) und [Flutter-Tests](technik/flutter-tests.md).
- [GitHub und Deployment](technik/git-deployment.md) – Entwicklung unter Windows, Testkopie und produktiver Dienst.
- [Entwicklungsstand](technik/entwicklungsstand.md) und [Weiterarbeit](technik/weiterarbeit.md).

## Nachgewiesener Stand

| Bereich | Stand am 23.11.2026 |
|---|---|
| PostgreSQL / FastAPI / HTTPS | Auf dem IONOS-VPS eingerichtet; JSON-GET-Endpunkte erreichbar |
| Öffentliche Website | Produktiv; App-Download weiterhin ausstehend |
| Portal-Authentifizierung | Administrator-/Partnerlogin, Session, Logout, CSRF und verpflichtender Passwortwechsel getestet |
| Partner- und Accountverwaltung | Admin erstellt Partner mit einmaligem Startpasswort; Zuweisen/Entfernen, Deaktivieren/Reaktivieren, Passwort-Reset im E2E-Test geprüft |
| Hilfestellen | Neue fiktive Einträge anlegen, Entwürfe bearbeiten, Status `draft` / `pending_review` / `published` verwalten |
| Zugriffsrechte | Admin sieht alle; Partner sieht nur über `portal_facility_assignment` zugewiesene Einträge |
| Änderungsfreigabe | Veröffentlichung bleibt bei Entwurf und Einreichung unverändert; Änderung erst nach Adminfreigabe |
| Audit | Datensatz- und Statusänderungen sowie Änderungsanträge protokolliert |
| Flutter | Modelle, Repositories, Controller und Entwicklungstests vorhanden; App-Oberfläche noch in Arbeit |
| Reale Beratung / verifizierte Einrichtungen | Noch nicht für den Realbetrieb freigegeben |

Das ursprüngliche ER-Diagramm bildet nur acht Fach-/Chat-Tabellen ab. In der laufenden Anwendung wurden fünf Portal-Tabellen ergänzt; die [Schemaübersicht](technik/datenmodell.md) dokumentiert diese Erweiterung gesondert.
