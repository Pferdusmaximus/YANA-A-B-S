# Betrieb, Sicherheit und Datenschutz

**Dokumentationsstand: 17. November 2026.** YANA ist ein technisch funktionierender **Entwicklungsprototyp** mit öffentlicher Website und internem Verwaltungsportal. Die bislang vorgenommenen Prüfungen reichen **nicht** für die sichere Verarbeitung realer Hilfesuchenden-, Chat- oder geheimer Standortdaten aus.

## 1. Bestätigter Betriebsstand

| Bereich | Ergebnis / offene Grenze |
|---|---|
| Ubuntu 24.04 LTS, grafische IONOS-Konsole | Eingerichtet und erreichbar |
| PostgreSQL 16 `app_db` | Ursprünglich acht Tabellen, jetzt drei zusätzliche Portal-Tabellen |
| FastAPI/Uvicorn und systemd `yana-api` | Produktiv aktiv; wiederholt neu gestartet und geprüft |
| Nginx und HTTPS | Öffentliche Website und API erreichbar |
| Let's Encrypt / Certbot | Produktives Zertifikat und Erneuerungs-Dry-Run bestätigt |
| Backup-Agent | Installiert/registriert; **vollständig erfolgreicher Restore-Test offen** |
| Flutter API | Drei GET-Endpunkte über Dart-CLI getestet |
| Flutter Web / CORS | Lokale Browser-Origin-Freigabe eingerichtet |
| Öffentliche Website | Produktiv im Browser aufgerufen |
| Teamportal-Anmeldung | Argon2, Session, Logout, CSRF und Browser-Smoke-Test erfolgreich |
| Teamportal-Hilfestellen | Übersicht/Bearbeiten/Speichern/Audit produktiv getestet |
| Nginx-Login-Limit | Konfiguration syntaktisch geprüft, Nginx neu geladen, Website/API weiter verfügbar; **Lasttest des Limits nicht bestätigt** |
| Echte externe Organisationsaccounts | **Nicht freigeschaltet** |
| Echte verifizierte Hilfs-/Schutzstandorte | **Nicht sicher freigegeben** |

## 2. Vertrauensgrenzen

```text
Internet
  └── Port 443 / Nginx (HTTPS, Login-Rate-Limit)
        └── FastAPI / Uvicorn (127.0.0.1:8000)
              └── PostgreSQL (lokal, nicht öffentlich)
                   ├── hilfestelle / kategorie / notfallnummer / ...
                   ├── portal_account
                   ├── portal_session
                   └── portal_facility_audit
```

Port `5432` (Datenbank), Uvicorn-Port `8000` und ggf. der lokale Nginx-Testport `8080` sollten nicht öffentlich erreichbar sein. Das Teamportal prüft **serverseitig** Session und Rolle; ein ausgeblendeter Browser-Link ersetzt keine Autorisierung.

## 3. Anmeldung und Sessions

Für interne Portalaccounts wurde folgendes implementiert:

- Hashing und Prüfung der Passwörter mit **Argon2** (`pwdlib`).
- Eine zufällige Session-ID, die in `portal_session` nur als SHA-256-Hash gespeichert wird.
- Signiertes `SessionMiddleware`-Cookie (`HttpOnly`, `Secure`, `SameSite=Strict`) mit 30 Minuten `max_age`.
- Ein Formular-CSRF-Token mit serverseitiger Prüfung bei Login, Logout und Datenbearbeitung.
- Vorübergehende Account-Sperre nach mehrfachen falschen Passwörtern und eine getrennte Nginx-Begrenzung für Login-POSTs.
- Beim Bearbeiten eine Rollenprüfung für `admin`/`team`; die externe Rolle `facility` hat darauf **keinen** pauschalen Zugriff.

Login, Logout, ungültige CSRF-Tokens und die Bearbeitung wurden in den beschriebenen Basis-Szenarien getestet. Die Beurteilung umfasst **keinen** vollständigen Sicherheits-/Penetrationstest und keine Prüfung der Privilegieneskalation unter realistischen Angriffsszenarien. Die genaue Implementierung steht unter [Login und Sicherheit](teamportal-login.md).

## 4. Zugangsdaten und Quellcode

**Nicht veröffentlichen:** `.env`, `PORTAL_SESSION_SECRET`, Datenbankpasswort, TLS-Private-Keys, Backup-Zugangsdaten, Login-Passwörter, Session-Cookies, reale Kontakt-/Standortdaten aus Datenbankexports.

Die produktive `.env` liegt lokal im Backendverzeichnis auf dem VPS, nicht im GitHub-Repository. `chmod 600 .env` wurde als Dateirecht gesetzt. Der GitHub-Root besitzt inzwischen eine `.gitignore` für `__pycache__`, `*.pyc`, `.venv` und `.env`. Schon früher versehentlich versionierte Cache-Dateien wurden entfernt. **Eine `.gitignore` löscht keine Geheimnisse aus früheren Commits.** Wurden Zugangsdaten veröffentlicht, sind sie umgehend zu rotieren.

## 5. Datenpflege, Audit und Schutzstandorte

Die Hilfestellenverwaltung unterstützt derzeit das Ändern von `name`, `phone`, `email` und `opening_hours`. Die SQL-Änderung und der Audit-Eintrag sind transaktional verbunden; durch das Audit wird dokumentiert, **welcher Portalaccount wann welche Werte geändert hat**. Die Audit-JSON-Felder können personenbezogene Kontaktdaten enthalten und benötigen Zugriffs- und Aufbewahrungsregeln.

