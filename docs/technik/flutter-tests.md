# Flutter-Testkonzept und bestätigte Testergebnisse

**Stand: 27. Oktober 2026 · Unit-Tests und manuelle Live-API-Tests erfolgreich**

Eine zentrale Entscheidung im YANA-Projekt ist die **Trennung von automatisierten, reproduzierbaren Tests und manuellen Live-Verbindungstests**. Diese Trennung wurde eingeführt, nachdem der Flutter-Test-Runner echte HTTP-Anfragen in einem Test mit Statuscode 400 beantwortet hatte.

## 1. Testarten

| Testart | Ordner | Aufruf | Reales Backend nötig? | Projektstatus |
|---|---|---|---|---|
| Controller-Unit-Tests mit Fake-Repositories | `test/` | `flutter.bat test` | Nein | Erfolgreich |
| Manuelle Live-Verbindungstests | `tool/` | `dart run tool/...` | Ja | Erfolgreich |
| Widget-/Screen-Tests der eigentlichen UI | `test/` | `flutter.bat test` | Nein, bei Mocks | Noch zu erweitern |
| Gerätetest der fertigen App | `integration_test/` bzw. Flutter-Gerätetest | Noch festzulegen | Ja bzw. Testumgebung | Noch nicht bestätigt |

**Begriffe:** Der Begriff „Integrationstest“ wird im Projekt leicht missverständlich verwendet. Unsere `tool/`-Dateien sind **manuelle, durchgängige API-Smoke-Tests** über das öffentliche Netzwerk, **keine** offiziell durch `integration_test` orchestrierten UI-/E2E-Tests auf einem Android-Gerät. Diese Abgrenzung ist für die spätere Bewertung und CI sinnvoll.

## 2. Manuelle Live-API-Tests (`tool/`)

Projektverzeichnis: `apps/mobile/`

```powershell
dart run tool/api_connection_test.dart
dart run tool/category_connection_test.dart
dart run tool/emergency_connection_test.dart
```

Die Programme instanziieren jeweils das echte Repository, rufen die FastAPI über den `ApiClient` auf und geben die Ergebnisse im Terminal aus. Beispiel des Hilfestellen-Smoke-Tests:

```dart
// ignore_for_file: avoid_print
import 'package:yana/features/help/data/help_repository.dart';

Future<void> main() async {
  final repository = HelpRepository();
  final facilities = await repository.getHelpFacilities();

  print('Anzahl Hilfestellen: ${facilities.length}');
  for (final facility in facilities) {
    print('${facility.id}: ${facility.name}');
  }
}
```

**Voraussetzungen:** erreichbarer VPS, gültiges HTTPS-Zertifikat, laufender Nginx-/FastAPI-/PostgreSQL-Stack. Im Schulnetzwerk konnte der Zugriff durch eine vorgeschaltete Fortinet-Firewall eingeschränkt sein; die externe Verbindung wurde über einen Mobilfunk-Hotspot erprobt. Das ist **kein** Vorschlag, Sicherheitsrichtlinien des Schulnetzwerks zu umgehen.

### Bestätigte tatsächliche Ergebnisse

| Live-Test | Beobachtung | Interpretation |
|---|---|---|
| `api_connection_test.dart` | `Anzahl Hilfestellen: 2`, Namen der zwei fiktiven Teststellen | HTTP, JSON und `HelpFacility.fromJson()` funktionieren für diese Daten |
| `category_connection_test.dart` | `Anzahl Kategorien: 2`, *Frauenberatung* und *Schutzunterkunft* | Kategorie-Modell und Repository funktionieren |
| `emergency_connection_test.dart` | `Anzahl Notfallnummern: 0`, ohne Exception | Endpunkt erreichbar; eine **leere Liste** wird korrekt behandelt |

**Einschränkung:** Der dritte Test bestätigt das Parsen einer **leeren** Liste, aber **noch nicht** die Konvertierung eines gefüllten `EmergencyContact`-JSON-Datensatzes. Für vollständigen Nachweis sollten ein explizit fiktiver Testkontakt oder ein Mock-Test hinzugefügt werden.

### Umgang mit Konsolenausgaben

Da in den manuellen Diagnosewerkzeugen `print()` beabsichtigt ist, steht dort als erste Zeile:

```dart
// ignore_for_file: avoid_print
```

Damit gilt die Ausnahme nur für diese Dateien; die Lint-Regel bleibt für den übrigen Anwendungscode aktiv. Die Meldung `avoid_print` ist ein **Info-/Lint-Hinweis**, kein Laufzeitfehler.

## 3. Automatisierte Controller-Tests (`test/`)

Ein Controller nimmt ein optionales Repository im Konstruktor entgegen. Dieses Repository kann durch ein Fake ersetzt werden, das bewusst **keine** Netzwerkverbindung aufbaut.

### Beispiel: `HelpController` mit Fake-Daten

Pfad: `test/help_controller_test.dart` (inhaltlicher Auszug aus dem implementierten Muster):

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:yana/features/help/data/help_model.dart';
import 'package:yana/features/help/data/help_repository.dart';
import 'package:yana/features/help/logic/help_controller.dart';

