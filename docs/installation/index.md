# Installation & Quick Start

Diese Dokumentation beschreibt die **reproduzierbare Einrichtung des bisher umgesetzten YANA-Backends** auf einem IONOS-VPS. Der Serveraufbau bis einschließlich der getesteten automatischen HTTPS-Zertifikatserneuerung (Schritt 22.3) wurde am **20. Oktober 2026** abgeschlossen. Die Dokumentation wurde am **27. Oktober 2026** um die Flutter-Entwicklungsumgebung, API-Anbindung, Controller und Tests erweitert.

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
| Mobiler Client | Flutter **3.44.4**, Dart **3.12.2** (beobachteter Stand) | API-Zugriffe und Controller bereits implementiert; UI in Entwicklung |

> Die Versionsangaben entsprechen der Einrichtung bzw. den dokumentierten Beobachtungen; zur Wiederholbarkeit vor jedem neuen Deployment die konkret installierten Versionen erneut prüfen. Die Option „Ubuntu 24.04 + Plesk“ bzw. „+ n8n“ wurde **nicht** ausgewählt.

## Reproduktionsreihenfolge

1. [Ubuntu installieren und GNOME konfigurieren](ubuntu-gnome.md)
2. [IONOS Backup-Agent installieren und Registrierung prüfen](backup-agent.md)
3. [PostgreSQL und pgAdmin installieren](postgresql-pgadmin.md)
4. [Datenbankstruktur des ER-Modells anlegen](../technik/datenmodell.md)
5. [FastAPI erstellen, DB anbinden und als Dienst konfigurieren](fastapi.md)
6. [Nginx als Reverse Proxy einrichten, HTTPS aktivieren und Erneuerung testen](nginx-https.md)
7. [Flutter-/Dart-Entwicklungsumgebung einrichten](flutter-setup.md)
8. [Flutter-API-Zugriff mit Models und Repositories](../technik/flutter-api-anbindung.md)
9. [Controller für die Flutter-Logikschicht](../technik/flutter-controller.md)
10. [Live-Verbindungen und Unit-Tests prüfen](../technik/flutter-tests.md)
11. [Sicherheit, Backups und Betriebskontrollen überprüfen](../technik/betrieb-sicherheit.md)

## Vor der Veröffentlichung beachten

Alle Befehle sind Beispiele für Ubuntu 24.04 und müssen auf den Zielserver angepasst werden. **Nicht veröffentlichen:** `.env`, Klartextpasswörter, private TLS-Schlüssel, IONOS-Zugangsdaten, Datenbankexports mit echten Nutzerdaten, Token oder geheimhaltungsbedürftige Adressen. Server-IP und Benutzernamen sind in Beispielen abstrahiert; wo `SERVER_IP` steht, ist die reale öffentliche IPv4 einzusetzen.

Ein funktionierender HTTPS-Endpunkt oder ein erfolgreicher Flutter-Live-Test ist noch **kein** Nachweis für eine sichere, produktionsbereite Beratungslösung. Die derzeitigen GET-Endpunkte stellen Testfunktionalität bereit; Authentifizierung und Datenschutzmaßnahmen stehen teilweise noch aus. Für die Flutter-Oberfläche siehe den [Übergabeplan](../technik/flutter-teamworkflow.md).
