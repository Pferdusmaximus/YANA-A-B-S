# Entwicklungsstand und Projektmeilensteine

**Dokumentationsstand: 24. November 2026 · Der bewusst gesetzte Pause-Punkt liegt nach dem bestandenen Geoapify-Speichertest und vor dem noch unbestätigten Produktivdeployment.**

## 1. Zeitlicher Verlauf

| Zeitraum | Umsetzung | Ergebnis |
|---|---|---|
| Oktober 2026 | Ubuntu-VPS, PostgreSQL, pgAdmin, FastAPI, Nginx/HTTPS | Server und GET-API erreichbar |
| Oktober/November 2026 | Flutter-Entwicklungsumgebung; API-Models, Repositories, Controller und Tests | Technische Grundlagen für App und API-Anbindung |
| November 2026 | Öffentliche Website, GitHub-Workflow und CORS | Website auf IONOS erreichbar, lokaler Flutter-Web-Zugriff möglich |
| November 2026 | Login, Session-Hash, Argon2, CSRF, Nginx-Loginbegrenzung | Geschütztes Verwaltungsportal |
| **17.11.2026** | Hilfestellen anzeigen und vorhandene Kontaktfelder bearbeiten | Test und produktive Browserprüfung mit Audit bestanden |
| **18.11.2026** | Neue Hilfestellen erfassen, ID automatisch generieren, Audit | Funktionstests und fiktiver Speichertest erfolgreich; produktiv |
| **18.11.2026** | Veröffentlichungsstatus und öffentliche API-Filterung | `draft` / `pending_review` / `published`; API liefert nur `published` |
| **18.11.2026** | Freigabeaktionen für Neuaufnahmen | Einreichen, Freigeben, Zurückweisen und Zurücknehmen getestet; produktiv |
| **18.11.2026** | Partnerrolle und Einrichtungszuordnung | `admin`/`partner`, `portal_facility_assignment`; Testpartner kann eigene Einrichtung sehen |
| **18.11.2026** | Änderungen an veröffentlichten Einträgen | Getrennter Entwurf, Admin-Freigabe, öffentliche API erst danach aktualisiert; E2E-Test und Produktivprüfung bestanden |
| **23.11.2026** | Partnerverwaltung im Portal | Account-Erstellung mit Startpasswort, Zuweisen/Entfernen, eigener Pflicht-Passwortwechsel |
| **23.11.2026** | Account-Lebenszyklus | Deaktivieren, Reaktivieren und Admin-Reset; 12 Integrationstests nach Nutzerangabe bestanden, produktiv bereitgestellt |
| **24.11.2026** | Öffentlicher Datenschutzfilter für Standorte | Einzel- und Typfreigabe für Adresse/Koordinaten, DB-Trigger, Administratorverwaltung; Test und Produktivprüfung bestanden |
| **24.11.2026** | Website-Design | Einheitliche weiß-lila Farbpalette, Navigation/Logout, kompakte Partner- und Standorttabellen; produktiv bestätigt |
| **24.11.2026** | Geoapify-Geocoding | Adresseingabe, echte externe Suche, Bestätigungscode und Speicherung mit/ohne Koordinaten in Testumgebung erfolgreich geprüft; Produktivdeployment noch nicht bestätigt |

## 2. Aktueller Funktionsstatus