class FakeHelpRepository extends HelpRepository {
  @override
  Future<List<HelpFacility>> getHelpFacilities() async {
    return [
      const HelpFacility(
        id: 1,
        name: 'YANA Test-Beratungsstelle',
        type: 'Beratungsstelle',
        address: 'Musterstraße 1',
        latitude: 49.0134,
        longitude: 12.1016,
        phone: null,
        email: null,
        openingHours: null,
        capacity: 10,
        categoryId: 1,
      ),
    ];
  }
}

class FailingHelpRepository extends HelpRepository {
  @override
  Future<List<HelpFacility>> getHelpFacilities() async {
    throw Exception('Simulierter Verbindungsfehler');
  }
}

void main() {
  test('Startzustand', () {
    final controller = HelpController();
    expect(controller.facilities, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);
    controller.dispose();
  });

  test('Erfolgreicher Ladevorgang', () async {
    final controller = HelpController(repository: FakeHelpRepository());
    await controller.loadFacilities();
    expect(controller.facilities.length, 1);
    expect(controller.facilities.first.name, 'YANA Test-Beratungsstelle');
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);
    controller.dispose();
  });

  test('Fehlerbehandlung', () async {
    final controller = HelpController(repository: FailingHelpRepository());
    await controller.loadFacilities();
    expect(controller.facilities, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNotNull);
    controller.dispose();
  });
}
```

**Analog erfolgreich ausgeführt:** `test/category_controller_test.dart` mit `FakeCategoryRepository` und `YanaCategory` sowie `test/emergency_controller_test.dart` mit `FakeEmergencyRepository` und einem **fiktiven** `EmergencyContact` (`phoneNumber: '000000'`). Die drei Tests je Controller prüfen den Startzustand, erfolgreiche Ergebnisübernahme und Fehlerbehandlung.

### Alle automatisierten Tests starten

```powershell
cd apps/mobile
flutter.bat test
flutter.bat analyze
```

**Bestätigtes Endergebnis:** Nach Entfernung des unpassenden Netzwerk-Tests aus `test/` verliefen `flutter.bat test` und `flutter.bat analyze` ohne Fehler. Es wurde keine produktive Flutter-Oberfläche für diese Tests benötigt.

## 4. Der HTTP-400-Testfehler und seine Lösung

Zunächst lag in `test/help_repository_test.dart` ein Test, der `HelpRepository()` mit dem echten `ApiClient` aufrief. Unter `flutter.bat test` wurde daraus:

```text
Exception: API-Fehler: HTTP 400
Warning: ... TestWidgetsFlutterBinding ...
all HTTP requests will return status code 400
```

Die Testumgebung blockiert echte HTTP-Requests, sodass dieser Test **nicht** beweist, dass der Server fehlerhaft ist. Die echte Verbindung war durch `dart run tool/api_connection_test.dart` bereits erfolgreich nachgewiesen.

**Durchgeführte Korrektur:** `test/help_repository_test.dart` wurde entfernt. Der Live-Test blieb in `tool/api_connection_test.dart`. Controller-Tests in `test/` verwenden Fake-Repositories und greifen nicht auf das Netz zu. Bei künftigen HTTP-bezogenen Unit-Tests sollte ein **injizierbarer, simulierter HTTP-Client** (`http.MockClient`) verwendet werden.

## 5. Testfallmatrix und verbleibende Lücken

| Fall | Hilfestellen | Kategorien | Notfallnummern |
|---|---|---|---|
| API-Abruf über HTTPS | Erfolgreich, 2 Daten | Erfolgreich, 2 Daten | Erfolgreich, 0 Daten |
| Leere API-Liste | Vor Seed auf Serverseite beobachtet | Nicht gesondert berichtet | Erfolgreich beobachtet |
| Controller startet leer | Getestet | Getestet | Getestet |
| Fake-Repository liefert Daten | Getestet | Getestet | Getestet |
| Fake-Repository wirft Fehler | Getestet | Getestet | Getestet |
| Gefüllte HTTP-Antwort direkt über MockClient dekodieren | Noch offen | Noch offen | Noch offen |
| Live-Daten in Flutter-UI anzeigen | Noch offen | Noch offen | Noch offen |
| Gerätebasierter E2E-Test | Noch offen | Noch offen | Noch offen |
| Offline-Fallback | Noch offen | Noch offen | Noch offen |

## 6. Empfehlungen für künftige GitHub Actions

Als **geplanter CI-Workflow** (noch nicht als implementiert dokumentiert) bietet sich an:

```powershell
flutter.bat pub get
flutter.bat analyze
flutter.bat test
```

In Linux-basierten CI-Runnern heißen die Befehle ohne `.bat`: `flutter pub get`, `flutter analyze`, `flutter test`. Die `tool/`-Live-Checks sollten **nicht** ungefragt bei jedem öffentlichen Pull Request gegen den realen VPS laufen; diese bleiben manuell oder werden später gegen eine eigens freigegebene Testumgebung betrieben.

Siehe [Flutter-Fehlerprotokoll](flutter-troubleshooting.md) und [offizielle Flutter-Testübersicht](https://docs.flutter.dev/testing/overview).
