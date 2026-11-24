# Hilfestellenverwaltung: Anlegen, Bearbeiten und Status

**Stand: 24. November 2026 · Neueintrag und Statusfreigabe produktiv; Geoapify-Neuanlage in der Testumgebung geprüft, Produktionsübernahme noch offen**

## 1. Funktionen und Zuständigkeiten

| Funktion | `admin` | `partner` |
|---|---|---|
| Hilfestellen sehen | Alle (max. 100 alphabetisch) | Nur zugewiesene (max. 100) |
| Neue Hilfestelle anlegen | Ja, nur `YANA Test`-Einträge | Nein |
| Nicht veröffentlichten Entwurf bearbeiten | Ja | Nur zugewiesenen Entwurf |
| Zur Prüfung einreichen | Ja | Nur zugewiesenen Entwurf |
| Einreichung freigeben / zurückweisen | Ja | Nein |
| Veröffentlichung zurücknehmen | Ja | Nein |
| Veröffentlichte Kontaktdaten ändern | Über [Änderungsantrag](teamportal-aenderungsfreigabe.md) | Über eigenen [Änderungsantrag](teamportal-aenderungsfreigabe.md) |

Die Freigabe für neue Einträge ist vom **Änderungsantrag für bereits veröffentlichte Einträge** zu unterscheiden.

## 2. Neue Hilfestelle anlegen

Die Routen `GET/POST /portal/hilfestellen/neu` liegen in `portal_facilities_create.py`. Im bisherigen Produktivstand werden für die Neuerstellung die Standortdaten noch über den ursprünglichen Formularablauf erfasst. **Die neue, erfolgreich getestete Version von `hilfestellen_neu.html` fragt Straße, Hausnummer, PLZ und Ort statt manuell einzugebender Koordinaten ab.** Ein Klick auf „Standort ermitteln“ startet für ausdrücklich als nicht vertraulich gekennzeichnete Beratungsstellen eine Geoapify-Abfrage. Ein signierter Bestätigungscode bindet den Treffer an die geprüfte Adresse; ohne gültigen Treffer kann die Hilfestelle als Entwurf ohne Koordinaten gespeichert werden. Die neue Eingabe ist **am aktuellen Checkpoint noch nicht als produktiv veröffentlicht bestätigt**. Details: [Geocoding](geocoding.md). Für die aktuelle Testphase muss der Name mit **`YANA Test`** beginnen.

Das Datenbank-`INSERT` nutzt parametrisierte SQL-Werte und `RETURNING facility_id`. Ein `created`-Ereignis wird in `portal_facility_audit` protokolliert. Durch `publication_status DEFAULT 'draft'` erscheint der neue Datensatz nicht automatisch über `/hilfestellen`.

## 3. Entwürfe bearbeiten

`GET/POST /portal/hilfestellen/{facility_id}/edit` in `portal_facilities.py` erlaubt die Bearbeitung ausschließlich, solange `publication_status = 'draft'` gilt. **Für Partner** ist die zugehörige Berechtigungszuordnung bereits in der Datensatzabfrage geprüft. Fremde Einträge sind nicht einsehbar oder veränderbar.

| Bearbeitbares Feld | Regel im Backend |
|---|---|
| `name` | erforderlich, maximal 100 Zeichen |
| `phone` | optional, maximal 30 Zeichen |
| `email` | optional, maximal 150 Zeichen, einfache Formatprüfung |
| `opening_hours` | optional, maximal 200 Zeichen |

`facility_type`, `address`, `latitude`, `longitude`, `capacity`, `category_id` und Leistungen können nicht nachträglich über dieses Formular bearbeitet werden. Das `UPDATE` und der Audit-Eintrag erfolgen innerhalb einer Transaktion; die zugehörige Zeile wird mit `FOR UPDATE` gesperrt.

## 4. Freigabeprozess für neue Einträge

Der separate Router `portal_facilities_status.py` verarbeitet:

| POST-Aktion | Vorher | Nachher | Berechtigung |
|---|---|---|---|
| `/portal/hilfestellen/{id}/status/submit` | `draft` | `pending_review` | Admin oder zugeordneter Partner |
| `.../status/approve` | `pending_review` | `published` | Admin |
| `.../status/reject` | `pending_review` | `draft` | Admin |
| `.../status/unpublish` | `published` | `draft` | Admin |

Alle Aktionen benötigen Anmeldung, gültige Rolle, CSRF-Token und eine erlaubte Statusübergangsregel. Statuswechsel werden mit Eventtyp in `portal_facility_audit` protokolliert. Veröffentlichungen bleiben in der Testphase auf `YANA Test`-Datensätze begrenzt.

Die öffentliche API `GET /hilfestellen` wählt ausschließlich `publication_status = 'published'`. Der Status selbst muss nicht im öffentlichen JSON enthalten sein.

## 5. Bereits veröffentlichte Einträge

Der direkte `/edit`-Endpunkt verweigert hier Änderungen (HTTP 409). Statt die Veröffentlichung für eine einfache Telefonkorrektur zurückzunehmen, nutzt ein Partner den **separaten Änderungsvorschlag**. Der bisherige veröffentlichte Datensatz bleibt bis zur Freigabe erhalten.

Details, SQL-Transaktionen und Grenzen: [Änderungs- und Freigabeprozess](teamportal-aenderungsfreigabe.md).

## 6. Tests und Datenschutz

Die Erstellung wurde durch zehn Funktionstests und einen echten fiktiven Speichertest mit ID-/Audit-/API-Kontrolle geprüft. Der Statusworkflow und die Partner-Zugriffsbeschränkung wurden einschließlich negativer Berechtigungstests erprobt; die Browserbedienung wurde produktiv geprüft. Tests auf dem VPS greifen **auf die gemeinsame produktive Datenbank** zu, daher nur mit fiktiven Testdaten.

Veröffentlichung ist **keine** sichere Freigabe vertraulicher Standortdaten. Bei Status `published` enthält die öffentliche API weiterhin Adressen und Koordinaten; vor einer echten Schutzunterkunft muss eine getrennte Sichtbarkeits-/Datenschutzregel implementiert werden.

## 7. Standortfelder und nächste Erweiterung (24.11.2026)

Die Spalten `latitude` und `longitude` sind nach Datenbankmigration **nullable**; ein CHECK-Constraint erlaubt nur ein vollständiges Paar oder beide Werte `NULL`. Das ermöglicht das Speichern eines Entwurfs bei fehlendem Geoapify-Treffer. Die öffentliche Sichtbarkeit hängt **nicht** von der bloßen Speicherung ab, sondern von der [zweistufigen Standortfreigabe](standort-datenschutz.md). Die bestehende Bearbeitungsseite für bereits angelegte Hilfestellen enthält noch **keine neue Adresse-/Geocoding-Funktion**; dies ist der nächste fachliche Schritt **nach** dem Deployment der Neuanlage.
