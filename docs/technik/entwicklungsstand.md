# Entwicklungsstand und Änderungsprotokoll

**Dokumentationsstand: 27. Oktober 2026**

Dieses Protokoll hält nachvollziehbar fest, **was im Projekt tatsächlich eingerichtet und erfolgreich überprüft wurde**. Zeitpunkte orientieren sich am dokumentierten Projektverlauf; konkrete Git-Commit-IDs sind noch nachzutragen. Ein erfolgreiches technisches Experiment wird nicht automatisch als produktionsbereite Funktion bewertet.

## 1. Meilensteine

| Zeitraum | Umsetzung | Verifizierter Nachweis | Noch offen |
|---|---|---|---|
| Oktober 2026 – Servereinrichtung | IONOS-VPS, Ubuntu 24.04 LTS, GNOME über Browser-Konsole | GNOME erreichbar | Ressourcenüberwachung im Dauerbetrieb |
| Oktober 2026 – Backup | IONOS/Acronis-Agent | Agent erfolgreich installiert und in Backup-Konsole registriert | Abgeschlossener Sicherungs- und Restore-Test hier nicht bestätigt |
| Oktober 2026 – Datenbank | PostgreSQL 16, pgAdmin 4, 8 Tabellen | Cluster `online`, pgAdmin verbunden, SQL-Schema angelegt | Fachliche Datenvalidierung und Schutz sensibler Daten |
| Oktober 2026 – REST-API | Python / FastAPI / Psycopg | Swagger und GET-Endpunkte über VPS getestet | Authentifizierung, Filter, Chat, Admin-Endpunkte |
| 20.10.2026 – Betrieb | `yana-api` via systemd, Nginx Reverse Proxy | Dienst aktiv, lokaler Proxy funktionsfähig | Monitoring und Deployment-Automatisierung |
| 20.10.2026 – Verschlüsselung | Let's Encrypt IP-Zertifikat via Certbot | Echtes Zertifikat statt Staging; Firefox sichere Verbindung | Erneuerungen künftig überwachen |
| 20.10.2026 – Certbot-Automation | Snap-Timer, Nginx Deploy Hook | Timer aktiv, `renew --dry-run --run-deploy-hooks` erfolgreich | Langfristige Erneuerungsüberwachung |
| Bis 27.10.2026 – Client-Setup | Flutter 3.44.4, Dart 3.12.2, Android-Projekt | Android-Debug-Build erfolgreich | iOS-Build, Release-Signierung |
| Bis 27.10.2026 – Dart-Netzwerk | HTTP-Client, 3 Models, 3 Repositories | 2 Hilfestellen, 2 Kategorien, 0 Notfallnummern per Live-Dart-Test | Gefülltes Notfallnummern-JSON, UI-Integration |
| Bis 27.10.2026 – Flutter-Logik | `ChangeNotifier`-Controller für drei Bereiche | Start-/Erfolgs-/Fehler-Tests mit Fake-Repositories bestanden | Screen-Lebenszyklus und echte Geräteinteraktion |
| 27.10.2026 – Qualitätssicherung | Tests von Live-Netzzugriff getrennt | `flutter analyze` und `flutter test` erfolgreich | CI-Automatisierung, MockClient-Parsingtests |

## 2. Was wurde geändert gegenüber der Dokumentation vom 20.10.2026?

Die ältere Dokumentation enthielt Server-, Datenbank-, Reverse-Proxy- und TLS-Schritte. Der Flutter-Client war darin lediglich eine geplante Systemkomponente. Die Erweiterung zum 27.10.2026 ergänzt **nicht nur Installationsanleitungen**, sondern auch die tatsächlichen Datenmodelle, Repositories, Controller, Live-Tests, Fake-Tests und ihre Fehlersuche. Die Systemarchitektur und die API-Referenz wurden entsprechend aktualisiert.

| Neu/aktualisiert | Zweck |
|---|---|
| [Flutter-Installation](../installation/flutter-setup.md) | Windows-SDK, lokaler Git-Klon, Android-Debug-Build |
| [Client-Architektur](flutter-architektur.md) | Drei Schichten und Verantwortung der Dateien |
| [API-Datenzugriff](flutter-api-anbindung.md) | Modelle, JSON, Repositories und gemeinsamer API-Client |
| [Controller](flutter-controller.md) | `ChangeNotifier`, Lade-/Fehlerzustand, Lebenszyklus |
| [Testkonzept](flutter-tests.md) | Fake-Controller-Tests vs. Live-Smoke-Tests |
| [Flutter-Fehlerprotokoll](flutter-troubleshooting.md) | Tatsächliche Fehlermeldungen und Gegenmaßnahmen |
| [Team-Workflow](flutter-teamworkflow.md) | Übergabe an UI-Entwicklung und Git-Pull-Requests |
| [Betrieb und Sicherheit](betrieb-sicherheit.md) | Status der mobilen Anbindung und weitere Risiken |

## 3. Nächste Entwicklungsschritte

- [ ] Controller in die von der Projektgruppe entwickelte Flutter-Oberfläche einbinden.
- [ ] Hilfestellen und Kategorien auf einem Android-Gerät sichtbar darstellen; Lade-, Fehler- und Leerzustand prüfen.
- [ ] Notfallnummern ausschließlich mit verifizierten Daten freigeben; Offline-Verfügbarkeit prüfen.
- [ ] `http.MockClient`-Tests für nicht-leere API-Antworten und fehlerhafte JSON-Formate ergänzen.
- [ ] Servercode aus dem nur lokal auf dem VPS liegenden `yana-backend` kontrolliert in `services/api/` versionieren (ohne `.env` und Geheimnisse).
- [ ] Authentifizierung, Autorisierung, Logging und Datenschutznachweise erarbeiten, bevor Chat- oder Nutzerdaten über die API verarbeitet werden.
- [ ] GitHub Actions für Analyse und Unit-Tests erstellen.
- [ ] Vollständigen erfolgreichen Sicherungs- und Wiederherstellungstest dokumentieren.
- [ ] Release-/Installationsanleitung, Screenshots, App-Download und Promovideo ergänzen.

## 4. Nachweisdokumentation

Um den Projektfortschritt später objektiv beurteilen zu können, sollten für jeden neuen Meilenstein die **betroffenen Commit-IDs, der getestete Branch, der konkrete Befehl, das Ergebnis und gegebenenfalls ein bereinigter Screenshot** ergänzt werden. Bisher wurden Ergebnisse im Entwicklungsdialog mit Terminalausgaben bestätigt, jedoch noch nicht als CI-Artefakte bzw. konkrete Git-Commits referenziert.

**Sicherheitsregel:** Screenshots und Logs vor dem Hochladen auf sensible Daten prüfen; insbesondere keine Zugangsdaten, Privatschlüssel, echten Chat- oder Standortdaten öffentlich dokumentieren.
