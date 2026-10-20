# Fehlerbehebung und tatsächlich aufgetretene Probleme

Diese Seite protokolliert die wesentlichen Probleme aus dem bisherigen YANA-Serveraufbau, ihren Kontext und die tatsächlich wirksame Lösung. Sie erleichtert eine spätere Reproduktion und verhindert die Wiederholung derselben Fehler.

| Situation | Beobachtung | Diagnose/Lösung |
|---|---|---|
| Erster Backup-Installationsversuch ohne `sudo` | `/var/lib/apt/... Permission denied`, `You should run this program as root` | Installer mit `sudo ./backup-agent-installer-Europe-Linux.sh` starten. |
| Backup-Agent unter Ubuntu 26.04.1 | `dkms-3.10.16.1-99.noarch does not verify: no digest`, keine bestätigte Registrierung | Neuinstallation auf Ubuntu 24.04 und erneuter Installationslauf waren erfolgreich. Ursache des ursprünglichen Prüffehlers nicht endgültig bestätigt. |
| `acronis_mms` nicht gefunden | `service not found` | Keine pauschale Dienstbezeichnung unterstellen; Pakete, Installationsprotokoll und erkannte Dienste prüfen. |
| IONOS-Browser-Konsole nach Neuinstallation | `Something went wrong, connection is closed` | Nach erneuter Neuinstallation war der Konsolenzugriff wieder möglich. Ein eindeutiger technischer Grund wurde nicht festgestellt. |
| GNOME-Nutzung über IONOS-Konsole | Zunächst nur Terminal | `ubuntu-desktop-minimal`, `graphical.target`, `gdm3` installiert/aktiviert; Oberfläche war über IONOS-Konsole sichtbar. Kein XRDP erforderlich. |
| Acronis-Installation meldet Kernelmodul | `The UTF8 kernel module is missing` | Installation lief dennoch weiter und endete mit `Cyber Protection Agent has been successfully installed in the system`. Meldung im Ergebnis nicht blockierend. |
| Nginx-Datei nicht speicherbar | `Error writing ... No such file or directory` | `/etc/nginx/sites-available` existierte. Korrekte Pfadangabe und `sudo nano ...` ermöglichten das Speichern. |
| ACME-Test via öffentlicher IP | `404 Not Found nginx/1.24.0` | Root-Pfad liefert beabsichtigt 404; vollständige URL `/.well-known/acme-challenge/test.txt` verwenden. Danach `YANA-ACME-OK` sichtbar. |
| HTTPS auf Smartphone als unsicher markiert | Swagger erreichbar, Firefox vertraute Zertifikat nicht | `curl -Iv` meldete `unable to get local issuer certificate`; `openssl` zeigte `(STAGING)` beim Issuer. Staging-Zertifikat durch Produktionszertifikat ersetzt, Nginx neu geladen; danach Firefox „sichere Verbindung“. |
| Zugriff aus Schulnetzwerk | Fortinet-Firewall verhinderte Test | Externen Zugriff über Mobilfunk-Hotspot getestet; Server war darüber erreichbar. Schulnetzrichtlinien nicht umgehen; ggf. mit Schul-IT abstimmen. |
| API-Test vor Testdaten | `HTTP 200` + `[]` | Kein Fehler: Tabelle war leer. Nach Einfügen fiktiver Datensätze JSON-Antwort mit zwei Hilfestellen. |

## Diagnosebefehle

```bash
# Webserver / Reverse Proxy
sudo nginx -t
sudo systemctl status nginx

# Backend
sudo systemctl status yana-api
sudo journalctl -u yana-api -n 100 --no-pager

# Datenbank
pg_lsclusters

# Lokaler API-Check
curl -i http://127.0.0.1:8000/health

# Certbot / HTTPS
sudo /snap/bin/certbot certificates
sudo systemctl status snap.certbot.renew.timer
curl -Iv https://SERVER_IP/docs
```

Bitte keine Passwörter, Tokens, `privkey.pem`-Inhalte oder personenbezogenen Daten aus Logs in öffentliche GitHub-Issues kopieren.
