# Team-Workflow und Übergabe zwischen API und Flutter-Oberfläche

**Stand: 27. Oktober 2026 · API-/Controller-Schicht fertig; Präsentation parallel in Entwicklung**

Im YANA-Team wird die **Startseite/Präsentationsschicht** parallel zur **Datenzugriffs- und Logikschicht** entwickelt. Damit Änderungen nicht gegenseitig überschrieben werden, erhält die UI-Entwicklung eine stabile technische Schnittstelle.

## 1. Aufgaben und Dateien trennen

| Arbeitsbereich | Primäre Dateien | Verantwortlichkeit |
|---|---|---|
| Startseite und Navigation | `lib/main.dart`, später `lib/app/`, `lib/features/*/presentation/` | Design, Routen, Widgets, Nutzerinteraktion |
| Gemeinsames Netzwerk | `lib/core/config/`, `lib/core/network/` | API-Basisadresse, HTTP/JSON |
| Datenmodelle und Repositories | `lib/features/*/data/` | JSON-Typisierung und Datenabruf |
| Controller | `lib/features/*/logic/` | Zustände, Laden, Fehlerbehandlung |
| Unit-Tests | `test/` | Reproduzierbare Fake-Tests ohne Server |
| Live-Diagnose | `tool/` | Manuelle GET-Tests gegen den VPS |
| Dokumentation | `docs/` | MkDocs, technische Entscheidungen, Qualitätssicherung |

Die Model-/Repository-/Controller-Schnittstellen wurden erfolgreich separat getestet. **Eine fertige Screen-Integration ist noch nicht nachgewiesen.**

## 2. Welche Schnittstellen die UI verwenden kann

**Hilfestellen:**

```dart
final controller = HelpController();
await controller.loadFacilities();
final hilfestellen = controller.facilities;
final laedt = controller.isLoading;
final fehler = controller.errorMessage;
```

**Kategorien:**

```dart
final controller = CategoryController();
await controller.loadCategories();
final kategorien = controller.categories; // List<YanaCategory>
```

**Notfallkontakte:**

```dart
final controller = EmergencyController();
await controller.loadContacts();
final kontakte = controller.contacts; // List<EmergencyContact>, derzeit leer
```

Dies sind **methodische Auszüge**, keine vollständigen UI-Screens. Ein Flutter-Screen muss `ChangeNotifier` abonnieren, einen Lade-/Fehlerzustand anzeigen und den Controller bei Freigabe mit `dispose()` schließen. Ein vollständiger Beispiel-Screen steht unter [Controller und Flutter-UI](flutter-controller.md#5-controller-im-flutter-screen-verwenden-integrationsbeispiel).

**Datenvertrag:** Der UI-Code soll auf Model-Properties wie `facility.name`, `facility.address` oder `category.name` zugreifen, **nicht** auf rohe Map-Schlüssel wie `facility_id` oder `phone_number`. Das Parsing bleibt zentral in den Models.

## 3. Git-Workflow für parallele Arbeit

Ein zweckmäßiges Vorgehen für ein gemeinsames öffentliches Repository:

```powershell
# Vom Repository-Root
# Vor dem Erstellen eines Branches: aktuellen Stand abrufen
git checkout main
git pull origin main

git switch -c feature/flutter-api
# Änderungen vornehmen und prüfen ...
git status
# Nur beabsichtigte, überprüfte Dateien stagen:
git add apps/mobile/lib apps/mobile/test apps/mobile/tool docs
# Kein git add . ohne Prüfung, wenn Secrets oder lokale Dateien möglich sind.
git commit -m "Implement Flutter API models repositories and controllers"
git push -u origin feature/flutter-api
```

Danach einen Pull Request auf `main` erstellen und mit dem Team prüfen. Ein Teammitglied kann beispielsweise `feature/flutter-home` verwenden. **Beide** sollten vor dem Zusammenführen Tests und Review ausführen.

### Check vor einem Pull Request

```powershell
cd apps/mobile
flutter.bat pub get
flutter.bat analyze
flutter.bat test
```

Ein manueller Live-Test (`dart run tool/...`) ist sinnvoll, wenn die REST-Schnittstelle geändert wurde, gehört aber **nicht zwingend** in jeden automatisierten Pull-Request-Check.

## 4. Was ins Repository gehört – und was nicht

**Einchecken:** Dart-Quellcode, Models, Repositories, Controller, Tests, `pubspec.yaml`, `pubspec.lock`, Plattformkonfiguration, öffentliche MkDocs-Dokumentation.

**Nicht einchecken:** `.env`, API-/DB-Secrets, private TLS-Schlüssel, Android-Keystore, erzeugte Build-Artefakte, lokale `.dart_tool/`-Dateien, Test-/Produktivdaten mit Personenbezug.

Vor einem Push prüfen:

```powershell
git status
git diff --cached --stat
```

Wenn ein Secret versehentlich committet wird, reicht das Löschen aus der letzten Version **nicht**. Das Secret muss rotiert und die Git-Historie bzw. mögliche bereits veröffentlichte Kopien überprüft werden.

## 5. Änderungen an der API kommunizieren

Ändert sich der FastAPI-Endpunkt oder das JSON-Schema, muss das Team abgestimmt anpassen:

1. FastAPI/SQL-Implementierung auf dem Server (bzw. künftig `services/api/`).
2. [REST-API-Referenz](api-referenz.md).
3. Dart-Model `fromJson()` und gegebenenfalls Repository.
4. Fake-Tests und manuelle Live-Verbindungstests.
5. UI-Anzeige/Validierung, falls neue Felder sichtbar werden.

Das Ziel ist ein klarer **API-Vertrag**, sodass Präsentation und Backend unabhängig entwickelt werden können.

## 6. Übergabe-Checkliste für die Oberfläche

- [x] Hilfestellen, Kategorien und Notfallnummern per HTTPS erreichbar.
- [x] Models und Repositories für alle drei Bereiche vorhanden.
- [x] Controller mit Lade- und Fehlerzustand vorhanden.
- [x] Fake-Controller-Tests für alle drei Bereiche erfolgreich.
- [ ] Hilfestellen-Screen bindet `HelpController` ein und zeigt Live-Daten.
- [ ] Kategorien/Filter werden in der UI eingebunden.
- [ ] Notfallnummern werden mit verifizierten Daten und Offline-Konzept bereitgestellt.
- [ ] Fehler-, Offline- und Ladezustände auf echten Geräten getestet.
- [ ] Barrierefreiheit, sensible Standorte und Datenschutz vor Veröffentlichung geprüft.

## 7. Dokumentation und Nachvollziehbarkeit

Bei jedem abgeschlossenen Feature mindestens folgende Angaben nachtragen: **Zweck**, betroffene Dateien, Endpunkt/JSON-Schema, Testkommando, tatsächliches Testergebnis, bekannte Einschränkungen und Git-Commit/PR (wenn vorhanden). Derzeit sind keine konkreten Commit-IDs als Nachweise in der Dokumentation eingetragen, da sie im Gespräch nicht genannt wurden. Sie sollten nach dem Merge ergänzt werden.

Siehe auch [Architektur](flutter-architektur.md), [Tests](flutter-tests.md) und [Installation](../installation/flutter-setup.md).
