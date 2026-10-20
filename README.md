# YANA-A-B-S

## Projekt

YANA ist eine mobile Flutter-App für Frauen in Not. Die App stellt
Hilfsangebote und Informationen bereit, zeigt geeignete Anlaufstellen auf einer
Karte und bietet einen Chatbot für eine erste Orientierung.

Das Repository ist als Monorepo aufgebaut:

```text
.
├── apps/
│   └── mobile/                 # Flutter-App für iOS und Android
│       ├── lib/
│       │   ├── app/            # App-Start, Routing, Theme, Konfiguration
│       │   ├── core/           # Fehler, Netzwerk, Storage, gemeinsame Widgets
│       │   ├── features/       # Fachliche Bereiche der App
│       │   │   ├── emergency/  # Notfall- und Sicherheitsfunktionen
│       │   │   ├── chatbot/    # Chatbot-Oberfläche und State
│       │   │   ├── map/        # Karte und Standortanzeige
│       │   │   ├── help/       # Hilfestellen und Suche/Filter
│       │   │   └── information/# Informationsinhalte
│       │   └── main.dart
│       ├── test/
│       ├── integration_test/
│       └── assets/
├── services/
│   └── api/                    # FastAPI-Backend
│       ├── app/
│       │   ├── api/            # Versionierte HTTP-Routen
│       │   ├── core/           # Settings, Authentifizierung, Logging
│       │   ├── db/             # PostgreSQL-Verbindung und Migrationen
│       │   ├── models/         # Datenbankmodelle
│       │   ├── schemas/        # Request-/Response-Modelle
│       │   ├── repositories/   # Datenzugriff
│       │   └── services/       # Fachlogik
│       └── tests/
├── infra/                      # Docker, Deployment und Umgebungsbeispiele
├── docs/                       # Projekt- und Entwicklerdokumentation
└── mkdocs.yml
```

### Architektur

Die Flutter-App spricht ausschließlich mit der FastAPI-API. Die API kapselt
den Zugriff auf PostgreSQL; die App erhält keine direkten Datenbankzugänge.
Fachliche Funktionen werden in der App nach Features und im Backend nach
API-, Datenzugriffs- und Serviceschicht getrennt.

Weitere Einzelheiten stehen in der
[Entwicklerdokumentation](docs/doku.md).

## Lokale Entwicklung

Die konkreten Befehle werden ergänzt, sobald Flutter- und FastAPI-Projekte
initialisiert sind. Für lokale Zugangsdaten sollen ausschließlich nicht
versionierte `.env`-Dateien verwendet werden; Zugangsdaten gehören nicht in
das Repository.

DEFINITION OF DONE (DoD)
1. mindestens einem Teammitlgied vorstellen
2. Tests durchführen
3. mindestens ein Teammitglied muss absegnen
4. Dokumentation aktualisieren
5. ggf. ReadMe aktualisieren
   
