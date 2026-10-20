# Entwicklerdokumentation

## Projektstruktur

Das Repository ist ein Monorepo. Die ausführliche Übersicht ist auch im
[README](../README.md) enthalten.

### `apps/mobile`

Die Flutter-App ist nach fachlichen Features organisiert. Jedes Feature soll
seine Screens, Widgets, Models, Repositories und seinen State möglichst
zusammen halten. Wiederverwendbare technische Bausteine gehören nach
`lib/core`, nicht in ein einzelnes Feature.

Empfohlene Aufteilung innerhalb eines Features:

```text
features/<feature>/
├── data/           # API-DTOs und konkrete Repository-Implementierungen
├── domain/         # fachliche Models und Repository-Verträge
└── presentation/   # Screens, Widgets und State-Management
```

Wichtige Features sind `emergency`, `chatbot`, `map`, `help` und
`information`. Standortberechtigungen und externe Kartenanbieter werden in
`core` bzw. der Kartenfunktion gekapselt.

### `services/api`

Das Backend verwendet eine versionierte API, zum Beispiel
`/api/v1/help-centers` und `/api/v1/chat`. Die Schichten haben folgende
Aufgaben:

- `api`: HTTP-Endpunkte, Authentifizierung und Statuscodes
- `schemas`: öffentliche Request- und Response-Formate
- `services`: fachliche Abläufe, zum Beispiel Suche und Chatbot-Orchestrierung
- `repositories`: Datenbankabfragen
- `models`: PostgreSQL-/ORM-Modelle
- `db`: Verbindung, Transaktionen und Migrationen

Damit bleiben HTTP-Details und Datenbankzugriff voneinander getrennt und
können unabhängig getestet werden.

## Datenbank

PostgreSQL ist ausschließlich über die FastAPI-Anwendung erreichbar.
Voraussichtliche fachliche Tabellen sind:

- `help_centers`: Name, Beschreibung, Adresse, Koordinaten und Kontakt
- `help_center_categories`: Kategorien und Zuordnung zu Hilfestellen
- `information_articles`: redaktionelle Informationsinhalte
- `chat_sessions` und `chat_messages`: nur falls Chatverläufe gespeichert
  werden sollen

Personenbezogene Daten und Chatverläufe müssen vor der Implementierung
hinsichtlich Zweck, Aufbewahrung und Löschung geklärt werden. Änderungen am
Schema werden über versionierte Migrationen eingespielt.

## API

Die API liefert JSON und wird ausschließlich über HTTPS angesprochen.
Vorgesehene Endpunktgruppen:

```text
/api/v1/health
/api/v1/help-centers
/api/v1/information
/api/v1/chat
/api/v1/emergency
```

Die OpenAPI-Dokumentation der FastAPI-Anwendung ist die maßgebliche
Schnittstellenbeschreibung. Die Flutter-App verwendet dafür typisierte
DTOs und kapselt HTTP-Fehler in der gemeinsamen Netzwerk-Schicht.

## Deployment

Für die lokale Entwicklung kann `infra/docker-compose.yml` später API und
PostgreSQL starten. In produktiven Umgebungen sollen API und Datenbank
getrennt betrieben, Zugangsdaten über Secrets injiziert und Backups sowie
Monitoring eingerichtet werden.

Umgebungsabhängige Einstellungen gehören in `.env`-Dateien außerhalb der
Versionsverwaltung. Eine `.env.example` darf nur Platzhalter enthalten.
