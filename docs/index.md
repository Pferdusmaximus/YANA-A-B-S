# YANA – You Are Not Alone

**Hilfe finden. Informationen erhalten. In schwierigen Situationen schneller handeln.**

YANA ist ein Schul- und Entwicklungsprojekt für eine mobile Anwendung, die betroffenen Frauen den Zugang zu Notfallkontakten, Hilfestellen und Informationen zur Gewaltprävention erleichtern soll. Neben der Flutter-App gibt es eine öffentliche Informationswebsite und **ein gemeinsames, geschütztes Verwaltungsportal** für das YANA-Team und externe Partnerorganisationen. Die technische Grundlage bilden Flutter/Dart, FastAPI, PostgreSQL und Nginx auf einem IONOS-VPS.

**Dokumentationsstand: 24. November 2026.** Öffentliche Website und Verwaltungsportal laufen auf dem IONOS-VPS im neuen weiß-lila Design. Rollen, Partner-/Accountverwaltung, Freigabe- und Änderungsabläufe sowie die **zweistufige öffentliche Standortfreigabe** wurden für fiktive Daten erfolgreich getestet und im Browser produktiv kontrolliert. **Neu:** Die automatisierte Adresseingabe über Geoapify (Straße, Hausnummer, PLZ und Ort) hat einschließlich echter API-Abfrage, signiertem Bestätigungscode und Speichertests alle Prüfungen in `~/yana-portal-test` bestanden. **Ihr produktives Deployment ist am aktuellen Pause-/Übergabepunkt noch nicht bestätigt.**

> **Entwicklungs- und Sicherheitshinweis:** YANA ist weiterhin ein Schulprototyp, kein regulärer Notfall- oder Beratungsdienst. `GET /hilfestellen` liefert bei veröffentlichten Einträgen **Adresse und Koordinaten nur nach zusätzlicher Einzel- und Typfreigabe**; andernfalls `null`. Andere Kontaktdaten können weiterhin schutzwürdig sein. Bis zur fachlichen Datenschutzprüfung nur fiktive **„YANA Test“**-Daten verwenden. Im Notfall offizielle Notrufstellen kontaktieren.

## Portal und zentrale Neuerungen

- [Verwaltungsportal benutzen](nutzung/teamportal.md) – gemeinsamer Login und unterschiedliche Funktionen für `admin` und `partner`.
- [Portalarchitektur und Rollenmodell](technik/teamportal-architektur.md) – ein Portal, Berechtigung pro Einrichtung, Module und Datenfluss.
- [Partner- und Benutzerverwaltung](technik/teamportal-benutzerverwaltung.md) – Partner erstellen, Hilfestellen zuweisen, Accounts deaktivieren/reaktivieren und Startpasswort zurücksetzen.
- [Bedienung der Partnerverwaltung](nutzung/partnerverwaltung.md) – Schritt-für-Schritt-Anleitung für Administratoren und Partner.
- [Hilfestellenverwaltung](technik/teamportal-hilfestellen.md) – erfassen, Entwürfe bearbeiten, einreichen und veröffentlichen.
- [Standortdatenschutz](technik/standort-datenschutz.md) und [Standortfreigaben bedienen](nutzung/standortfreigaben.md) – zweistufige Freigabe von Adresse und Koordinaten.
- [Adresseingabe mit Geoapify](technik/geocoding.md) – implementiert und in Testumgebung erfolgreich geprüft; Produktivbereitstellung als nächster Schritt.
- [YANA-Designsystem](technik/designsystem.md) – einheitliches Weiß-Lila-Design für bestehende und neue Portalseiten.
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

| Bereich | Stand am 24.11.2026 |
|---|---|
| PostgreSQL / FastAPI / HTTPS | Auf dem IONOS-VPS eingerichtet; JSON-GET-Endpunkte erreichbar |
| Öffentliche Website | Produktiv im weiß-lila Redesign; Teamportal-Zugang oben rechts; App-Download weiterhin ausstehend |
| Portal-Authentifizierung | Administrator-/Partnerlogin, Session, Logout, CSRF und verpflichtender Passwortwechsel getestet |
| Partner- und Accountverwaltung | Admin erstellt Partner mit einmaligem Startpasswort; Zuweisen/Entfernen, Deaktivieren/Reaktivieren, Passwort-Reset im E2E-Test geprüft |
| Hilfestellen | Neue fiktive Einträge anlegen, Entwürfe bearbeiten, Status `draft` / `pending_review` / `published` verwalten |
| Zugriffsrechte | Admin sieht alle; Partner sieht nur über `portal_facility_assignment` zugewiesene Einträge |
| Änderungsfreigabe | Veröffentlichung bleibt bei Entwurf und Einreichung unverändert; Änderung erst nach Adminfreigabe |
| Standortdatenschutz | Produktiv: `published` + `is_location_public` + freigegebene Einrichtungsart; Admin-Tabelle unter `/portal/standorte`, Trigger zum Entzug bei Standortänderungen |
| Geoapify-Adresseingabe | Externe Geocoding-Anfrage, Validierung, signierter Beleg sowie Speicherung mit/ohne Koordinaten erfolgreich in Testumgebung geprüft; produktives Deployment noch offen |
| Audit | Datensatz- und Statusänderungen sowie Änderungsanträge protokolliert |
| Flutter | Modelle, Repositories, Controller und Entwicklungstests vorhanden; App-Oberfläche noch in Arbeit |
| Reale Beratung / verifizierte Einrichtungen | Noch nicht für den Realbetrieb freigegeben |

Das ursprüngliche ER-Diagramm bildet acht Fach-/Chat-Tabellen ab. Daneben existieren fünf Portal-Tabellen **sowie die neu eingerichtete Positivlisten-Tabelle `portal_public_location_type`**. Die [Schemaübersicht](technik/datenmodell.md) dokumentiert die Erweiterungen gesondert. Zum nächsten Termin direkt mit [Wiedereinstieg](technik/weiterarbeit.md) fortfahren.
