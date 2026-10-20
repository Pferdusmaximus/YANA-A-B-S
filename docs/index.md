# YANA-A-B-S

## Zweck

YANA unterstützt Frauen in Not beim schnellen Finden von Hilfsangeboten und
verlässlichen Informationen. Die mobile Anwendung wird mit Flutter für iOS und
Android entwickelt.

Geplante Kernfunktionen:

- Hilfestellen aus der Datenbank suchen, filtern und anzeigen
- Hilfestellen auf einer Karte darstellen
- Informationen zu Sicherheit, Beratung und weiteren Themen bereitstellen
- Chatbot als niedrigschwellige erste Orientierung
- Notfallinformationen schnell erreichbar machen

## Systemübersicht

```text
Flutter-App (iOS / Android)
          │ HTTPS/JSON
          ▼
FastAPI (REST-API)
          │
          ▼
PostgreSQL
```

Die App greift nie direkt auf PostgreSQL zu. Authentifizierung, Validierung,
Berechtigungen und Datenbankzugriffe liegen im Backend.

## Dokumentation

- [Entwicklerdokumentation](doku.md)
- [Projekt-README](../README.md)
