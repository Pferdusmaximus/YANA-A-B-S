# Teamportal verwenden: Hilfestellen ansehen und bearbeiten

**Gültig für den bestätigten Stand vom 17.11.2026.** Das Portal ist bislang für das YANA-Team gedacht; der Login für externe Hilfestellen/Kanzleien und das Anlegen neuer Einrichtungen sind noch nicht fertig.

## Zugang zum Teamportal

1. Die öffentliche YANA-Website über den eingerichteten HTTPS-Zugang öffnen.
2. Die URL `https://SERVER_IP/portal/login` aufrufen (`SERVER_IP` durch die tatsächliche Serveradresse ersetzen).
3. Mit dem vom YANA-Team vergebenen Portal-Account anmelden. Es gibt keine öffentliche Registrierung.
4. Nach erfolgreichem Login erscheint das Dashboard.

E-Mail und Passwort werden serverseitig geprüft. Bei falscher Anmeldung erscheint eine allgemeine Fehlermeldung; nach mehreren Fehlversuchen kann ein Account vorübergehend gesperrt werden. Passwörter niemals per Chat oder als Screenshot weitergeben.

## Hilfestellenübersicht öffnen

Im Dashboard die Kachel **Hilfestellen** wählen und auf **Hilfestellen anzeigen** klicken. Die Tabelle unter `/portal/hilfestellen` enthält aktuell z. B. ID, Name, Typ, Kategorie, Adresse und Telefon. Sie zeigt derzeit nur die ersten 100 alphabetisch sortierten Datensätze; eine Such-/Filter-/Paginierungsfunktion ist noch nicht umgesetzt.

**Berechtigung:** `admin` und `team` dürfen die Übersicht nutzen. Eine Rolle `facility` darf momentan **nicht** pauschal alle Einträge sehen oder ändern.

## Vorhandene Hilfestelle bearbeiten

1. In der betreffenden Zeile **Bearbeiten** anklicken.
2. Die vier freigegebenen Felder prüfen: **Name, Telefonnummer, E-Mail, Öffnungszeiten**.
3. Änderungen eingeben und **Änderungen speichern** wählen.
4. Die Seite wird neu geladen und zeigt die Erfolgsmeldung, wenn der Vorgang erfolgreich war.
5. Die angezeigten Werte überprüfen; bei Bedarf die JSON-API oder pgAdmin zur technischen Verifikation verwenden.

**Nicht** über das aktuelle Formular bearbeitbar: Standortadresse, Koordinaten, Kapazität, Typ, Kategorie, Leistungen. Andere Verwaltungsaktionen wie „Neue Hilfestelle“, „Löschen“ oder „Freigeben“ existieren noch nicht.

## Nachvollziehbarkeit

Änderungen werden zusammen mit Account-ID und Zeitpunkt in `portal_facility_audit` dokumentiert. Gespeichert werden die Werte **vor** und **nach** der Änderung. Die Audit-Tabelle ist derzeit nur über autorisierte Datenbankadministration einsehbar; im Portal gibt es noch keine Protokollansicht.

## Abmelden

Im Dashboard auf **Abmelden** klicken. Die aktive Session wird gelöscht. Danach darf der geschützte Bereich nicht ohne erneute Anmeldung geöffnet werden. Bei einem gemeinsam genutzten Computer zusätzlich das Browserfenster schließen.

## Sicherheitshinweise

- Das Portal ist ein Entwicklungs-/Teamwerkzeug, kein offizieller Kontakt- oder Notfalldienst.
- Die bisherigen Standorte sind fiktive Testdatensätze.
- Keine echten Schutzunterkunft-Adressen oder persönlichen Beratungsdaten eintragen, solange öffentliche Sichtbarkeit, Rollen und Datenschutz nicht abgesichert sind.
- Das Speichern kann im aktuellen Stand Daten unmittelbar in der öffentlich abrufbaren Flutter-API verändern.

Technische Details: [Hilfestellenbearbeitung](../technik/teamportal-hilfestellen.md), [Login und Sessions](../technik/teamportal-login.md).
