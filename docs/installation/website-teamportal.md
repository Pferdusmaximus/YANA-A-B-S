# Website und Teamportal einrichten (Entwicklungsablauf)

**Stand: 23. November 2026 · Das gemeinsame Verwaltungsportal wurde zusätzlich um Partner- und Passwortverwaltung erweitert.** Die Seite dokumentiert die Vorgehensweise zur Wiederholung auf einem neuen Server. Sie ist keine Aufforderung, SQL oder Installationsbefehle unüberprüft noch einmal auf dem laufenden Produktionsserver auszuführen.

## Voraussetzungen

- Funktionsfähiges Ubuntu 24.04, PostgreSQL 16 und `app_db` mit acht ursprünglichen Tabellen.
- `~/yana-backend` mit `.venv`, `database.py`, `main.py` und lokaler `.env`.
- Systemd-Dienst `yana-api`, Nginx-HTTPS-Proxy und gültiges TLS-Zertifikat.
- GitHub-Repository `YANA-A-B-S` mit `services/api/`.
- Zugriff auf Ubuntu über die **grafische IONOS-Konsole** und auf die Datenbank über pgAdmin 4.

## 1. Projektdateien

```text
services/api/
├── main.py
├── database.py
├── website.py
├── portal.py
├── portal_access.py
├── portal_facilities.py
├── portal_facilities_create.py
├── portal_facilities_status.py
├── portal_facility_changes.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── portal/
│       ├── login.html
│       ├── dashboard.html
│       ├── hilfestellen.html
│       ├── hilfestellen_bearbeiten.html
│       ├── hilfestellen_neu.html
│       ├── aenderung_bearbeiten.html
│       └── aenderungen_pruefen.html
└── static/css/style.css
```

**Kritische Schreibweise:** `hilfestellen_bearbeiten.html` im Plural. Nicht mit `hilfestelle_bearbeiten.html` verwechseln.

## 2. Python-Pakete

Die im Projekt verwendete virtuelle Umgebung wurde im Laufe des Setups um Folgendes erweitert:

```bash
cd ~/yana-backend
source .venv/bin/activate
python -m pip install jinja2 'pwdlib[argon2]' itsdangerous python-multipart python-dotenv httpx
```

`jinja2` dient dem Rendern der HTML-Dateien. `pwdlib[argon2]` prüft Passwort-Hashes, `itsdangerous` signiert Sessions, `python-multipart` liest Formulardaten, `python-dotenv` lädt Konfiguration, `httpx` wird für Tests benötigt. Vor einer Neuinstallation Versionen mit der installierten Umgebung abgleichen und dauerhaft eine `requirements.txt`/Lockdatei pflegen.

## 3. Datenbank und erster Admin

Für das Portal wurden `portal_account`, `portal_session`, `portal_facility_audit`, `portal_facility_assignment` und `portal_facility_change` ergänzend zu den acht Fach-Tabellen angelegt. Die neuere Variante des Schemas erlaubt nur `admin` und `partner`; die Migrationen dürfen nicht pauschal erneut auf der Produktivdatenbank ausgeführt werden. Vollständiges dokumentiertes Schema und GRANT-Befehle stehen auf [Portal-Datenbank](../technik/teamportal-datenbank.md).

Der erste Administrator wurde in pgAdmin mit `role='admin'` und einem vorab lokal erzeugten **Argon2-Hash** angelegt. Keinen Klartext in `INSERT`-Befehlen oder in Markdown/GitHub speichern. Vor dem Test prüfen:

```sql
SELECT account_id, role, is_active
FROM public.portal_account;
```

## 4. Session-Secret

In der **serverlokalen** `.env` wurde `PORTAL_SESSION_SECRET` als kryptografisch zufälliger Wert ergänzt. Das Python-Backend erwartet diesen Schlüssel beim Start. `.env` niemals aus GitHub ersetzen; Dateirechte auf dem VPS einschränken (`chmod 600 .env`). Die bereits eingerichtete `.env` bleibt bei späteren Deployments unangetastet.

## 5. FastAPI konfigurieren

In `main.py` werden die Website, `portal_router`, die Router für Hilfestellen, Neuaufnahme, Statusfreigabe, Änderungsvorschläge, Partnerverwaltung (`partners_router`) und Passwortwechsel (`password_router`) sowie `StaticFiles` eingebunden. Hinzu kommen `SessionMiddleware` (geschützte Cookie-Konfiguration) und eine lokale CORS-Freigabe für Flutter Web. **Nicht** den gesamten ursprünglichen API-Code löschen: Die GET-Endpunkte `/health`, `/hilfestellen`, `/kategorien`, `/notfallnummern` müssen erhalten bleiben.

Unter `/` wird inzwischen eine HTML-Seite statt der ursprünglichen JSON-Willkommensmeldung angezeigt. Routen und Schutzregeln stehen unter [API-Referenz](../technik/api-referenz.md).

## 6. Nginx-Loginbegrenzung

Im Projekt wurde die Datei `/etc/nginx/conf.d/yana-portal-limit.conf` erstellt, die Login-POSTs über Port 443 begrenzt. Nach der Einrichtung waren `sudo nginx -t`, `sudo systemctl reload nginx` und die öffentlichen Website-/API-Smoke-Tests erfolgreich. Beschreibung und Einschränkungen: [Login-Sicherheit](../technik/teamportal-login.md).

## 7. Test statt sofortigem Deployment

Code zuerst aus GitHub unter `~/yana-deploy-source` abrufen und in `~/yana-portal-test` prüfen. Für den ersten Login-Test wurde eine eigenständige Datei `login_test_local.py` angelegt; ein heredoc mit `python - <<'PY'` konnte `input()`/`getpass()` **nicht interaktiv** lesen (EOFError). Erst nach den erfolgreichen Tests wurde mit Backup in `~/yana-backend` kopiert und `yana-api` neu gestartet.

Das kopier- und testbare Vorgehen steht in [Deployment](../technik/teamportal-deployment.md), konkrete Ergebnisse in [Portal-Tests](../technik/teamportal-tests.md).

## 8. Betrieb prüfen

```bash
sudo systemctl status yana-api --no-pager
sudo nginx -t
curl -sS -o /dev/null -w '%{http_code}\n' https://SERVER_IP/
curl -sS -o /dev/null -w '%{http_code}\n' https://SERVER_IP/hilfestellen
```

Danach im Browser `/portal/login` und `/portal/hilfestellen` testen, Anmeldung und Abmeldung prüfen. Die externen Partnerberechtigungen und Freigaben sind inzwischen für fiktive Daten implementiert. Vor der Freigabe echter Daten fehlen insbesondere Datenschutzregeln für öffentliche Standortinformationen, ein eigenständiges Account-Audit, MFA und ein separates Testsystem. Die vereinfachte Admin-Accountverwaltung ist jetzt implementiert: [Partner- und Benutzerverwaltung](../technik/teamportal-benutzerverwaltung.md).
