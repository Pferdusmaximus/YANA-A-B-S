# Änderungsvorschläge und Administratorfreigabe

**Dokumentationsstand: 18. November 2026 · Auf fiktiven Partnerdaten Ende-zu-Ende getestet und produktiv bereitgestellt**

## 1. Zweck

Bereits veröffentlichte Hilfestellen sollen für die Flutter-App **durchgehend verfügbar** bleiben, auch wenn eine Partnerorganisation Korrekturen beantragt. Deshalb werden Änderungen nicht unmittelbar in `hilfestelle` gespeichert, sondern zuerst als eigenständiger Antrag in **`portal_facility_change`** erfasst.

Diese Funktion ist Teil **desselben YANA-Verwaltungsportals**. Partner und Administratoren verwenden dieselbe Website mit rollenabhängigen Funktionen; es existiert kein zweites Partnerportal.

## 2. Unterstützte Änderungen

Derzeit umfasst der Workflow nur `name`, `phone`, `email` und `opening_hours`. Die Feldlängen und Validierung entsprechen der bisherigen Bearbeitungsfunktion (Name 100, Telefon 30, E-Mail 150, Öffnungszeiten 200 Zeichen). Die Testdatenbeschränkung `YANA Test` gilt auch beim Antrag und erneut bei der Freigabe.

Keine nachträgliche Änderung über diesen Ablauf: Anschrift, Koordinaten, Einrichtungstyp, Kapazität, Kategorie oder Leistungen.

## 3. Partnerablauf

1. Als Partner anmelden und **nur die zugewiesene** veröffentlichte Hilfestelle öffnen.
2. **Änderung vorschlagen** führt zu `GET /portal/hilfestellen/{facility_id}/aenderung`.
3. Werte ändern; **Als Entwurf speichern** setzt/behält den Antrag auf `draft`.
4. **Zur Prüfung einreichen** setzt `portal_facility_change.status` auf `pending_review`.
5. Während der Prüfung ist das Formular gesperrt. Der Partner sieht eine Statusmeldung; die veröffentlichten Werte bleiben unverändert.
6. Bei Ablehnung kann ein neuer Antrag gestellt werden; ein eigener noch nicht eingereichter Entwurf kann verworfen werden (`cancelled`).

Die Anwendung erlaubt **höchstens einen aktiven Antrag (`draft` oder `pending_review`) je Hilfestelle**. Ein anderer zugeordneter Partner kann den aktiven privaten Entwurf nicht bearbeiten oder dessen Daten einsehen.

## 4. Prüfablauf des YANA-Administrators

Die geschützte Seite `GET /portal/aenderungen` listet bis zu 100 offene Anträge und zeigt geänderte Werte **alt vs. beantragt** an. Es existieren zwei Entscheidungen:

- `POST /portal/aenderungen/{change_id}/approve`: Antrag freigeben; bisherige Datensatzwerte prüfen, vier Felder in `hilfestelle` aktualisieren, Antrag auf `approved` setzen, Audit `change_approved` schreiben.
- `POST /portal/aenderungen/{change_id}/reject`: Antrag mit optionalem Hinweis zurückweisen, Status `rejected`, Audit `change_rejected`; `hilfestelle` bleibt unverändert.

Freigabe und Status-/Audit-Aktualisierung geschehen in **einer PostgreSQL-Transaktion**. Das Backend sperrt den Datensatz und Antrag (`SELECT ... FOR UPDATE`) und vergleicht die öffentliche Ausgangsversion mit `base_data`. Wurden öffentliche Werte zwischenzeitlich geändert oder ist die Hilfestelle nicht mehr veröffentlicht, wird die Freigabe mit HTTP 409 verweigert.

## 5. Datenmodell

