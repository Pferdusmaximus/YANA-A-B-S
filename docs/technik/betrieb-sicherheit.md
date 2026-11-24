# Betrieb, Sicherheit und Datenschutz

**Dokumentationsstand: 24. November 2026.** YANA ist ein funktionsfähiger **Entwicklungsprototyp** mit öffentlicher Informationswebsite, Flutter-GET-API und gemeinsamem Verwaltungsportal. Die erfolgreichen Funktionstests sind **keine Freigabe für echte sensible Hilfedaten**.

## 1. Technischer Betriebsstand

| Bereich | Bestätigter Stand / Grenze |
|---|---|
| IONOS-VPS, Ubuntu, PostgreSQL `app_db` | Eingerichtet; acht Fach-/Chat-, fünf Portal- sowie eine Standort-Positivlisten-Tabelle dokumentiert |
| Nginx/HTTPS, systemd `yana-api` | Produktiv eingerichtet und im Browser geprüft |
| FastAPI-/Flutter-Schnittstellen | Öffentliche GET-Routen erreichbar; lokale Flutter-Web-CORS-Regel |
| Gemeinsames Portal | Admin- und Partner-Testaccount können sich anmelden |
| Rollenrechte | Partner sieht nur explizit zugewiesene Hilfestellen; Admin besitzt Freigabe- und Accountverwaltungsrechte |
| Account-Lebenszyklus | Partner erstellen, Startpasswort/Pflichtwechsel, deaktivieren, reaktivieren, Reset und Session-Entzug getestet |
| Neuaufnahmen | Entwurf / Prüfung / Veröffentlichung und Audit für Testdaten implementiert |
| Änderungsvorschläge | Getrennte gespeicherte Werte; öffentliche Daten erst bei Adminfreigabe verändert |
| Öffentliche Standorte | Zweistufiger Filter für Adresse/Koordinaten, Admin-Freigabe und DB-Trigger produktiv geprüft |
| Geoapify | Echte externe Abfrage und vollständige Speichertests in der Testumgebung bestanden; produktive Einbindung des neuen Formulars noch nicht bestätigt |
| Website-Design | Weiß-lila Redesign mit kompakten Partner- und Standorttabellen produktiv bestätigt |
| Backup-Agent | Registriert; vollständiger Restore-Test weiterhin offen |
| Login-Rate-Limit | Nginx-Konfiguration aktiv; kontrollierter Lasttest weiterhin offen |
| Reale Hilfsangebote / geheime Schutzadressen | Nicht für den Realbetrieb freigegeben |

## 2. Netzwerk- und Vertrauensgrenzen

```text
Internet (HTTPS)
  └── Nginx: TLS, Login-Limit
        └── FastAPI / Uvicorn (localhost)
              ├── Öffentliche Website und JSON-GET-API
              ├── Portal: Login, Sessions, CSRF, Rollenprüfung
              ├── Portal: Einrichtungszuordnung / Freigaben
              └── PostgreSQL app_db (nicht öffentlich)
                   ├── hilfestelle, kategorie, notfallnummer, ...
                   ├── portal_account, portal_session
                   ├── portal_facility_assignment
                   ├── portal_facility_change
                   ├── portal_facility_audit
                   └── portal_public_location_type
```

Datenbankport `5432`, lokaler API-Port `8000` und Nginx-Testport `8080` dürfen nicht offen veröffentlicht werden. Die Portal-Links richten sich nach der Rolle, die **eigentliche Zugriffskontrolle erfolgt aber im Backend**, auch bei direkt aufgerufenen IDs.

## 3. Anmeldung und Autorisierung

- Passwörter werden mit Argon2 (`pwdlib`) gehasht. Keine Klartextpasswörter im Repository.
- Ein zufälliger Session-Token wird im Cookie über HTTPS transportiert; in PostgreSQL steht nur sein SHA-256-Hash. Session-Lebensdauer ca. 30 Minuten.
- `SessionMiddleware` nutzt signierte Cookies mit `Secure` und `SameSite=Strict`.
- Login, Logout und zustandsändernde Formulare prüfen CSRF-Tokens. Mehrere Fehlversuche lösen eine zeitweilige Kontosperre aus; Nginx begrenzt Login-POSTs zusätzlich.
- `admin` entspricht dem YANA-Team. `partner` entspricht einer externen Organisation. Partner dürfen nur in `portal_facility_assignment` zugewiesene Einrichtungen sehen und zugehörige Änderungen einreichen.
- Neue Hilfestellen und Statuswechsel werden mit `portal_facility_audit` protokolliert. Eingereichte Änderungen veröffentlichter Kontaktfelder werden ausschließlich von Administratoren freigegeben oder zurückgewiesen.
- Der Administrator kann Partnerkonten erstellen, deaktivieren, reaktivieren und Passwörter zurücksetzen. Startpasswörter werden einmalig gezeigt und müssen vor Nutzung der geschützten Portalbereiche geändert werden. Der Account-Lebenszyklus besitzt noch **kein eigenständiges Audit-Protokoll**.

Ein Simulations-/Browser- und End-to-End-Test der Rollen und Freigaben wurde durchgeführt. Eine unabhängige Sicherheitsprüfung, ein vollständiger Penetrationstest und eine Prüfung unter realen Angriffsszenarien stehen noch aus.

