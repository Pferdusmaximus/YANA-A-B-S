# Betrieb, Sicherheit und Datenschutz

## Ist-Zustand zum 20.10.2026

| Prüfaspekt | Status | Nachweis / Bemerkung |
|---|---|---|
| Ubuntu 24.04 + GNOME | **Bestätigt** | Grafische IONOS-Konsole funktionsfähig |
| IONOS Backup-Agent | **Bestätigt** | Erfolgreich installiert und in Backup-Konsole sichtbar |
| Vollständiges Backup abgeschlossen | **Nicht bestätigt** | Schutzplan, Abschlussprotokoll und Restore-Test gesondert prüfen |
| PostgreSQL `app_db` | **Bestätigt** | Cluster online, lokale Verbindung erfolgreich |
| 8 Tabellen | **Bestätigt** | Schema in pgAdmin angelegt |
| Beispiel-Hilfestellen | **Bestätigt** | Zwei fiktive Datensätze angelegt |
| FastAPI-API | **Bestätigt** | GET-Endpunkte getestet, HTTP 200 |
| systemd-Dienst `yana-api` | **Bestätigt** | `active (running)`, Browserprüfung erfolgreich |
| Nginx lokal und öffentlich | **Bestätigt** | `127.0.0.1:8080` sowie HTTPS-Port 443 |
| HTTPS-Zertifikat | **Bestätigt** | Staging-Zertifikat ersetzt, Firefox meldete sichere Verbindung |
| Erneuerung mit Certbot | **Bestätigt (Test)** | Timer und `renew --dry-run --run-deploy-hooks` erfolgreich |
| Flutter-App per API verbunden | **Noch nicht** | Nächster Entwicklungsschritt |
| Authentifizierte API für sensible Daten | **Noch nicht** | Darf vor produktiven Chatdaten nicht fehlen |

## Sicherheitskonzept des aktuellen Testbetriebs

Die DB ist lokal an FastAPI angebunden. Nginx ist der einzige beabsichtigte öffentliche Web-Zugang.

```text
Internet → TCP 443 / Nginx → 127.0.0.1:8000 / FastAPI
                                   → 127.0.0.1:5432 / PostgreSQL
```

**Nicht öffentlich freigeben:** DB-Port `5432`, FastAPI-Port `8000`, interner Nginx-Testport `8080`. Der Port `80` ist nur für die ACME-Validierung erreichbar; die HTTP-Startseite liefert 404.

Die aktuelle Datenbankbenutzerrolle `app_user` ist Eigentümer von `app_db`. Für den späteren Livebetrieb sollte ein Konto mit minimal benötigten Berechtigungen für die API eingeführt werden; Migrationen und Administration sollten von einer separaten Rolle ausgeführt werden.

## Umgang mit Geheimnissen

- Datenbankpasswort **nur** in lokaler Datei `~/yana-backend/.env`, Zugriffsrecht `chmod 600`.
- `.env`, Zertifikats-Private-Key (`privkey.pem`), Zugangsdaten, Token und Backup-Zugänge **niemals** in GitHub committen.
- Dokumentationsbeispiele verwenden ausschließlich Dummy-Werte wie `PASSWORT_NUR_LOKAL_EINSETZEN` und `SERVER_IP`.
- Das Vorhandensein einer öffentlichen Server-IP ist nicht gleichbedeutend mit einer geheimen Zugangsinformation; dennoch wird die konkrete IP hier bewusst nicht in den öffentlichen Text übernommen.
- Wenn versehentlich ein Passwort ins Repository gelangt: sofort ändern/rotieren und Git-Historie bzw. veröffentlichte Artefakte kontrollieren.

## Relevante Betriebsbefehle

| Aufgabe | Befehl |
|---|---|
| Backend-Status | `sudo systemctl status yana-api` |
| Backend neu starten | `sudo systemctl restart yana-api` |
| Backend-Logs | `sudo journalctl -u yana-api -n 100 --no-pager` |
| Nginx prüfen | `sudo nginx -t` |
| Nginx neu laden | `sudo systemctl reload nginx` |
| PostgreSQL-Cluster | `pg_lsclusters` |
| Zertifikate prüfen | `sudo /snap/bin/certbot certificates` |
| Certbot-Timer | `sudo systemctl status snap.certbot.renew.timer` |
| Letzte Erneuerungsaktivität | `sudo journalctl -u snap.certbot.renew.service -n 100 --no-pager` |

**Datenschutz:** Logs dürfen keine Chat-Inhalte, Klarnamen, Standortverläufe, Zugangstokens oder andere unnötige personenbezogene Informationen enthalten. Standard-Access-Logs können Client-IP-Adressen enthalten und müssen im Projekt datenschutzrechtlich berücksichtigt werden.

## Backups und Wiederherstellung

Die Anmeldung des Servers in der IONOS Backup-Konsole wurde überprüft. Für den produktiven Betrieb sind ergänzend zu dokumentieren:

1. Schutzziel/Backup-Typ (vollständige Maschine vs. einzelne Daten).
2. Zeitplan, Aufbewahrungsdauer, Backup-Speicherort und Verantwortliche.
3. Datum und Ergebnis eines **erfolgreichen** Sicherungslaufs.
4. Dokumentierter Restore-Test, inklusive Konsistenzprüfung von PostgreSQL.
5. Optional konsistente, getrennte `pg_dump`-Sicherungen (sicher verwahrt, nicht im öffentlichen Repository).

Beispiel einer **lokalen** logischen Sicherung (Pfad/Berechtigungen und Speicherstrategie vor der Nutzung festlegen):

```bash
# Empfehlung / nicht als bereits ausgeführt bestätigen
sudo -u postgres pg_dump -Fc app_db > app_db.backup
```

Backups mit realen Daten gehören **nicht** in GitHub. Eine Sicherungsdatei ersetzt keine getestete Wiederherstellung.

## Notwendige Arbeiten vor der Nutzung mit echten Betroffenen

- **Authentifizierung und Autorisierung:** Endpunkte nach Rollen absichern; keine fremden Chats abrufbar machen.
- **Anonyme Beratung:** Datensparsamkeit, Pseudonymisierung, sichere Session-IDs, Aufbewahrungs-/Löschkonzept.
- **Sicherheitsprüfung:** API-Eingaben validieren, Rate Limiting, Dependency-Updates, Fehler- und Log-Behandlung, regelmäßige Schwachstellenprüfung.
- **Schutzstandorte:** Vertrauliche Adressen von Schutzunterkünften nicht unkontrolliert als vollständige Standortdaten veröffentlichen.
- **Echte Notfallkontakte:** Aktualität, Zuständigkeit, Öffnungszeiten und Erreichbarkeit fachlich verifizieren; Offline-/Fehler-Fallback in der App vorsehen.
- **Datenschutz:** Verzeichnis der Datenverarbeitungen, Rechtsgrundlage, Löschfristen und ggf. Datenschutz-Folgenabschätzung prüfen.
- **Betrieb:** Monitoring, Kapazitätsmessung, Alerting bei TLS- und Backup-Fehlern.
- **Dokumentationsoberfläche:** Öffentlichen Zugriff auf Swagger `/docs` vor einem echten Produktivbetrieb gesondert bewerten, ggf. deaktivieren oder absichern.

> **Kritische Abgrenzung:** Das aktuelle System ist ein technischer Prototyp mit simulierten Einträgen; noch keine verlässlich nutzbare Sicherheits- oder Beratungsanwendung.