| Tabelle / Feld | Bedeutung |
|---|---|
| `portal_facility_change.change_id` | Eindeutige ID des Änderungsantrags |
| `facility_id` | Betroffene veröffentlichte Einrichtung |
| `created_by_account_id` | Antragsteller |
| `status` | `draft`, `pending_review`, `approved`, `rejected`, `cancelled` |
| `base_data` (JSONB) | Werte der öffentlichen Einrichtung zum Erstellungszeitpunkt |
| `proposed_data` (JSONB) | Vorgeschlagene neue Werte |
| `review_note` | Optionale Begründung bei Entscheidung |
| `reviewed_by_account_id` | Entscheidender Administrator |
| `created_at`, `updated_at`, `submitted_at`, `reviewed_at` | Nachvollziehbare Bearbeitungszeitpunkte |

Ein partieller Unique-Index begrenzt offene Anträge auf einen pro Hilfestelle; ein weiterer Index unterstützt die Warteschlange. Details stehen in [Portal-Datenbank](teamportal-datenbank.md). Die SQL-Migration `sql/01_change_requests.sql` ist im Repository zu dokumentieren und **nicht erneut blind auf der produktiven Datenbank auszuführen**.

## 6. Implementierte Endpunkte

| Methode | Pfad | Wirkung / Schutz |
|---|---|---|
| `GET` | `/portal/hilfestellen/{id}/aenderung` | Zugeordnete veröffentlichte Einrichtung, Formular |
| `POST` | `/portal/hilfestellen/{id}/aenderung` | Entwurf speichern (`mode=save`) oder einreichen (`mode=submit`), CSRF |
| `POST` | `/portal/hilfestellen/{id}/aenderung/discard` | Eigenen Entwurf verwerfen, CSRF |
| `GET` | `/portal/aenderungen` | Nur Admin: offene Anträge vergleichen |
| `POST` | `/portal/aenderungen/{change_id}/approve` | Nur Admin: Daten übernehmen und Audit |
| `POST` | `/portal/aenderungen/{change_id}/reject` | Nur Admin: Antrag zurückweisen und Audit |

Der Code befindet sich in `services/api/portal_facility_changes.py`. Verwendete Templates sind `aenderung_bearbeiten.html` und `aenderungen_pruefen.html`. Der Router wird über `main.py` eingebunden. Ein gültiges Session-Cookie und CSRF-Token sind für zustandsändernde Formularaktionen erforderlich.

## 7. Nachgewiesene Tests (18.11.2026)

Der automatische End-to-End-Test wurde mit dem bereits angelegten fiktiven Partner-Account und einer zugeordneten veröffentlichten Test-Hilfestelle durchgeführt. Im Projektverlauf als erfolgreich gemeldet:

1. Admin- und Partner-Login sowie Rechteprüfung.
2. Änderung als Entwurf speichern – **öffentliche Werte unverändert**.
3. Antrag einreichen – **öffentliche Werte unverändert**.
4. Admin gibt Änderung frei – neue Werte über die öffentliche API sichtbar.
5. Ursprüngliche fiktive Telefonnummer über erneuten Antrag wiederherstellen.
6. Erwartete Audit-Ereignisse kontrollieren.

Nach diesen Tests wurden die geänderten Anwendungsdateien produktiv bereitgestellt; die Browserprüfung wurde als erfolgreich bestätigt. Die Datenbank wird weiterhin von Test- und Produktivcode gemeinsam verwendet. Ein E2E-Test ist kein vollständiger Sicherheits- oder Penetrationstest.

## 8. Offene Punkte

- Echte Einrichtungen und insbesondere geheime Schutzunterkunft-Adressen dürfen derzeit nicht übernommen werden.
- Kein allgemeines Ändern von Adresse, Kapazität, Kategorie, Leistungen oder Koordinaten über Antrag.
- Keine automatische Benachrichtigung per E-Mail/Push bei Freigabe oder Ablehnung.
- Kein zentraler UI-Dialog zum Anlegen und Zuordnen von Partner-Accounts.
- Für komplexere parallele Änderungen und langfristige Versionshistorie ist ein erweitertes Konflikt-/Historienkonzept sinnvoll.
