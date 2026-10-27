# YANA – You Are Not Alone

**Hilfe finden. Informationen erhalten. In schwierigen Situationen schneller handeln.**

YANA ist ein Schulprojekt zur Entwicklung einer mobilen Anwendung, die betroffenen Frauen den Zugang zu Notfallkontakten, Hilfsstellen und Informationen zu Gewaltprävention erleichtern soll. Die Anwendung soll standortbezogene Angebote übersichtlich darstellen und künftig weitere unterstützende Funktionen bereitstellen. Das technische Fundament besteht aus Flutter, einer FastAPI-Schnittstelle und PostgreSQL.

**Projektstatus (27.10.2026):** Das Backend läuft auf dem IONOS-VPS. In Flutter sind für **Hilfestellen, Kategorien und Notfallnummern** jeweils Model, Repository und Controller implementiert. Alle drei REST-Verbindungen wurden per Dart-Live-Test geprüft; die Controller-Tests mit Fake-Repositories sind erfolgreich. **Die fertige App-Oberfläche und die Einbindung der Controller in sichtbare Screens sind noch in Entwicklung.**

> **Hinweis:** Aktuell angelegte Hilfestellen sind fiktive Testdaten. Die Software stellt noch keinen verlässlichen Notfalldienst dar. Bei akuter Gefahr die offiziellen lokalen Notrufnummern verwenden.

## Projekt kennenlernen

- [Installation & Quick Start](installation/index.md) – Server, Backend und Flutter-Entwicklungsumgebung reproduzieren.
- [Flutter einrichten](installation/flutter-setup.md) – Windows, Flutter SDK, Git und Android-Build.
- [Technische Dokumentation](technik/index.md) – Architektur, Implementierung, Tests und Fehlerprotokolle.
- [Technische Systemarchitektur](technik/architektur.md) – Gesamtsystem und Datenfluss.
- [Flutter: Drei-Schichtenmodell](technik/flutter-architektur.md) – Aufbau der mobilen Anwendung.
- [Flutter: API-Anbindung](technik/flutter-api-anbindung.md) – Models, Repositories und HTTPS-Zugriff.
- [Flutter: Tests](technik/flutter-tests.md) – Controller-Tests und manuelle Live-Tests.
- [API-Referenz](technik/api-referenz.md) – Implementierte Server-Endpunkte.
- [Nutzungshandbuch](nutzung/index.md) – Funktionen und derzeitige Entwicklungsgrenzen.

## Nachgewiesener technischer Stand

| Bereich | Nachweis |
|---|---|
| PostgreSQL / FastAPI / HTTPS | Laufendes Backend, öffentlich vertrauenswürdiges TLS-Zertifikat |
| Flutter-Live-API-Tests | 2 Hilfestellen, 2 Kategorien, 0 Notfallnummern erfolgreich abgerufen |
| Flutter-Logikschicht | 3 Controller, jeweils Start-/Erfolgs-/Fehlertest bestanden |
| Mobile UI / reale Beratung | In Entwicklung, **kein** produktiver Notfalldienst |

## Download und Projektvideo

App-Download und Promovideo werden ergänzt, sobald eine vorzeigbare App-Version zur Verfügung steht. Das Promovideo wird entsprechend den Vorgaben unter einem Titel mit **„RDF Projekt“** oder **„RDF Projektarbeit“** veröffentlicht.

<!-- Logo und Screenshots nach Freigabe hier einbinden; keine Platzhalter-Bilder mit kaputten Links veröffentlichen. -->
