# Installation & Quick Start

Diese Dokumentation beschreibt die **reproduzierbare Einrichtung des bisher umgesetzten YANA-Backends** auf einem IONOS-VPS. Sie entspricht dem Entwicklungsstand vom **20. Oktober 2026** und umfasst den Serveraufbau bis einschließlich der getesteten automatischen HTTPS-Zertifikatserneuerung (Schritt 22.3).

## Zielsystem und Voraussetzungen

| Komponente | Eingesetzte Lösung | Funktion |
|---|---|---|
| Hosting | IONOS VPS, 2 vCores / 4 GB RAM | Virtueller Linux-Server |
| Betriebssystem | Ubuntu 24.04 LTS | Serverplattform |
| GUI | GNOME (`ubuntu-desktop-minimal`) | Bedienung über IONOS-Konsole |
| Backup | IONOS Cloud Backup / Acronis-Agent | Inkrementelle/vollständige Sicherung nach Schutzplan |
| Datenbank | PostgreSQL 16 | Persistente Anwendungsdaten |
| Datenbankverwaltung | pgAdmin 4 Desktop | SQL-Editor und Administration |
| Backend | Python 3.12, FastAPI **0.150.0** (bei Einrichtung gemessen), Psycopg 3 | REST-API |
| ASGI-Server | Uvicorn | Ausführung der FastAPI-Anwendung |
| Dienstverwaltung | systemd | Autostart und Neustart nach Fehlern |
| Reverse Proxy | Nginx (Screenshot: 1.24.0) | HTTPS-Terminierung, Weiterleitung an Uvicorn |
| TLS | Let's Encrypt über Certbot (Snap, für IP-Zertifikate ≥ 5.4) | Öffentlich vertrauenswürdiges IP-Zertifikat |
| Künftiger Client | Flutter/Dart | Mobile App; **noch nicht verbunden** |

> Die Versionsangaben entsprechen der Einrichtung bzw. den dokumentierten Beobachtungen; zur Wiederholbarkeit vor jedem neuen Deployment die konkret installierten Versionen erneut prüfen. Die Option „Ubuntu 24.04 + Plesk“ bzw. „+ n8n“ wurde **nicht** ausgewählt.

## Reproduktionsreihenfolge

1. [Ubuntu installieren und GNOME konfigurieren](ubuntu-gnome.md)
2. [IONOS Backup-Agent installieren und Registrierung prüfen](backup-agent.md)
3. [PostgreSQL und pgAdmin installieren](postgresql-pgadmin.md)
4. [Datenbankstruktur des ER-Modells anlegen](../technik/datenmodell.md)
5. [FastAPI erstellen, DB anbinden und als Dienst konfigurieren](fastapi.md)
6. [Nginx als Reverse Proxy einrichten, HTTPS aktivieren und Erneuerung testen](nginx-https.md)
7. [Sicherheit, Backups und Betriebskontrollen überprüfen](../technik/betrieb-sicherheit.md)

## Vor der Veröffentlichung beachten

Alle Befehle sind Beispiele für Ubuntu 24.04 und müssen auf den Zielserver angepasst werden. **Nicht veröffentlichen:** `.env`, Klartextpasswörter, private TLS-Schlüssel, IONOS-Zugangsdaten, Datenbankexports mit echten Nutzerdaten, Token oder geheimhaltungsbedürftige Adressen. Server-IP und Benutzernamen sind in Beispielen abstrahiert; wo `SERVER_IP` steht, ist die reale öffentliche IPv4 einzusetzen.

Ein funktionierender HTTPS-Endpunkt ist noch **kein** Nachweis für eine sichere, produktionsbereite Beratungslösung. Die derzeitigen GET-Endpunkte sind Testfunktionalität; Authentifizierung und Datenschutzmaßnahmen stehen teilweise noch aus.
