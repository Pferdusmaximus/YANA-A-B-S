# Wiedereinstieg: Nächster Entwicklungsschritt

**Fixierter Projektstand zum Pausieren: Dienstag, 17. November 2026.**

Diese Seite ist der Einstiegspunkt, wenn die YANA-Entwicklung nach der Dokumentationsaktualisierung fortgesetzt wird. Sie unterscheidet abgeschlossene Arbeiten und noch nicht umgesetzte Aufgaben.

## 1. Genau hier wurde gestoppt

**Zuletzt fertiggestellt und produktiv geprüft:**

- Öffentliche YANA-Website mit HTML, CSS, Jinja2 und FastAPI.
- HTTPS über Nginx; bestehende JSON-API für Flutter weiterhin verfügbar.
- Teamportal mit Administrator-Login, Argon2-Passwörtern, Session, Logout, CSRF und Nginx-Loginbegrenzung.
- Geschütztes Dashboard und Hilfestellenübersicht für `admin` und `team`.
- Bearbeitungsformular für **bestehende** Hilfestellen: Name, Telefon, E-Mail, Öffnungszeiten.
- SQL-`UPDATE` mit Validierung, `SELECT ... FOR UPDATE`, Änderungsprotokoll (`portal_facility_audit`).
- Kompletter Speichertest an einer **fiktiven** Hilfestelle, Audit-Prüfung und Wiederherstellung erfolgreich.
- Anschließend **produktives Deployment** auf IONOS und erfolgreiche Browserprüfung des Bearbeitens/Speicherns.
- GitHub `.gitignore` bereinigt, insbesondere Python-Cache aus Versionsverwaltung entfernt.

Nach den erfolgreichen Schritten wurde versehentlich `sudo journalctl -u yana-api -n 40 --no-pager` ausgeführt. Das **liest nur Logeinträge** und hatte keine Auswirkungen auf Server oder Datenbank.

### Konkreter nächster Feature-Schritt

> **„Neue Hilfestelle anlegen“ – ein geschütztes Eingabeformular und eine validierte `INSERT`-Funktion mit Audit- bzw. Erstellungsprotokoll.**

**Noch nicht implementiert!** Nicht als vorhandene Funktion in der Nutzung oder Präsentation aufführen.

## 2. Wo entwickeln wir weiter?

| Zweck | Ort |
|---|---|
| Quellcode bearbeiten | Windows / VS Code / `YANA-A-B-S/services/api/` |
| GitHub synchronisieren | `git pull --rebase origin main` bei sauberem Arbeitsstand; danach `git push` |
| Code vom GitHub auf VPS holen | `~/yana-deploy-source/` |
| Code vorab testen | `~/yana-portal-test/` |
| Produktives Backend | `~/yana-backend/`, Dienst `yana-api` |
| PostgreSQL | `app_db`, pgAdmin 4 auf dem VPS |
| Browserportal | `https://SERVER_IP/portal/login` |

Alle Serverarbeiten wurden bisher über die **grafische Ubuntu-/IONOS-Konsole** ausgeführt. Es ist keine SSH-Verbindung vom Windows-PC erforderlich.

## 3. Empfohlene Umsetzung des neuen Features

1. **Datenbank-Zwangsfelder abgleichen.** Für `hilfestelle` sind `name`, `facility_type`, `address`, `latitude`, `longitude` und `capacity` derzeit `NOT NULL`. `category_id` ist optional. Die zwei ursprünglichen Test-Hilfestellen hatten explizite IDs; den Identity-Sequenzstand vor dem ersten automatisch generierten INSERT prüfen.
2. **Sichtbarkeit und Datenschutz vorab entscheiden.** `GET /hilfestellen` ist öffentlich. Ein neuer Eintrag wäre derzeit sofort für die Flutter-App sichtbar. Vor dem Erfassen realer Hilfeangebote einen Veröffentlichungsstatus, Freigabe und Schutzstandort-Regeln konzipieren; bis dahin **nur fiktive Testdatensätze**.
3. **Formular planen.** Eingabefelder und Pflichtfelder aus Schema ableiten, Kategorien dynamisch laden, feldweise Fehlermeldungen und sichere Defaults vorsehen. Kein ungeprüftes `latitude/longitude`-Freitext-Insert.
4. **Neue FastAPI-Routen.** Z. B. `GET /portal/hilfestellen/neu` und `POST /portal/hilfestellen/neu`; serverseitig Session, Rolle `admin/team`, CSRF und Validierung prüfen. Achtung: Routenreihenfolge in FastAPI; feste Pfade möglichst vor dynamischen `/{facility_id}`-Routen definieren.
5. **Transaktion und Audit.** Parameterisiertes `INSERT`, generierte `facility_id` mit `RETURNING`, Erstellung getrennt von Änderungsprotokollen erfassen (bestehendes Audit-Schema hat `before_data NOT NULL`, ist primär für Änderungen gedacht).
6. **Automatisierte Tests.** Ohne Login, falsche Rolle, falsches CSRF, fehlende Pflichtfelder, falsche Koordinaten, gültiger Insert, DB-/Audit-Prüfung, Wiederherstellung/Entfernung **nur im Testdatenkontext**; vor allem eine isolierte Testdatenbank einrichten.
7. **Deployment.** GitHub → VPS-Code-Testkopie → Backup → produktive Übernahme → `yana-api`-Neustart → Browserprüfung. Alle bisherigen APIs erneut auf Regressionen testen.

## 4. Offene Aufgaben nach dem Anlegen

- Hilfestellen nach Kategorie und Standort filtern, Suche und Pagination.
- Dokumentierte Freigabe neuer/aktualisierter Einrichtungen vor Anzeige in der öffentlichen API.
- Externe Accounts mit **Zuordnung zu eigener Organisation** und genau eingegrenzten Rechten.
- Kanzleien und Leistungen fachlich modellieren, statt sie unüberlegt als einen Hilfestellentyp anzunehmen.
- Benutzerverwaltung, Passwort-Reset/MFA, Betriebsmonitoring und separates Testsystem.
- Flutter-Web-Screens und mobile UI weiter integrieren; Notfallkontakte nur mit verifizierten Daten veröffentlichen.

## 5. Wichtige wiederkehrende Stolperfallen

- Template-Dateiname **`hilfestellen_bearbeiten.html`** (Plural), in `portal_facilities.py` identisch referenzieren.
- Für interaktive Python-Skripte mit `input()`/`getpass()` **eine `.py`-Datei** verwenden und mit `python datei.py` starten, keinen `python - <<'PY'`-Heredoc.
- Bei Test-Skripten zunächst die numerische Hilfestellen-ID (`1` im damaligen Test) eingeben, **erst danach** `TEST` bestätigen.
- `git push` allein aktualisiert nicht die öffentliche Website.
- Nicht übersehene `__pycache__`-Dateien committen; `.gitignore` im Repository-Root beachten.
- Niemals `.env`, reale Passwörter, Session-Secrets, private Schlüssel oder reale Schutzstandort-Daten in GitHub oder MkDocs veröffentlichen.

**Wenn die Entwicklung wieder startet:** mit [Hilfestellenbearbeitung](teamportal-hilfestellen.md), [Datenmodell](datenmodell.md) und [Deployment](teamportal-deployment.md) beginnen. Danach das neue Feature „Hilfestelle anlegen“ implementieren und erst nach erfolgreichem Test den Status dieser Seite aktualisieren.