| Funktion | Status |
|---|---|
| Öffentliche YANA-Website | **Implementiert** |
| Öffentliche GET-API | **Implementiert**, nur veröffentlichte fiktive Hilfestellen |
| Admin- und Partner-Login / Sessions / Logout / CSRF | **Implementiert und geprüft** |
| Neue fiktive Hilfestellen anlegen | **Implementiert**, derzeit nur durch Admin |
| Entwürfe bearbeiten und einreichen | **Implementiert** |
| Neuaufnahmen freigeben / zurückweisen / zurücknehmen | **Implementiert** (Adminentscheidung) |
| Partner sehen nur zugewiesene Einrichtungen | **Implementiert und im Browser geprüft** |
| Änderungsvorschläge veröffentlichter Einträge | **Implementiert**, Name/Telefon/E-Mail/Öffnungszeiten |
| Administrator prüft Änderungsvorschläge | **Implementiert**, alt/neu, Freigabe/Zurückweisung |
| Audit-Protokollierung | **Implementiert**; noch keine allgemeine Audit-Webansicht |
| Partnerkonten über Website erstellen / zuordnen | **Implementiert**; Accountverwaltung unter `/portal/partner` |
| Startpasswort, Pflichtwechsel und eigenes Passwort ändern | **Implementiert und mit Testpartner geprüft** |
| Account deaktivieren, reaktivieren, Passwort-Reset | **Implementiert und E2E-getestet** |
| Standortdaten öffentlich schützen | **Implementiert und produktiv** für `address`, `latitude`, `longitude` mit separater Standortfreigabe; weitere sensible Daten offen |
| Administratorseite Standortfreigaben | **Implementiert und produktiv**, Tabelle/Suche/Filter/Detailaktionen |
| Automatische Adresseingabe bei Neuanlage | **Testumgebung erfolgreich**, Geoapify-Speichertest bestanden; Deployment noch offen |
| Reale Einrichtungen umfassend datenschutzrechtlich freigeben | **Noch offen**; weitere Felder und fachliche Prüfung |
| Hilfestellen komplett löschen | **Offen** |
| App-Download und vollständige mobile UI | **Noch nicht veröffentlicht / nicht vollständig nachgewiesen** |
| Reale anonyme Beratung und verifizierte Notfallhilfe | **Nicht als produktiver Dienst verfügbar** |

## 3. Relevante Korrekturen

- `hilfestellen_bearbeiten.html` muss im Template-Renderaufruf im **Plural** referenziert werden.
- Die Erstellungsmaske benötigte ein gespeichertes und übertragenes HTML-Template mit `<input name="csrf_token">`; erst danach bestanden alle zehn Funktionstests.
- Beim Partnerlogin zeigte das Dashboard zunächst **„Keine Berechtigung“**, obwohl Python-Rollenprüfungen und DB-Zuordnung korrekt waren. Ursache war der alte `admin`/`team`-Zweig im Dashboard-Template; nach Umstellung auf `admin`/`partner` konnte der Partner seine Hilfestelle öffnen.
- FastAPI-Route-Introspektion über `app.routes` zeigte bei verschachtelten Routern nicht alle Pfade; ein realer `TestClient`-Aufruf bestätigte die Endpunkte.
- Testkopie und Produktivcode nutzen dieselbe PostgreSQL-Datenbank; echte Schreibtests wurden bewusst auf fiktive Daten begrenzt und wiederhergestellt.

## 4. Nachweise und Entwicklungsprozess

Entwickelt wird unter Windows/VS Code, versioniert über GitHub, geprüft in `~/yana-portal-test` und nach bestandenen Tests mit Sicherung in `~/yana-backend` bereitgestellt. Der produktive Systemdienst heißt `yana-api`. Automatische Integrationshilfen/ZIP-Pakete waren nur temporäre Entwicklungswerkzeuge; die dauerhaft benötigten Python-Module, Templates, CSS-Änderungen, Migration und sinnvolle Tests bleiben im Projekt nachvollziehbar dokumentiert.

## 5. Nächste Meilensteine

Die **Administrator-Benutzerverwaltung**, der **zweistufige Standortschutz** und das **weiß-lila Webdesign** sind produktiv umgesetzt. Als **nächster unmittelbarer Arbeitsschritt** folgt die Produktivbereitstellung der bereits erfolgreich getesteten **Geoapify-Neuanlage** (sechs Dateien + `.env`/Dienst/Browserprüfung). Danach: bestehende Hilfestellen mit der gleichen Adresseingabe bearbeiten, Flutter mit nullable Koordinaten prüfen, isolierte Testdatenbank, umfassende Regressionstests und Account-Audit. Siehe [Wiedereinstieg](weiterarbeit.md).

## 6. Nachtrag 23.11.2026: Partner- und Passwortverwaltung

Hinzugekommen sind `portal_partners.py`, `portal_password.py`, die Vorlagen `partner.html`, `partner_erstellt.html` und `passwort_aendern.html` sowie die Datenbankspalte `must_change_password`. Die Endpunkte unterstützen Account-Erstellung, Partner-/Einrichtungszuordnung, verpflichtenden Startpasswortwechsel, Deaktivierung, Reaktivierung und Passwort-Reset. Die schreibfreien Prüfungen und der vollständige Lifecycle-Test (12 Prüfschritte) wurden erfolgreich abgeschlossen; die anschließende produktive Bereitstellung wurde im Gespräch als erfolgreich bestätigt. Näheres unter [Benutzerverwaltung](teamportal-benutzerverwaltung.md).
