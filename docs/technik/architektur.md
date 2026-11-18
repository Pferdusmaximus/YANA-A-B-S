# Technische Systemarchitektur

**Stand: 18.11.2026**

## 1. Architekturprinzip

YANA verwendet eine **Client-Server-Architektur** mit gemeinsamem FastAPI-Backend und PostgreSQL-Datenbank. Es gibt drei wichtige Clients: die Flutter-App, die **öffentliche HTML-Website** und den **geschützten Browserzugang zum Teamportal**. Nginx terminiert HTTPS; der Backend-Dienst wird über `systemd` betrieben.

```mermaid
flowchart TB
    F["Flutter / Dart<br/>Models, Repositories, Controller"]
    V["Öffentliche Website<br/>Informationen und Download-Hinweis"]
    T["Teamportal im Browser<br/>Login, Partnerzuordnung und Änderungsfreigabe"]
    subgraph VPS["IONOS VPS: Ubuntu 24.04 · 2 vCores / 4 GB RAM"]
      N["Nginx: HTTPS und Login-Rate-Limit"]
      API["FastAPI / Uvicorn<br/>main.py · portal.py · portal_facilities*.py · portal_facility_changes.py"]
      DB[("PostgreSQL 16<br/>Fach- und Portal-Tabellen")]
      S["systemd: yana-api"]
      B["IONOS/Acronis Backup-Agent"]
      PG["pgAdmin 4 / Ubuntu-Konsole"]
      N --> API
      API --> DB
      S -.-> API
      PG -.-> DB
    end
    F -->|"HTTPS JSON GET"| N
    V -->|"HTTPS /"| N
    T -->|"HTTPS /portal/"| N
    B -.-> VPS
```

Die Website und das Portal werden nicht auf einem zweiten Webserver betrieben; sie verwenden denselben FastAPI-Prozess wie die REST-API. **Die Datenbank ist nicht öffentlich erreichbar.** Die getrennte Test-Codekopie greift derzeit auf dieselbe DB zu; diese Einschränkung wird unter [Portal-Tests](teamportal-tests.md) erläutert.

## 2. Verantwortlichkeiten

| Komponente | Aufgabe | Bestätigter Stand |
|---|---|---|
| Flutter | App-Oberfläche (in Entwicklung), Datenabruf und Zustandsverwaltung | GET-Datenzugriff/Controller/Tests implementiert |
| Website/Jinja2 | Informationsseiten unter `/`, statische Dateien | Produktiv im Browser getestet |
| Portal/Jinja2 | Login, Dashboard, Hilfestellenverwaltung | Produktiv im Browser getestet |
| FastAPI | Routing, Session-Prüfung, SQL-Operationen, JSON-Ausgabe | Funktioniert für vorhandene Routen |
| PostgreSQL | Acht ursprüngliche Fach-/Chat-Tabellen plus fünf Portal-Tabellen | Schema und Speichertest nachgewiesen |
| Nginx | HTTPS, Weiterleitung, Rate-Limit für Login | Konfiguration geprüft und aktiv |
| systemd | Start/Neustart von `yana-api` | Aktiv |
| Certbot | IP-TLS-Zertifikat und Erneuerung | Zertifikat und Dry-Run bestätigt |
| Backup-Agent | Backup-Infrastruktur | Installiert/registriert; vollständiger Restore-Test offen |

## 3. Typische Datenflüsse

### Flutter liest Hilfestellen

```mermaid
sequenceDiagram
    participant F as Flutter / Dart
    participant N as Nginx
    participant A as FastAPI
    participant D as PostgreSQL
    F->>N: GET /hilfestellen (HTTPS)
    N->>A: HTTP intern
    A->>D: SELECT hilfestelle WHERE publication_status = 'published'
    D-->>A: Datensätze
    A-->>F: HTTP 200 + JSON über Nginx
```

Bei Flutter Web in Chrome muss außerdem die CORS-Origin erlaubt sein. Für lokale `localhost`-/`127.0.0.1`-Entwicklungsports wurde `CORSMiddleware` in `main.py` ergänzt.

### Hilfestellen verwalten und Änderungen freigeben

Das Portal verwendet ein signiertes Cookie mit zufälliger Session-ID. FastAPI verifiziert den Session-Hash in `portal_session`, die Rolle und bei Partnern die Einrichtungszuordnung. POST-Formulare benötigen einen CSRF-Token.

- **Entwurf (`draft`):** Berechtigte Accounts können die vier unterstützten Kontaktfelder unmittelbar ändern; `FOR UPDATE` und Audit sichern den Speichervorgang. Die Veröffentlichung erfolgt erst nach Einreichung und Admin-Freigabe.
- **Veröffentlichte Einrichtung (`published`):** Änderungen werden als eigener Antrag in `portal_facility_change` abgelegt. Erst die Adminfreigabe aktualisiert `hilfestelle` in einer Transaktion samt Audit.

Mehr unter [Hilfestellenverwaltung](teamportal-hilfestellen.md) und [Änderungsfreigabe](teamportal-aenderungsfreigabe.md).

## 4. Repository- und Serverstruktur

```text
YANA-A-B-S/
├── apps/mobile/             # Flutter
├── services/api/            # FastAPI + Website/Portal
├── docs/                    # Diese MkDocs-Dokumentation
└── mkdocs.yml               # Navigation und Site-Konfiguration

IONOS VPS:
~/yana-deploy-source/       # GitHub-Klon (Entwicklungsversion)
~/yana-portal-test/          # Python-Testkopie
~/yana-backend/              # Produktiver FastAPI-Code, .venv, .env
/etc/systemd/system/yana-api.service
/etc/nginx/...
```

Es wurde bewusst **nicht** für jede Weboberfläche ein neues Backend oder eine zweite PostgreSQL-Instanz eingeführt. Dies vereinfacht den Einstieg, verlangt jedoch konsequente Rollenprüfung und vorsichtige Releases.

## 5. Technologische und fachliche Grenzen

- Die öffentliche `/hilfestellen`-API kann weiterhin Standortangaben enthalten; Schutzunterkünfte vor Aufnahme realer Datensätze besonders behandeln.
- Für Partner sind Einrichtungen inzwischen über `portal_facility_assignment` zugeordnet und serverseitig gefiltert.
- Neuaufnahme, Veröffentlichungsstatus und Änderungsvorschläge mit Freigabe sind für **fiktive Testdaten** implementiert; reale Notfallangebote sind noch nicht verifiziert.
- Technische Logik in Flutter ist getestet, vollständige sichtbare App-Screens noch nicht als fertig nachgewiesen.
- Es gibt noch keinen isolierten Staging-Datenbankbetrieb und keinen automatisierten CI-/Deployment-Prozess.

Verweise: [Teamportal-Architektur](teamportal-architektur.md), [Entscheidungen](entscheidungen.md), [Betrieb und Sicherheit](betrieb-sicherheit.md) und [Wiedereinstieg](weiterarbeit.md).
