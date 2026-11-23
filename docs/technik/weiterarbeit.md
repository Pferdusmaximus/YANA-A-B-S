# Wiedereinstieg: aktueller Stand und nächste Aufgaben

**Projekt-Checkpoint: Montag, 23. November 2026.**

## 1. Was ist abgeschlossen?

- Öffentliche Website und JSON-GET-API laufen über HTTPS auf dem IONOS-VPS.
- Gemeinsames Portal für `admin` (YANA-Team) und `partner` (externe, zugeordnete Organisation).
- Admin kann fiktive neue Hilfestellen anlegen; automatisch `draft`, `created`-Audit und neue ID.
- Entwürfe lassen sich bearbeiten, einreichen, veröffentlichen, zurückweisen oder wieder zurücknehmen.
- Öffentliche API liefert ausschließlich `published`-Hilfestellen.
- Partner sehen nur die ihnen per `portal_facility_assignment` zugewiesenen Einträge; ein Testpartner ist vorhanden.
- **Änderungsvorschläge bei veröffentlichten Einträgen**: Partner speichert getrennte Werte, reicht ein; Administrator vergleicht und gibt frei oder lehnt ab. Die öffentliche API ändert sich **erst bei Freigabe**.
- Die Änderungsfreigabe wurde mit fiktiven Testdaten Ende-zu-Ende geprüft und anschließend produktiv bereitgestellt. Die ursprüngliche Telefonnummer wurde nach dem Test wiederhergestellt.
- **Partnerverwaltung:** Account-Erstellung mit einmaligem Startpasswort, Zuordnen/Entfernen von Hilfestellen, Pflicht-Passwortwechsel, Deaktivieren, Reaktivieren und Administrator-Reset umgesetzt und mit Testpartnern geprüft; nach Projektverlauf produktiv bereitgestellt.

## 2. Welches Feature kommt als Nächstes?

Die vereinfachte **Administrator-Benutzerverwaltung ist umgesetzt**: Partner werden im Portal erstellt, mit Einrichtungen verknüpft, deaktiviert/reaktiviert und bei Bedarf per neuem Startpasswort zurückgesetzt.

Als nächste Entwicklungsschritte sind sinnvoll:

1. **Datenschutz vor realem Einsatz:** Vertrauliche Adressen und Koordinaten aus der öffentlichen `/hilfestellen`-Antwort heraushalten; Sichtbarkeit je Einrichtung definieren.
2. **Isolierte Testdatenbank:** Schreibtests dürfen nicht mehr produktive `app_db` verändern.
3. **Automatisierte Regressionstests:** Login, CSRF, Zuordnungen, Sperrungen, Freigaben, Session-Entzug und konkurrierende Bearbeitungen.
4. **Account-Audit:** Änderungen an Partnerkonten und Zuordnungen gezielt protokollieren. Aktuell protokolliert `portal_facility_audit` primär Hilfestellenaktionen.
5. **Betriebsreife:** Echte Organisationen verifizieren, Startpasswörter sicher übermitteln, MFA und Backup-Wiederherstellung prüfen.

Derzeit wird im Portal als Partneridentifikation eine E-Mail-Adresse verwendet; ein separates Organisationsprofil mit eigenem Datensatz wurde nicht implementiert.

## 3. Entwicklungsorte und Deployment

| Zweck | Ort |
|---|---|
| Quellcode | Windows / VS Code / `YANA-A-B-S/services/api/` |
| Remote-Repository | GitHub |
| VPS-Git-Arbeitskopie | `~/yana-deploy-source/` |
| VPS-Testcode | `~/yana-portal-test/` |
| Produktivcode | `~/yana-backend/` |
| Systemdienst | `yana-api` |
| PostgreSQL | `app_db`, pgAdmin 4 |
| Loginseite | `https://SERVER_IP/portal/login` |

VPS-Verwaltung erfolgt über die grafische Ubuntu-/IONOS-Konsole. Der GitHub-Push allein aktualisiert nicht die produktive Anwendung.

## 4. Wichtige technische Dateien

| Datei | Aufgabe |
|---|---|
| `portal.py` | Anmeldung, Sessions, Dashboard |
| `portal_access.py` | Rollen-/Partnerberechtigungen |
| `portal_facilities.py` | Übersicht und Bearbeitung von Entwürfen |
| `portal_facilities_create.py` | Neue Test-Hilfestellen |
| `portal_facilities_status.py` | Statuswechsel für Neueinträge |
| `portal_facility_changes.py` | Änderungsentwürfe und Freigabe veröffentlichter Einträge |
| `portal_partners.py` | Account-Erstellung, Zuweisungen, Deaktivieren/Reaktivieren, Reset |
| `portal_password.py` | Eigenes Passwort ändern, Pflichtwechsel |
| `templates/portal/partner.html` | Partnerverwaltung mit Formularen und CSRF |
| `templates/portal/partner_erstellt.html` | Startpasswort einmalig anzeigen |
| `templates/portal/passwort_aendern.html` | Eigenes Passwort festlegen |
| `templates/portal/hilfestellen.html` | Gemeinsame rollenabhängige Übersicht |
| `templates/portal/aenderung_bearbeiten.html` | Änderungsformular |
| `templates/portal/aenderungen_pruefen.html` | Administrations-Warteschlange |
| `sql/01_change_requests.sql` | Dokumentierte Änderungsvorschlags-Migration |

Die ursprüngliche `hilfestellen_bearbeiten.html`-Datei benötigt weiterhin den **Plural** im Namen.

## 5. Sicherheits- und Qualitätsaufgaben

- **Vor realen Hilfestellen:** Adressen/Koordinaten und ggf. weitere sensible Felder aus der öffentlichen API für bestimmte Kategorien ausschließen; echte Veröffentlichungskriterien fachlich definieren. Der Filter `published` allein reicht dafür nicht.
- Testdaten-Zwang `YANA Test...` erst nach Datenschutz- und Validierungsprüfung bewusst aufheben.
- Separates Test-PostgreSQL einrichten: Der aktuelle Testcode verwendet produktive `app_db`.
- Automatisierte CI-, Rollen-, CSRF- und Regressionstests ergänzen; veraltete Änderungsvorschläge und konkurrierende Partner prüfen.
- Datenschutz, **Account-Audit**, sichere Startpasswortübergabe, MFA, Protokoll-Aufbewahrung, Backups und Wiederherstellung prüfen; Account-Lifecycle und Admin-Reset sind implementiert.
- Keine Secrets, privaten Accounts, realen Hilfesuchendendaten oder schutzwürdigen Standorte in GitHub bzw. MkDocs dokumentieren.

## 6. Entwicklungs- und Dokumentationskonvention

Der Projektverantwortliche möchte Code **Datei für Datei in VS Code** nachvollziehen. Temporäre ZIP-/Installationsskripte sind keine notwendigen Bestandteile des Repositories. Sinnvolle Tests und SQL-Migrationen können als Nachweis einer nachvollziehbaren Entwicklung erhalten bleiben. Nach jedem Feature: Code/SQL, Testbelege, Deploymentdatum und offene Risiken in MkDocs aktualisieren.
