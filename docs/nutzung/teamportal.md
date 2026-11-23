# YANA-Verwaltungsportal verwenden

**Stand: 23. November 2026 · Gemeinsames Portal für YANA-Administratoren und externe Partner**

Die Rollen nutzen **denselben Login, dasselbe Dashboard und dieselbe Hilfestellenübersicht**. Das Backend filtert die Daten und erlaubt je nach Rolle unterschiedliche Aktionen. Es gibt weiterhin **keine öffentliche Registrierung**.

## Zugang und Rollen

1. HTTPS-Website öffnen und `/portal/login` aufrufen (`https://SERVER_IP/portal/login`).
2. Mit dem bereitgestellten Account anmelden. Bei einem neuen oder zurückgesetzten Startpasswort zunächst das **eigene Passwort ändern** und erneut anmelden.
3. Im Dashboard die Hilfestellenverwaltung öffnen. Administratoren finden zusätzlich die **Partnerverwaltung**.
4. Nach der Arbeit über **Abmelden** die Session beenden.

| Rolle | In der Übersicht sichtbar | Wichtige Aktionen |
|---|---|---|
| `admin` – YANA-Team | Alle Hilfestellen (aktuell auf 100 pro Aufruf begrenzt) | Testeinträge anlegen, Entwürfe bearbeiten, Freigaben/Zurückweisungen, Partner- und Accountverwaltung im Browser |
| `partner` – externe Einrichtung/Kanzlei | Nur ausdrücklich zugewiesene Hilfestellen | Eigene Entwürfe bearbeiten und einreichen; veröffentlichte Kontaktdaten als Änderungsvorschlag einreichen |

Ein Partner erhält **keinen** allgemeinen Zugriff auf fremde Einträge. Die Zuordnung erfolgt über `portal_facility_assignment`. Zugriffsschutz wird serverseitig geprüft; bloß ausgeblendete Schaltflächen reichen nicht aus. Ein fremder Eintrag ist für Partner auch bei direkter URL nicht abrufbar (typischerweise HTTP 404).

## Neue Hilfestelle erfassen (Administrator)

1. Unter `/portal/hilfestellen` **Neue Hilfestelle** auswählen.
2. Name, Einrichtungstyp, Adresse, Breiten-/Längengrad und Kapazität eingeben; Kategorie und Kontaktdaten nach Bedarf ergänzen.
3. Formular speichern. Das Backend validiert die Eingaben, vergibt die `facility_id` automatisch und erstellt einen Audit-Eintrag `created`.
4. Der neue Eintrag beginnt grundsätzlich als **`draft` (Entwurf)** und erscheint **noch nicht** in der öffentlichen Flutter-API.

**Testbegrenzung:** Die derzeitige Erstellungsfunktion akzeptiert ausschließlich Namen mit Präfix `YANA Test`. Partner können selbst keine neuen Hilfestellen erstellen; diese Berechtigung liegt aktuell beim Administrator.

## Entwurf bearbeiten und veröffentlichen

Einträge mit Status `draft` lassen sich über **Bearbeiten** ändern (Name, Telefon, E-Mail, Öffnungszeiten). Danach kann der berechtigte Account **Zur Prüfung einreichen** auswählen. Der Status wechselt auf `pending_review`, und die direkte Bearbeitung wird gesperrt.

Der YANA-Administrator kann den Entwurf **Freigeben** (`published`) oder **Zurückweisen** (zurück zu `draft`). Eine bereits veröffentlichte Einrichtung kann der Administrator **zurücknehmen**, wodurch sie erneut zum Entwurf und aus der öffentlichen API entfernt wird. Im Teststand dürfen nur als `YANA Test` gekennzeichnete Einträge veröffentlicht werden.

## Veröffentlichte Einrichtung ändern – ohne Offline-Schaltung

Bei einer bereits veröffentlichten, dem Partner zugeordneten Einrichtung wird **Änderung vorschlagen** verwendet, **nicht** die direkte Bearbeitung von `/edit`.

1. Partner öffnet **Änderung vorschlagen** und ändert z. B. eine Telefonnummer.
2. **Als Entwurf speichern** speichert den Vorschlag ausschließlich in `portal_facility_change`. Die bisher freigegebenen Kontaktdaten bleiben in `hilfestelle` und in der Flutter-API unverändert.
3. **Zur Prüfung einreichen** setzt den Antrag auf `pending_review`; weitere Bearbeitung ist bis zur Entscheidung gesperrt.
4. Administrator öffnet **Änderungsanträge prüfen** unter `/portal/aenderungen` und sieht alte und vorgeschlagene Werte nebeneinander.
5. Bei **Änderungen freigeben** werden die vier zulässigen Felder in einer Transaktion aktualisiert. Bei **Zurückweisen** bleiben die veröffentlichten Werte unverändert; eine optionale Begründung kann eingetragen werden.

Pro Einrichtung ist maximal ein aktiver Änderungsentwurf oder Prüfantrag gleichzeitig zulässig. Ein eigener Entwurf kann verworfen werden. Ein anderer berechtigter Bearbeiter darf einen fremden aktiven Entwurf nicht übernehmen.

## Status und Nachvollziehbarkeit

| Status des Eintrags (`hilfestelle`) | Bedeutung | Öffentliche API |
|---|---|---|
| `draft` | Nicht veröffentlicht; direkt bearbeitbar | Nein |
| `pending_review` | Neuaufnahme wird geprüft | Nein |
| `published` | Freigegebener Eintrag | Ja, mit aktuellen öffentlichen Spalten |

**Davon getrennt** existiert der Status eines *Änderungsvorschlags*: `draft`, `pending_review`, `approved`, `rejected` oder `cancelled`. Ein offener Änderungsvorschlag verändert den Veröffentlichungsstatus der Hilfestelle nicht.

Änderungen und Freigaben werden mit Account-Zuordnung und Zeitstempel in `portal_facility_audit` protokolliert. Eine allgemeine Audit-Historienansicht im Browser ist noch nicht umgesetzt.

## Sicherheit und Grenzen

- Nur fiktive Daten verwenden; keine realen Schutzunterkunft-Adressen speichern. **Der Veröffentlichungsfilter schützt nicht einzelne Adressfelder.**
- Name, Telefon, E-Mail und Öffnungszeiten sind die vier Felder des Änderungsworkflows. Standortdaten, Leistungen, Kapazität und Kategorie sind damit noch nicht nachträglich bearbeitbar.
- **Partner-Accounts und Zuordnungen werden inzwischen im Verwaltungsportal bearbeitet.** Startpasswörter werden einmalig generiert; Passwortwechsel, Deaktivieren, Reaktivieren und Admin-Reset sind implementiert. Ein Mailserver, öffentliche Selbstregistrierung und MFA fehlen weiterhin.
- Die öffentliche API ist kein Login-geschützter Dienst. Vor echten Einträgen sind Datenfreigabe und Datenschutzkonzept erforderlich.

Weitere Informationen: [Partner-Accounts verwalten](partnerverwaltung.md), [Technischer Ablauf der Änderungsfreigabe](../technik/teamportal-aenderungsfreigabe.md), [Hilfestellenverwaltung](../technik/teamportal-hilfestellen.md), [Portal-Sicherheit](../technik/teamportal-login.md).
