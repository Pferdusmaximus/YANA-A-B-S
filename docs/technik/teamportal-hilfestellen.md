# Teamportal: Hilfestellen anzeigen und bearbeiten

**Stand: 17. November 2026 · Produktiv im Browser getestet, inkl. Speicherung und Audit-Log**

## 1. Aktueller Funktionsumfang

Im geschützten Teamportal werden die vorhandenen fiktiven Einträge der PostgreSQL-Tabelle `hilfestelle` als HTML-Tabelle angezeigt. Die erste Verwaltungsfunktion erlaubt das **Bearbeiten einzelner bestehender Hilfestellen**. Ein neues Anlegen, Deaktivieren oder Löschen von Einträgen ist derzeit noch nicht implementiert.

| Funktion | Status |
|---|---|
| Hilfestellenübersicht mit Datenbankinhalt | Implementiert, produktiv geprüft |
| Rollenprüfung `admin` / `team` | Implementiert; `facility` erhält HTTP 403 |
| Bearbeitungsformular für existierende Einrichtung | Implementiert |
| Name, Telefon, E-Mail, Öffnungszeiten ändern | Implementiert |
| Serverseitige Prüfung und CSRF | Implementiert, Grundtests erfolgreich |
| SQL-Update mit Zeilensperre + Audit | Implementiert und durch Speichertest bestätigt |
| Neue Hilfestelle mit `INSERT` anlegen | **Noch offen – nächster Schritt** |
| Adresse/Koordinaten über Portal ändern | Noch nicht freigegeben |
| Externe Organisationszuordnung / Freigabe | Noch offen |

## 2. Aufruf im Browser

1. Unter `https://SERVER_IP/portal/login` anmelden.
2. Im Dashboard den Link **Hilfestellen anzeigen** wählen.
3. In `/portal/hilfestellen` eine Zeile auswählen und auf **Bearbeiten** klicken.
4. Bearbeitungsformular ausfüllen und **Änderungen speichern** drücken.
5. Nach Weiterleitung zurück auf dieselbe Seite die Erfolgsmeldung prüfen.
6. Bei Bedarf den neuen Wert über `GET /hilfestellen` oder in pgAdmin kontrollieren.

Nur berechtigte Mitarbeiterkonten dürfen diese Schritte ausführen. Ohne Login folgt eine Weiterleitung zu `/portal/login`, mit unzureichender Rolle eine Ablehnung.

## 3. Technische Implementierung

| Datei | Verantwortlichkeit |
|---|---|
| `services/api/portal_facilities.py` | Übersicht, GET-/POST-Bearbeitungsroute, Validierung, Update, Audit |
| `templates/portal/hilfestellen.html` | Datentabelle und Bearbeiten-Links |
| `templates/portal/hilfestellen_bearbeiten.html` | Formular (bewusst **Plural** im Dateinamen) |
| `templates/portal/dashboard.html` | Link aus der Dashboard-Kachel |
| `static/css/style.css` | Tabellen- und Formular-Styling |
| `database.py` | Bereitstellung von `get_connection()` |

**Dateinamenskonvention:** Die Route heißt `/portal/hilfestellen/{facility_id}/edit`, das Template heißt `portal/hilfestellen_bearbeiten.html`. Während der Entwicklung wurde versehentlich `hilfestelle_bearbeiten.html` (Singular) referenziert; dies führte zu `TemplateNotFound` und wurde in der Testumgebung und im Quellcode korrigiert.

## 4. Datenabruf und Berechtigungen

Die Übersicht liest die ersten **100** Hilfestellen alphabetisch und führt einen `LEFT JOIN` mit `kategorie` aus, um den Kategorienamen anzuzeigen. Dieser Grenzwert ist ein vorläufiger Entwicklungsstand, **keine** paginierte Gesamtliste. Vor einer größeren Datenbasis braucht es Suchfunktion, Filter, Pagination und eine konsistente Gesamtanzahl.

Die Bearbeitungsseite liest einen Datensatz anhand seiner `facility_id`. Beide Routen verwenden `session_account()` und eine Prüfung auf die Rollen `admin` oder `team`. Die POST-Route prüft zusätzlich `check_csrf()`.

## 5. Bearbeitbare Felder und Validierung

| Spalte in `hilfestelle` | HTML-Feld | Eingaberegel im Backend |
|---|---|---|
| `name` | Textfeld | erforderlich, nach Trim nicht leer, max. 100 Zeichen |
| `phone` | Telefonnummer | optional, max. 30 Zeichen |
| `email` | E-Mail | optional, max. 150 Zeichen und einfache E-Mail-Formatprüfung |
| `opening_hours` | Mehrzeiliger Text | optional, max. 200 Zeichen |

