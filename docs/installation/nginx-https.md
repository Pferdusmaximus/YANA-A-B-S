# Nginx, HTTPS und automatische Zertifikatserneuerung

**Umgesetzt und getestet bis Schritt 22.3.** Nginx leitet öffentliche HTTPS-Anfragen an FastAPI auf `127.0.0.1:8000` weiter. Das PostgreSQL-Port `5432` und das Uvicorn-Port `8000` werden nicht öffentlich benötigt.

## 1. Nginx installieren

```bash
sudo apt update
sudo apt install nginx -y
sudo systemctl enable --now nginx
sudo systemctl status nginx
```

Ein lokaler Aufruf von `http://127.0.0.1` zeigte die Nginx-Startseite. Die Versionsangabe in einem späteren HTTP-Fehler war `nginx/1.24.0 (Ubuntu)`.

## 2. Lokalen Reverse Proxy einrichten

Datei `/etc/nginx/sites-available/yana-api` erzeugen:

```bash
sudo nano /etc/nginx/sites-available/yana-api
```

Zunächst wurde ausschließlich ein lokaler Listener für `127.0.0.1:8080` eingerichtet:

```nginx
server {
    listen 127.0.0.1:8080;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Die Datei aktivieren:

```bash
sudo ln -s /etc/nginx/sites-available/yana-api /etc/nginx/sites-enabled/yana-api
sudo nginx -t
sudo systemctl reload nginx
```

**Test:** `http://127.0.0.1:8080/docs` rief die Swagger-Dokumentation auf, und `GET /hilfestellen` lieferte die Testeinträge. Das bewies die Proxy-Kette **Nginx → FastAPI → PostgreSQL**.

> Falls `nano` `Error writing ... No such file or directory` meldet, Pfad und Verzeichnis mit `ls -ld /etc/nginx/sites-available` prüfen und die Datei mit `sudo nano` öffnen. Das Verzeichnis war im Projekt vorhanden; ein erneuter Aufruf mit korrektem Pfad funktionierte.

## 3. Netzfreigaben bewusst begrenzen

| Protokoll/Port | Nutzung | Externe Freigabe |
|---|---|---|
| TCP 80 | Let's-Encrypt-HTTP-Validierung | Ja |
| TCP 443 | Öffentlicher HTTPS-Endpunkt | Ja |
| TCP 22 | SSH-Administration | Nur zugelassene Admin-IP(s), sofern benötigt |
| TCP 8000 | Uvicorn/FastAPI | **Nein**, Loopback |
| TCP 8080 | Lokaler Nginx-Test | **Nein**, Loopback |
| TCP 5432 | PostgreSQL | **Nein**, Loopback |

Die Regeln wurden im IONOS Cloud Panel unter **Netzwerk → Firewall-Richtlinien** geprüft bzw. ergänzt. Optional lokalen UFW-Status kontrollieren:

```bash
sudo ufw status
```

Nur falls UFW aktiv ist, die erforderlichen Webports erlauben:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

Beim Aktivieren einer Host-Firewall zuvor SSH-Zugang absichern; die IONOS-Browser-Konsole als Notfallzugang verfügbar halten.

## 4. HTTP-01-Validierung (Webroot) einrichten

Verzeichnis für die ACME-Challenge:

```bash
sudo mkdir -p /var/www/yana-acme/.well-known/acme-challenge
```

Datei `/etc/nginx/sites-available/yana-acme`:

```nginx
server {
    listen 80 default_server;
    server_name _;

    root /var/www/yana-acme;

    location ^~ /.well-known/acme-challenge/ {
        try_files $uri =404;
    }

    location / {
        return 404;
    }
}
```

Die zuvor aktive Standardwebsite wurde deaktiviert und die neue Konfiguration verlinkt:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/yana-acme /etc/nginx/sites-enabled/yana-acme
sudo nginx -t
sudo systemctl reload nginx
```

Verifikation:

```bash
echo "YANA-ACME-OK" | sudo tee /var/www/yana-acme/.well-known/acme-challenge/test.txt
curl -i http://127.0.0.1/.well-known/acme-challenge/test.txt
```

Von einem **externen Netz** (Mobilfunk-Hotspot) wurde `http://SERVER_IP/.well-known/acme-challenge/test.txt` aufgerufen. Ergebnis: `YANA-ACME-OK`. Ein anfänglicher `404 Not Found` wurde durch Korrektur des aufgerufenen Pfads behoben. Die Wurzeladresse `http://SERVER_IP/` liefert **absichtlich 404**, weil der ACME-Server nur die Challenge-Dateien ausliefern soll.

## 5. Certbot installieren

```bash
sudo apt update
sudo apt install snapd -y
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/local/bin/certbot
/snap/bin/certbot --version
```

Falls der Symlink bereits besteht, keinen zweiten erzwingen. Für IP-Zertifikate per Webroot wurde **Certbot 5.4 oder neuer** verwendet.

**Hintergrund:** Let's Encrypt stellt seit 2026 öffentlich vertrauenswürdige IP-Zertifikate aus; sie verwenden das Profil `shortlived` und sind **160 Stunden** gültig. Die Erneuerung muss daher zuverlässig automatisiert werden.

## 6. Zertifikat für öffentliche IP ausstellen

Zunächst wurde ein **Staging-Testzertifikat** angefordert:

```bash
sudo /snap/bin/certbot certonly \
  --staging \
  --preferred-profile shortlived \
  --webroot \
  --webroot-path /var/www/yana-acme \
  --ip-address SERVER_IP
```

