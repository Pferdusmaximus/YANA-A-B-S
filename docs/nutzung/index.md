# Nutzungshandbuch – derzeitiger Entwicklungsstand

Die mobile YANA-App wird mit **Flutter/Dart** entwickelt. Die technische Anbindung an die bereits eingerichtete FastAPI steht zum dokumentierten Stand vom **20.10.2026** noch aus. Daher werden hier **keine** noch nicht implementierten Nutzerfunktionen als fertig dargestellt.

## Geplante Funktionen (aus Projektkonzept)

- Standortbezogene Anzeige von Hilfestellen.
- Übersicht über Notfallnummern mit schneller Kontaktmöglichkeit.
- Kategorisierung von Hilfsangeboten.
- Informationsmaterial zu Gewaltprävention und Handlungsmöglichkeiten.
- Möglichkeit einer anonymen Erstberatung (für die Umsetzung sind besondere Sicherheits- und Datenschutzanforderungen zu beachten).

## Für Entwickler bereits nutzbar

Die Backend-API kann über `/docs` interaktiv getestet werden. Unter `/hilfestellen` und `/kategorien` sind derzeit **rein fiktive** Datensätze vorhanden. Details siehe [API-Referenz](../technik/api-referenz.md).

## Noch zu ergänzen

Sobald die Flutter-Integration umgesetzt ist, werden hier die **konkreten Benutzerabläufe**, bereinigte Screenshots und Nutzertests dokumentiert. Download-Link/CTA und Promovideo werden auf der [Startseite](../index.md) ergänzt.

> **Sicherheitshinweis:** YANA befindet sich in der Entwicklungsphase. Angezeigte Teststandorte sind keine realen, verifizierten Hilfsangebote; in einer akuten Notlage sind offizielle Notruf- und Beratungsstellen zu kontaktieren.