Andere DB-Spalten (z. B. `facility_type`, `address`, `latitude`, `longitude`, `capacity`, `category_id`) bleiben beim Speichern unverändert. Das Eingabelimit für `name` ist aktuell restriktiver als das Datenbankschema (`VARCHAR(150)`), ebenso für Öffnungszeiten (`VARCHAR(255)`); es sollte später bewusst fachlich abgestimmt werden.

Bei ungültigem Namen antwortet der Server mit **HTTP 422** und zeigt den Fehler auf der Formularseite an; mit gefälschtem CSRF-Token mit **HTTP 403**. Beim erfolgreichen Speichern folgt ein **HTTP 303** auf `/portal/hilfestellen/{id}/edit?saved=1`.

## 6. Datenbanktransaktion und Änderungsnachweis

Die POST-Route sperrt die betroffene Zeile mit `SELECT ... FOR UPDATE`. Bei tatsächlicher Änderung erfolgen in einer Transaktion:

```sql
-- vereinfachtes Schema des implementierten Ablaufs
UPDATE public.hilfestelle
SET name = %s, phone = %s, email = %s, opening_hours = %s
WHERE facility_id = %s;

INSERT INTO public.portal_facility_audit
    (facility_id, account_id, before_data, after_data)
VALUES (%s, %s, %s, %s);
```

Die Parameter werden über Psycopg übergeben, nicht in SQL-Strings hineinkonkatenatiert. Das Audit speichert den vorherigen und neuen Zustand der vier bearbeitbaren Felder als JSONB und verknüpft ihn mit dem eingeloggten Account und dem Zeitpunkt. Bei einem Datenbankfehler soll die Transaktion gemeinsam zurückgerollt werden.

**Achtung:** Die Test- und Produktions-Python-Instanz benutzen dieselbe PostgreSQL-Datenbank. Selbst ein Test im Verzeichnis `~/yana-portal-test` kann echte Tabelleninhalte verändern. Tests mit Änderungen daher nur an ausdrücklich fiktiven Einträgen und mit Wiederherstellungsprüfung durchführen.

## 7. Bestätigter Speichertest

Der Projektverlauf bestätigt folgende Prüfkette als bestanden:

| Prüfung | Ergebnis |
|---|---|
| Bearbeitungsseite ohne Login | HTTP 303 |
| Admin-Login | HTTP 303 |
| Bearbeitungsseite als Admin | HTTP 200 |
| Ungültiges CSRF-Token | HTTP 403 |
| Leerer/ungültiger Name | HTTP 422 |
| Fiktive Telefonnummer speichern | HTTP 303 |
| Wert erneut aus `hilfestelle` lesen | Testwert vorhanden |
| Neuesten Audit-Eintrag lesen | Änderung protokolliert |
| Ursprüngliche Nummer wiederherstellen | HTTP 303; Originalwert bestätigt |
| Abmelden | HTTP 303 |

Danach wurden die getesteten Dateien in das produktive Backend übernommen, der Dienst `yana-api` neu gestartet und die Bearbeitungsfunktion **im Browser erfolgreich getestet**. Die produktive Datenänderung wurde anschließend zurückgesetzt.

## 8. Fachliche Risiken und Grenzen

- `GET /hilfestellen` ist öffentlich; für echte Schutzunterkünfte dürfen vertrauliche Adressen und Koordinaten nicht ausgegeben werden.
- Berechtigungen für externe Betreiber sind **noch nicht** implementiert; `facility` darf nicht pauschal alle Einträge bearbeiten.
- Änderungen werden momentan direkt sichtbar, es existiert **keine** Moderation/Freigabe für externe Inhalte.
- Audit-Einträge können personenbezogene Kontaktwerte enthalten; Zugriff und Löschfristen sind zu definieren.
- Noch kein Schutz gegen gleichzeitige fachliche Bearbeitung über längere Zeiträume: `FOR UPDATE` schützt die Transaktion, aber ein zwischenzeitlich im Browser veraltetes Formular kann weiterhin neuere Werte überschreiben. Optimistic Locking/Versionsfeld ist offen.

Das konkrete nächste Arbeitspaket steht auf der Seite [Weiterarbeit](weiterarbeit.md). Technische Testabläufe: [Portal-Tests](teamportal-tests.md).