**Zentrales Sicherheitsproblem:** Die öffentliche JSON-API `/hilfestellen` enthält in der bisherigen Struktur **Adresse sowie Breiten- und Längengrad**. Sobald eine echte Schutzunterkunft eingetragen würde, könnten vertrauliche Standorte ungewollt veröffentlicht werden – unabhängig davon, ob das Portal hinter einem Login liegt. Deshalb:

1. Bis zur Lösung weiterhin **nur fiktive Daten** verwenden.
2. Öffentliche und interne Felder ausdrücklich trennen, z. B. durch sichere API-Projektionen und Veröffentlichungsstatus.
3. Für vertrauliche Einrichtungen keinen exakten Standort in öffentlichen Antworten ausgeben.
4. Externe Änderungen zuerst prüfen/freigeben, statt sie sofort in der öffentlichen API erscheinen zu lassen.
5. Mitarbeiterkonten nur konkreten Einrichtungen zuordnen und sämtliche Lese-/Schreibrechte serverseitig erzwingen.

Noch **nicht umgesetzt**: „Neue Hilfestelle anlegen“, gesonderte Organisationszuordnung, Moderation/Freigabe, differenzierte Schutzstandortveröffentlichung und Bearbeiten von Adressen/Koordinaten.

## 6. Testumgebung und Datensicherheit

Es gibt die voneinander getrennten **Codeverzeichnisse** `~/yana-portal-test` und `~/yana-backend`. Die Testumgebung wurde jedoch mit derselben `.env` und **derselben PostgreSQL-Datenbank** betrieben. Ein Test unter `~/yana-portal-test` ist damit **kein** isolierter Datenbanktest und kann produktive Datensätze verändern.

Die erfolgreichen Speichertests verwendeten ausdrücklich fiktive Einträge, einen temporären Telefonnummernwert und anschließend die Wiederherstellung. Eine automatische Wiederherstellung im Skript ist kein vollwertiger DB-Rollback bei Absturz. Zukünftig sind separate Testdatenbank, Migrationen und transaktionale Testisolation vorzusehen.

## 7. Betriebsdiagnose

```bash
# Status / Protokolle
sudo systemctl status yana-api --no-pager
sudo journalctl -u yana-api -n 40 --no-pager

# Reverse Proxy / Rate-Limit
sudo nginx -t
sudo systemctl status nginx --no-pager

# PostgreSQL
pg_lsclusters

# Certbot / TLS
sudo /snap/bin/certbot certificates
sudo systemctl status snap.certbot.renew.timer

# Test des öffentlichen REST-Zugangs
curl -i https://SERVER_IP/health
```

**`journalctl` ist rein lesend** und verändert nichts am Dienst. Logs können IP-Adressen und andere sensible Informationen enthalten: Vor dem Teilen bereinigen. Das Aktivieren eines gefährlichen `curl -k` zum Umgehen der Zertifikatsprüfung ist nicht empfohlen.

## 8. Backups und Wiederherstellung

Der Acronis-/IONOS-Agent wurde installiert und in der Backup-Konsole registriert; dies ist **kein Nachweis** für erfolgreich abgeschlossene Sicherungen und Restores. Vor realem Betrieb müssen Sicherungsplan, Aufbewahrung, Verantwortlichkeiten und mindestens ein erfolgreicher Wiederherstellungstest nachgewiesen werden.

Für Code-Deployments wurden manuelle Tar-Backups des produktiven Backends ohne `.env` und `.venv` angelegt. Diese Backups schützen **nicht** vor Datenbankverlust und ersetzen keine konsistenten PostgreSQL-Sicherungen.

Eine mögliche zusätzliche **Empfehlung**, nicht als bereits erledigt dokumentiert:

```bash
# Sicherung muss an einem geschützten Ziel mit korrekten Dateirechten erfolgen
sudo -u postgres pg_dump -Fc app_db > app_db.backup
```

Eine produktive Datenbank-Backup-Datei gehört nicht in GitHub oder öffentlich zugängliche Downloads.

## 9. Vor echtem Einsatz noch erforderlich

- Rechtliche und organisatorische Datenschutzprüfung, Lösch- und Aufbewahrungsfristen, potenziell Datenschutz-Folgenabschätzung.
- Geheimhaltung vertraulicher Schutzstandorte; Review öffentlicher API-Antworten.
- Belastbare externe Rollen/Organisationstrennung, mindestens ein Freigabe-Workflow für neue/geänderte Einträge.
- Verifizierte Hilfskontakte statt Testdaten; sichere Offline-/Fehlerbehandlung in der mobilen App.
- Getrennte Staging-/Produktionsdatenbanken und reproduzierbare SQL-Migrationen.
- Weitere Sicherheits-/Integrationstests, Rate-Limit-Lasttest, Dependency-Updates, Secrets-Rotation, Monitoring und Alarmierung.
- Eignung der Swagger-`/docs`-Veröffentlichung überprüfen.
- Sicherungs- und Restore-Test mit konsistenter PostgreSQL-Wiederherstellung.

**Zusammenfassung:** Das interne Teamportal ist funktional, **nicht** als vollumfänglich sichere Lösung für echte sensible Personendaten freigegeben. Der nächste Implementierungsschritt bleibt [„Neue Hilfestelle anlegen“](weiterarbeit.md).