## 4. Zentrales Datenschutzrisiko: öffentliche Standortdaten

Der Endpunkt `/hilfestellen` ist **ohne Portal-Login** erreichbar. Inzwischen schützt er drei sensible Felder über eine **zweistufige Freigabe**: Nur `published`-Hilfestellen erscheinen überhaupt; `address`, `latitude` und `longitude` enthalten nur dann Werte, wenn `is_location_public=TRUE` **und** `facility_type` in der Positivliste steht. Ohne diese Bedingungen liefert die API `null`.

Die Positivliste enthält im bestätigten Stand ausschließlich **`Beratungsstelle`**. Schutzunterkünfte sind nicht zugelassen. Die gesonderte Administratorseite `/portal/standorte` steuert die Einzelgenehmigung; bei Änderung von Art, Adresse oder Koordinaten widerruft ein PostgreSQL-Trigger eine bisherige Freigabe. Mit fiktiven Daten wurde sowohl die Freigabe als auch die Rücknahme bis zur API-Antwort geprüft.

**Weiterhin offen für den Realbetrieb** sind:

1. Andere sensible Felder (z. B. **Name, Telefon, E-Mail, Öffnungszeiten, Kapazität**) fachlich klassifizieren; auch diese können Rückschlüsse auf Schutzstandorte zulassen.
2. Falsche Einrichtungsklassifizierung verhindern, öffentliche Adressen mit der Organisation verifizieren und Veröffentlichungsberechtigungen dokumentieren.
3. **Externe Geocoding-Anfragen** nur für öffentliche, nicht vertrauliche Adressen zulassen. Für Schutzunterkünfte keine automatische Übermittlung an Drittanbieter.
4. Datenschutz-/Aufbewahrungskonzept für Kontakte, Audit, mögliche Chatdaten und Backups; unabhängige Sicherheitstests.

Die neuen Filter sind deshalb **kein Freibrief für echte Schutzunterkunftsdaten**. Siehe [Standortdatenschutz](standort-datenschutz.md) und [Geocoding](geocoding.md).

## 5. Entwicklungs- und Testdaten

`~/yana-portal-test` und `~/yana-backend` sind getrennte **Codeverzeichnisse**, verwenden aber dieselbe PostgreSQL-Datenbank `app_db`. Ein Schreibtest im Testordner kann produktiv sichtbare Datensätze ändern. Deshalb wurden fiktive Testeinträge verwendet und die ursprüngliche Telefonnummer nach dem E2E-Test wiederhergestellt.

Eine separate Staging-Datenbank, automatisierte Test-Rollbacks und reproduzierbare Migrationen sind noch offen.

## 6. Secrets, Repository und Dateirechte

**Niemals in GitHub oder öffentliches MkDocs übernehmen:** `.env`, `PORTAL_SESSION_SECRET`, DB-Passwort, Klartextpasswörter, Session-Cookies, Private Keys, personenbezogene Datensätze und geheime Schutzstandorte.

Der Geoapify-Schlüssel `GEOAPIFY_API_KEY` gehört ebenfalls **nur in die geschützte VPS-Konfiguration**, nicht in GitHub. Seine produktive Einbindung in den laufenden Dienst ist am Checkpoint noch nicht bestätigt. Die produktive `.env` bleibt auf dem VPS; `.gitignore` umfasst `.env`, `.venv`, `__pycache__` und `*.pyc`. Eine `.gitignore` entfernt keine früher in Git veröffentlichten Geheimnisse; in einem solchen Fall Zugänge rotieren und Git-Historie gesondert behandeln.

## 7. Betriebsdiagnose

```bash
sudo systemctl status yana-api --no-pager
sudo journalctl -u yana-api -n 40 --no-pager
sudo nginx -t
pg_lsclusters
curl -i https://SERVER_IP/health
```

`journalctl` ist lesend; Logausgaben vor dem Teilen auf E-Mail-Adressen, IPs, Tokens und andere sensitive Informationen prüfen.

## 8. Backups und Wiederherstellung

Der registrierte IONOS/Acronis-Agent ist kein Beleg für einen erfolgreichen Datenbank-Restore. Vor größeren Datenbankmigrationen wurde zusätzlich manuell mit `pg_dump -Fc` gesichert. Code-Backups mit `tar` schützen dagegen nicht die Datenbank. Für echten Betrieb fehlen definierte Sicherungsintervalle, Aufbewahrung und mindestens ein überprüfter Restore.

## 9. Priorisierte nächste Schritte

- **Account-Audit** und sicherer manueller Übergabeprozess für generierte Startpasswörter; MFA für echte Partner prüfen.
- Bestehenden Standortfilter auf weitere sensible öffentliche Felder ausweiten und fachliche Freigabe für reale Hilfestellen prüfen.
- Getrennte Testdatenbank und automatisierte Regressionstests mit nichtproduktiven Daten.
- Monitoring, Log-/Audit-Aufbewahrung, MFA (Admin-Passwort-Reset ist vorhanden) und überprüfte Backup-Wiederherstellung.

Siehe [Änderungsvorschläge](teamportal-aenderungsfreigabe.md), [Portal-Datenbank](teamportal-datenbank.md) und [Weiterarbeit](weiterarbeit.md).
