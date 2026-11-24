# Website-Designsystem und Benutzeroberflächen

**Stand: 24. November 2026 · Weiß-lila YANA-Redesign produktiv bereitgestellt und im Browser bestätigt.**

## Gestaltungsprinzip

Das gesamte Webangebot – Landingpage und geschütztes Portal – verwendet ein gemeinsames, **helles, professionelles YANA-Design**. Weiß bildet die Grundfläche; kräftiges Lila wird sparsam für aktive Bedienelemente, Links, Fokuszustände und Akzente eingesetzt. Helle Lavendelabstufungen dienen zur optischen Gruppierung.

Im Designkonzept wurden unter anderem diese Richtwerte verwendet:

| Rolle | Beispielwert | Zweck |
|---|---|---|
| Primärlila | `#6D28D9` | Hauptaktionen, Markenakzente |
| Akzentlila | `#8B5CF6` | Hover-/Akzentzustände |
| Lavendel | `#F2EAFF` | Dezente Hintergrundflächen |
| Weiß | `#FFFFFF` | Seiten- und Tabellenhintergrund |

Die **tatsächlich im Quellcode definierten CSS-Variablen sind verbindlich**; die Tabelle hält die Designabsicht fest und ersetzt keine aktuelle Codeinspektion.

## Umgesetzte Seiten

- **Landingpage:** vereinheitlichter Hero- und Kachelbereich, Teamportal-Link rechts oben.
- **Login:** Formular direkt sichtbar, kurzer Hinweis auf den Zugang nur für autorisierte Kanzleien, Hilfestellen, Beratungsstellen und YANA-Mitarbeitende.
- **Dashboard:** Karten im lila Design; Logout in der oberen Navigation.
- **Hilfestellenverwaltung:** Buttons, Formulare und Statusfarben vereinheitlicht.
- **Standortfreigaben:** kompakte Tabelle mit Suche, Statusfilter und aufklappbaren Details statt großer Einzelkarten.
- **Partnerverwaltung:** ebenfalls kompakte Tabelle mit Suche/Filter und ausklappbaren Aktionen; bestehende CSRF-geschützte Formulare bleiben erhalten.
- **Weitere Portalseiten:** Layout und Akzentfarben über `templates/base.html` und `static/css/style.css` vereinheitlicht.

## Technische Umsetzung

| Datei | Aufgabe |
|---|---|
| `services/api/static/css/style.css` | Zentrale Farben, Abstände, Komponenten und Responsive-Regeln |
| `services/api/templates/base.html` | Gemeinsames Layout, Navigation und Logout |
| `services/api/templates/index.html` | Landingpage |
| `services/api/templates/portal/login.html` | Anmeldung und berechtigungserklärender Hinweis |
| `services/api/templates/portal/standorte.html` | Standorttabelle |
| `services/api/templates/portal/partner.html` | Partnertabelle und Verwaltungsaktionen |

Serverseitige **Rollen-/CSRF-Prüfungen bleiben unabhängig vom Design**. Die visuelle Ausblendung von Links ist keine Zugangssicherung.

## Konvention für neue Seiten

Neue Portalansichten erweitern das bestehende `base.html`, benutzen gemeinsame CSS-Klassen und Farben und enthalten keine eigenständigen abweichenden Designsysteme. Datendichte Ansichten bevorzugen **Tabelle + Filter + aufklappbare Details**; mobile Ansichten bleiben bedienbar. Jedes POST-Formular behält ein gültiges CSRF-Feld und die zuständige serverseitige Berechtigungsprüfung.

Die Designumstellung wurde auf dem produktiven Server vom Projektverantwortlichen als funktionsfähig und gelungen bestätigt. Ein vollständiger Accessibility-Audit (Tastaturbedienung, Kontrast, Screenreader, Mobilgeräte) ist weiterhin eine separate Aufgabe.
