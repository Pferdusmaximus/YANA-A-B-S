# Wiedereinstieg: aktueller Stand und nächste Aufgaben

**Projekt-Checkpoint: Mittwoch, 18. November 2026.**

## 1. Was ist abgeschlossen?

- Öffentliche Website und JSON-GET-API laufen über HTTPS auf dem IONOS-VPS.
- Gemeinsames Portal für `admin` (YANA-Team) und `partner` (externe, zugeordnete Organisation).
- Admin kann fiktive neue Hilfestellen anlegen; automatisch `draft`, `created`-Audit und neue ID.
- Entwürfe lassen sich bearbeiten, einreichen, veröffentlichen, zurückweisen oder wieder zurücknehmen.
- Öffentliche API liefert ausschließlich `published`-Hilfestellen.
- Partner sehen nur die ihnen per `portal_facility_assignment` zugewiesenen Einträge; ein Testpartner ist vorhanden.
- **Änderungsvorschläge bei veröffentlichten Einträgen**: Partner speichert getrennte Werte, reicht ein; Administrator vergleicht und gibt frei oder lehnt ab. Die öffentliche API ändert sich **erst bei Freigabe**.
- Die Änderungsfreigabe wurde mit fiktiven Testdaten Ende-zu-Ende geprüft und anschließend produktiv bereitgestellt. Die ursprüngliche Telefonnummer wurde nach dem Test wiederhergestellt.

## 2. Welches Feature kommt als Nächstes?

**Administrator-Benutzerverwaltung im bestehenden Portal**, ohne zweites Partnerportal:

1. Partner-Account mit sicherem Passwort anlegen und aktivieren/deaktivieren.
2. Eine oder mehrere Hilfestellen zuweisen und Zuweisungen entziehen.
3. Anzeigen, welche Organisation zu welchem Account gehört.
4. Rollen- und Zuordnungsprüfungen auf allen neuen Endpunkten ergänzen; CSRF, Audit und Negativtests berücksichtigen.
5. Bestehenden Admin-Account niemals unkontrolliert sperren oder umstellen.

Aktuell werden Partner-Accounts und Zuordnungen noch **manuell über pgAdmin** angelegt. Es existiert eine fiktive Test-Partneridentität, aber noch keine Admin-Verwaltungsseite für Konten.

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
- Datenschutz, Account-Lifecycle, Passwort-Reset/MFA, Protokoll-Aufbewahrung, Backups und Wiederherstellung prüfen.
- Keine Secrets, privaten Accounts, realen Hilfesuchendendaten oder schutzwürdigen Standorte in GitHub bzw. MkDocs dokumentieren.

## 6. Entwicklungs- und Dokumentationskonvention

Der Projektverantwortliche möchte Code **Datei für Datei in VS Code** nachvollziehen. Temporäre ZIP-/Installationsskripte sind keine notwendigen Bestandteile des Repositories. Sinnvolle Tests und SQL-Migrationen können als Nachweis einer nachvollziehbaren Entwicklung erhalten bleiben. Nach jedem Feature: Code/SQL, Testbelege, Deploymentdatum und offene Risiken in MkDocs aktualisieren.