Danach sollte ein produktives Zertifikat ausgestellt werden. Im tatsächlichen Projektverlauf war zunächst **noch das Staging-Zertifikat aktiv**, obwohl HTTPS technisch antwortete; `curl` meldete `unable to get local issuer certificate`, und `openssl` zeigte beim Aussteller `(STAGING)`.

Das Testzertifikat wurde erfolgreich durch das Produktionszertifikat ersetzt:

```bash
sudo /snap/bin/certbot certonly \
  --cert-name SERVER_IP \
  --force-renewal \
  --server https://acme-v02.api.letsencrypt.org/directory \
  --preferred-profile shortlived \
  --webroot \
  --webroot-path /var/www/yana-acme \
  --ip-address SERVER_IP
```

**Wichtig:** `--force-renewal` war eine **einmalige Reparatur** des bestehenden Staging-Zertifikats. Für eine frische Installation ohne bestehenden Certbot-Eintrag ist eine reguläre produktive Ausstellung **ohne** `--staging`, `--cert-name` und `--force-renewal` üblich. Die normale spätere Erneuerung übernimmt `certbot renew`.

Zertifikat verifizieren (Pfade auf tatsächlich gemeldeten Namen abstimmen):

```bash
sudo /snap/bin/certbot certificates
sudo openssl x509 \
  -in /etc/letsencrypt/live/SERVER_IP/fullchain.pem \
  -noout -issuer -dates -ext subjectAltName
```

Der Eintrag `Identifiers` beziehungsweise die `Subject Alternative Name` muss die richtige öffentliche IP-Adresse enthalten, und beim `issuer` darf **kein** `(STAGING)` erscheinen. Die privaten Schlüssel (`privkey.pem`) **niemals veröffentlichen**.

## 7. HTTPS in Nginx aktivieren

Die zuvor erstellte Datei `/etc/nginx/sites-available/yana-api` wurde **um einen öffentlichen HTTPS-Block ergänzt**. Die fertige, dokumentierte Konfiguration lautet:

```nginx
# Lokaler Testzugriff
server {
    listen 127.0.0.1:8080;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Öffentliche API über HTTPS
server {
    listen 443 ssl;
    server_name SERVER_IP;

    ssl_certificate /etc/letsencrypt/live/SERVER_IP/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/SERVER_IP/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

In dieser **Vorlage** ist `SERVER_IP` vor dem Einsatz an allen Stellen durch die tatsächliche IP-Adresse zu ersetzen. Die Zertifikatsdateien müssen bereits existieren; andernfalls schlägt `nginx -t` fehl. Der HTTP-ACME-Block bleibt in **`yana-acme`** erhalten.

Aktivieren und testen:

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -Iv https://SERVER_IP/docs
```

**Bestätigter Ist-Stand:** Swagger war von einem Smartphone aus über HTTPS erreichbar. Nach dem Ersatz des Testzertifikats zeigte Firefox eine **sichere Verbindung ohne Warnung**.

## 8. Automatische Zertifikatserneuerung – Schritt 22.1–22.3

Da IP-Zertifikate kurzlebig sind, wurde der Snap-Certbot-Timer überprüft:

```bash
sudo systemctl list-timers --all | grep certbot
sudo systemctl status snap.certbot.renew.timer
```

**Bestätigt:** `snap.certbot.renew.timer` mit `Active: active (waiting)`.

Nach erfolgreicher Erneuerung muss Nginx das Zertifikat neu laden. Dazu wurde ein Deploy Hook angelegt:

```bash
sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy
sudo nano /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

Dateiinhalt:

```sh
#!/bin/sh
set -e
/usr/sbin/nginx -t
/bin/systemctl reload nginx
```

```bash
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

Anschließend wurde ein Dry-Run **inklusive Ausführung des Deploy Hooks** durchgeführt:

```bash
sudo /snap/bin/certbot renew --dry-run --run-deploy-hooks
```

**Bestätigtes Ergebnis:** Timerprüfung, Skripteinrichtung und der Erneuerungstest waren erfolgreich (Benutzerrückmeldung). Die Erneuerung ist damit für den aktuellen Stand konfiguriert; die tatsächlichen zukünftigen Ausführungen sollten im Betrieb überwacht werden.

### Kontrolle bei Fehlern

```bash
sudo systemctl status snap.certbot.renew.timer
sudo journalctl -u snap.certbot.renew.service -n 100 --no-pager
sudo /snap/bin/certbot certificates
sudo nginx -t
curl -Iv https://SERVER_IP/docs
```

## 9. Grenzen des Ist-Zustands

- **Swagger `/docs` ist noch öffentlich zugänglich**; für den Produktivbetrieb sollte die Dokumentationsoberfläche geschützt oder deaktiviert werden.
- Die drei Daten-Endpunkte verfügen derzeit **über keine Authentifizierung**, API-Drosselung oder datenspezifische Zugriffskontrolle.
- Für echte Beratungs-/Chatdaten sind Rollen, Zugriffsschutz, Logging-Reduktion und Datenschutzkonzept erforderlich.
- Die Verbindung über eine IP-Adresse ist derzeit bewusst ein **Entwicklungssetup ohne eigene Domain**.

Weiter zu [Betrieb und Sicherheit](../technik/betrieb-sicherheit.md) und [API-Referenz](../technik/api-referenz.md).
