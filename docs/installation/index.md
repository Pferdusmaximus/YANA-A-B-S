# Installation & Quick Start

Diese Dokumentation beschreibt die schrittweise Einrichtung von Server, Datenbank, API, Website, Teamportal und Flutter-Entwicklungsumgebung für **YANA – You Are Not Alone**. Die ursprüngliche Serverinstallation wurde im Oktober 2026 abgeschlossen; **Stand der ergänzten Website- und Portal-Implementierung ist der 18. November 2026**.

## Zielsystem

| Komponente | Eingesetzt | Zweck |
|---|---|---|
| VPS | IONOS, 2 vCores / 4 GB RAM | Hosting |
| Ubuntu | 24.04 LTS, GNOME | Betrieb über grafische IONOS-Konsole |
| PostgreSQL 16 + pgAdmin 4 | `app_db` | Fach- und Portal-Daten |
| FastAPI, Uvicorn, Psycopg 3 | Python-Backend | JSON-API und HTML-Portal |
| Jinja2, HTML/CSS | Website/Portal | Templates und Oberfläche |
| Nginx, Certbot, Let's Encrypt | Öffentlicher HTTPS-Zugang | Reverse Proxy und TLS |
| systemd `yana-api` | Produktivdienst | Backend-Lebenszyklus |
| IONOS/Acronis Backup-Agent | Backupsystem | Sicherungsinfrastruktur; Restore-Test offen |
| Flutter / Dart | Mobile App | REST-Datenzugriff und Logikschicht |
| GitHub `YANA-A-B-S` | Versionsverwaltung | Gemeinsame Entwicklung |

## Reproduktionsreihenfolge

1. [Ubuntu und GNOME](ubuntu-gnome.md) einrichten.
2. [IONOS Backup-Agent](backup-agent.md) installieren.
3. [PostgreSQL und pgAdmin](postgresql-pgadmin.md) einrichten.
4. [Ursprüngliches relationales Datenmodell](../technik/datenmodell.md) aufbauen.
5. [FastAPI und systemd-Dienst](fastapi.md) konfigurieren.
6. [Nginx, HTTPS, Certbot](nginx-https.md) konfigurieren.
7. [Öffentliche Website und Teamportal](website-teamportal.md) ergänzen.
8. [Zusätzliche Portal-Datenbanktabellen](../technik/teamportal-datenbank.md), Account und Secret vorbereiten.
9. [Login-/Rollenprüfungen](../technik/teamportal-login.md) und [Portal-Tests](../technik/teamportal-tests.md) durchführen.
10. [GitHub und kontrolliertes Deployment](../technik/teamportal-deployment.md) einrichten.
11. [Flutter-Entwicklungsumgebung](flutter-setup.md), [API-Anbindung](../technik/flutter-api-anbindung.md), [Controller](../technik/flutter-controller.md), [Flutter-Tests](../technik/flutter-tests.md) vervollständigen.
12. [Betrieb, Sicherheit und offene Aufgaben](../technik/betrieb-sicherheit.md) prüfen.

## Achtung bei bestehenden Installationen

**SQL-Tabellen und Portal-Accounts sind bereits angelegt.** Die Befehle in den Kapiteln sind zum Teil historische Reproduktionsbeispiele; vor wiederholter Ausführung Zustand prüfen. Die VPS-Testkopie verwendet dieselbe DB wie der produktive Dienst. `.env`/`.venv` und echte Zugangsdaten niemals aus GitHub überschreiben oder veröffentlichen.

Der nächste Entwicklungsstand ist als [Wiedereinstieg](../technik/weiterarbeit.md) dokumentiert. Ein funktionsfähiger Prototyp ist noch keine datenschutzrechtlich und sicherheitstechnisch freigegebene Beratungsanwendung.
