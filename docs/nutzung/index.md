# Nutzungshandbuch – Entwicklungsstand

**Stand: 23. November 2026.** YANA besitzt inzwischen zwei klar getrennte Nutzungsebenen: die öffentliche Informationswebsite mit Download-Hinweis und ein geschütztes Teamportal für die interne Datenpflege. Die Flutter-App selbst befindet sich weiterhin in Entwicklung; eine veröffentlichte Download-Version oder verlässliche echte Notfallberatung ist nicht bestätigt.

## Öffentliche Website

Über die HTTPS-Startseite können Besucher Informationen zum YANA-Projekt und zu geplanten App-Funktionen lesen. Der Downloadbereich weist derzeit darauf hin, dass die App noch entwickelt wird. Es gibt keine öffentliche Registrierung für das Teamportal.

## Geschütztes Teamportal

Administratoren des YANA-Teams und zugeordnete externe Partner melden sich unter `/portal/login` an. Im selben Dashboard sehen Partner ausschließlich ihre Einrichtungen, Administratoren dagegen alle. Neue Test-Hilfestellen können erstellt, Entwürfe zur Veröffentlichung eingereicht und veröffentlichte Kontaktdaten über getrennte Änderungsvorschläge mit Administratorfreigabe aktualisiert werden. Zudem lassen sich Partner-Accounts direkt im Portal erstellen, Hilfestellen zuweisen, Accounts sperren/reaktivieren und Passwörter zurücksetzen. Hilfestellenaktionen werden in PostgreSQL protokolliert; eine umfassende Account-Auditansicht ist noch offen.

Die vollständigen Anleitungen stehen unter **[Teamportal bedienen](teamportal.md)** und **[Partner-Accounts verwalten](partnerverwaltung.md)**. Technische Details: [Hilfestellenverwaltung](../technik/teamportal-hilfestellen.md).

## Geplante mobile App-Funktionen

- Standortbezogene Hilfestellen und Kategorien anzeigen.
- Verifizierte Notfallkontakte schnell verfügbar machen.
- Präventionsinformationen und Wege zur Hilfe aufzeigen.
- Anonyme Erstberatung als späteres, besonders datenschutzsensibles Modul.

Die Netzwerk- und Logikschicht ist für drei Datenbereiche implementiert; der Abschluss der sichtbaren Flutter-Screens wird in dieser Dokumentation **nicht** behauptet.

## Hinweis zu echten Notfällen

Die bestehenden Hilfestellen, Telefonnummern und Standorte sind fiktive Entwicklungsdaten. YANA ersetzt aktuell **keinen** offiziellen Notruf und keine geprüfte Beratungsstelle. Für akute Hilfe sind die offiziellen zuständigen Dienste zu verwenden.
