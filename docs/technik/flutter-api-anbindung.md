# Flutter mit FastAPI verbinden: Modelle, API-Client und Repositories

**Stand: 27. Oktober 2026 · Umgesetzt und mit Live-Daten getestet**

Dieser Abschnitt dokumentiert die Datenzugriffsschicht, die zusätzlich zum bestehenden Python-Backend erstellt wurde. Die App spricht **ausschließlich die FastAPI-REST-API über HTTPS** an, nicht PostgreSQL direkt. Zum Zeitpunkt der Tests wurden zwei Hilfestellen, zwei Kategorien und eine **leere** Notfallnummernliste erfolgreich abgerufen.

## 1. Schnittstellen und Datenfluss

| Dart-Repository | API-Anfrage | PostgreSQL-Tabelle | Live-Test |
|---|---|---|---|
| `HelpRepository` | `GET /hilfestellen` | `hilfestelle` | HTTP-Ergebnis verarbeitet, **2** Datensätze |
| `CategoryRepository` | `GET /kategorien` | `kategorie` | **2** Datensätze |
| `EmergencyRepository` | `GET /notfallnummern` | `notfallnummer` | **0** Datensätze, reguläre leere Liste |

Die drei GET-Endpunkte wurden zuvor in [FastAPI](../installation/fastapi.md) implementiert und sind auch in der [API-Referenz](api-referenz.md) dokumentiert. Keine der drei APIs setzt im aktuellen Teststand Authentifizierung voraus. Das ist für **fiktive öffentliche Testdaten** vertretbar, nicht für später geschützte Chat- und Nutzerdaten.

## 2. HTTP-Abhängigkeit installieren

Im Flutter-Verzeichnis `apps/mobile/`:

```powershell
flutter.bat pub add http
flutter.bat pub get
```

Android-Netzwerkberechtigung in `android/app/src/main/AndroidManifest.xml` prüfen:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <!-- Bestehendes application-Element unverändert belassen. -->
</manifest>
```

Das Beispiel illustriert die **Position** der Berechtigung; nicht die vollständige vorhandene Manifestdatei überschreiben.

## 3. API-Basisadresse (`api_config.dart`)

Pfad: `lib/core/config/api_config.dart`

```dart
class ApiConfig {
  static const String baseUrl = 'https://SERVER_IP';
}
```

**Öffentliches Beispiel:** `SERVER_IP` ist ein Platzhalter. In der tatsächlichen lokalen Entwicklungsdatei ist die HTTPS-Adresse des YANA-Servers einzutragen. Die Basisadresse ist kein Geheimnis, enthält aber **keine** Zugangsdaten oder Tokens. Für mehrere Umgebungen empfiehlt sich später eine über `--dart-define` bzw. Konfiguration auflösbare Adresse.

## 4. Gemeinsamer API-Client (`api_client.dart`)

Pfad: `lib/core/network/api_client.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';

class ApiClient {
  Future<dynamic> get(String endpoint) async {
    final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');

    final response = await http.get(url).timeout(
      const Duration(seconds: 10),
    );

    if (response.statusCode != 200) {
      throw Exception('API-Fehler: HTTP ${response.statusCode}');
    }

    return jsonDecode(utf8.decode(response.bodyBytes));
  }
}
```

**Verantwortung:** URL zusammensetzen, `GET` senden, maximal zehn Sekunden warten, HTTP-Status kontrollieren, Antwort als UTF-8 lesen und JSON dekodieren. Der `ApiClient` kennt **keine** Hilfestellen, Kategorien oder Notfallnummern. Dadurch ist er wiederverwendbar.

**Aktuelle Grenzen:** Die Funktion ist zunächst auf erfolgreiche HTTP-200-GET-Antworten zugeschnitten. Eigene Exception-Typen, Authentifizierungs-Header, Monitoring, Retry-Strategien und robuste Schema-Validierung sind noch nicht implementiert. In produktiven Anwendungen sollten Statuscodes wie 401, 403, 404 und 429 kontrolliert behandelt werden. Ein Timeout kann als Ausnahme weitergegeben werden.

## 5. Model vs. Repository – Unterschied

- **Model**: Beschreibt die Datenstruktur einer Entität und übersetzt JSON in typisierte Dart-Objekte (`fromJson`). Beispiel: Ein `HelpFacility` besitzt `id`, `name`, `address`, `latitude` und weitere Felder.
- **Repository**: Holt Daten für einen fachlichen Bereich über den `ApiClient`, validiert die grundlegende Antwortform und liefert eine `Future<List<Model>>` zurück.
- **Controller**: Wird im [nächsten Kapitel](flutter-architektur.md) erläutert und steuert Ladezustand, Ergebnis und Fehler für die Benutzeroberfläche.

### Zuordnung der JSON-Felder

| DB/JSON-Key | Dart-Typ / Feld | Modell |
|---|---|---|
| `facility_id` | `int id` | `HelpFacility` |
| `facility_type` | `String type` | `HelpFacility` |
| `latitude`, `longitude` | `double latitude`, `double longitude` | `HelpFacility` |
| `category_id` | `int? categoryId` | `HelpFacility`, `EmergencyContact` |
| `category_id` | `int id` | `YanaCategory` |
| `description` | `String? description` | `YanaCategory` |
| `contact_id` | `int id` | `EmergencyContact` |
| `phone_number` | `String phoneNumber` | `EmergencyContact` |

Das Fragezeichen `?` steht in Dart für **nullable**, also einen optionalen Wert. Telefonnummern bleiben Strings, um führende Nullen und `+` zu erhalten.

## 6. Hilfestellen-Model und -Repository

**`lib/features/help/data/help_model.dart`:**

```dart
class HelpFacility {
  final int id;
  final String name;
  final String type;
  final String address;
  final double latitude;
  final double longitude;
  final String? phone;
  final String? email;
  final String? openingHours;
  final int capacity;
  final int? categoryId;

  const HelpFacility({
    required this.id,
    required this.name,
    required this.type,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.phone,
    required this.email,
    required this.openingHours,
    required this.capacity,
    required this.categoryId,
  });

  factory HelpFacility.fromJson(Map<String, dynamic> json) {
    return HelpFacility(
      id: json['facility_id'] as int,
      name: json['name'] as String,
      type: json['facility_type'] as String,
      address: json['address'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      phone: json['phone'] as String?,
      email: json['email'] as String?,
      openingHours: json['opening_hours'] as String?,
      capacity: json['capacity'] as int,
      categoryId: json['category_id'] as int?,
    );
  }
}
```

`latitude` und `longitude` kommen aus PostgreSQL als numerische JSON-Werte und werden mit `(value as num).toDouble()` verlässlich in `double` konvertiert.

**`lib/features/help/data/help_repository.dart`:**

```dart
import '../../../core/network/api_client.dart';
import 'help_model.dart';

class HelpRepository {
  final ApiClient _apiClient;

  HelpRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  Future<List<HelpFacility>> getHelpFacilities() async {
    final data = await _apiClient.get('/hilfestellen');

    if (data is! List) {
      throw const FormatException('Unerwartetes Antwortformat der API');
    }

    return data.map((item) {
      return HelpFacility.fromJson(
        Map<String, dynamic>.from(item as Map),
      );
    }).toList();
  }
}
```

Die optionale Übergabe von `apiClient` ist ein erster Baustein für Dependency Injection. Das Repository greift nicht direkt auf Widgets zu. Das direkte HTTP-Verhalten wird über den gemeinsamen `ApiClient` gekapselt.

## 7. Kategorien-Model und -Repository

Bei der Entwicklung wurde zunächst `Category` als Modellname verwendet. Dieser kollidierte mit einem bereits importierten Typnamen. Der projektspezifische, eindeutige Name lautet deshalb **`YanaCategory`**. Alle Verweise in Model, Repository und Controller müssen übereinstimmen.

**`lib/features/category/data/category_model.dart`:**

```dart
class YanaCategory {
  final int id;
  final String name;
  final String? description;

  const YanaCategory({
    required this.id,
    required this.name,
    this.description,
  });

  factory YanaCategory.fromJson(Map<String, dynamic> json) {
    return YanaCategory(
      id: json['category_id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
    );
  }
}
```

**`lib/features/category/data/category_repository.dart`:**

```dart
import '../../../core/network/api_client.dart';
import 'category_model.dart';

class CategoryRepository {
  final ApiClient _apiClient;

  CategoryRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  Future<List<YanaCategory>> getCategories() async {
    final data = await _apiClient.get('/kategorien');

    if (data is! List) {
      throw const FormatException(
        'Unerwartetes Antwortformat für Kategorien',
      );
    }

    return data.map((item) {
      return YanaCategory.fromJson(
        Map<String, dynamic>.from(item as Map),
      );
    }).toList();
  }
}
```

**Wichtig:** Nach der Umbenennung mussten auch `_categories` und der `categories`-Getter im `CategoryController` auf `List<YanaCategory>` umgestellt werden. Der zuvor aufgetretene Compile-Fehler ist in [Fehlerbehebung](flutter-troubleshooting.md) dokumentiert.

## 8. Notfallnummern-Model und -Repository

**`lib/features/emergency/data/emergency_model.dart`:**

```dart
class EmergencyContact {
  final int id;
  final String name;
  final String phoneNumber;
  final int? categoryId;
  final String description;
  final String availability;

  const EmergencyContact({
    required this.id,
    required this.name,
    required this.phoneNumber,
    this.categoryId,
    required this.description,
    required this.availability,
  });

  factory EmergencyContact.fromJson(Map<String, dynamic> json) {
    return EmergencyContact(
      id: json['contact_id'] as int,
      name: json['name'] as String,
      phoneNumber: json['phone_number'] as String,
      categoryId: json['category_id'] as int?,
      description: json['description'] as String,
      availability: json['availability'] as String,
    );
  }
}
```

**`lib/features/emergency/data/emergency_repository.dart`:**

```dart
import '../../../core/network/api_client.dart';
import 'emergency_model.dart';

class EmergencyRepository {
  final ApiClient _apiClient;

  EmergencyRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  Future<List<EmergencyContact>> getEmergencyContacts() async {
    final data = await _apiClient.get('/notfallnummern');

    if (data is! List) {
      throw const FormatException(
        'Unerwartetes Antwortformat für Notfallnummern',
      );
    }

    return data.map((item) {
      return EmergencyContact.fromJson(
        Map<String, dynamic>.from(item as Map),
      );
    }).toList();
  }
}
```

**Beobachtung:** Der Endpunkt antwortete erfolgreich, die Tabelle war aber leer. Dadurch ist **der HTTP-Pfad und die Behandlung einer leeren Liste** bestätigt, nicht jedoch das JSON-Parsing eines echten Notfallnummern-Datensatzes. Dafür fehlt noch ein ausdrücklich fiktiver Seed-Datensatz oder ein gezielter Repository-Test mit Mockantwort.

## 9. Live-Abfragen, ohne die UI zu verändern

In `apps/mobile/tool/` liegen manuelle Dart-Verbindungstests. Sie werden **mit `dart run`** gestartet, weil sie echte Netzwerkanfragen gegen den VPS senden:

```powershell
cd apps/mobile
dart run tool/api_connection_test.dart
dart run tool/category_connection_test.dart
dart run tool/emergency_connection_test.dart
```

**Tatsächlich bestätigt:** Hilfestellen 2, Kategorien 2, Notfallnummern 0 – bei allen drei Tests erfolgreiche API-Verbindung. Der Live-Test steht ausführlich unter [Teststrategie und Ergebnisse](flutter-tests.md).

## 10. Sicherheits- und Weiterentwicklungshinweise

- Keine SQL-Verbindung oder PostgreSQL-Passwörter in Flutter ablegen.
- Nur die öffentlichen Testdaten-Endpunkte ungeschützt aufrufen; geschützte Daten benötigen künftig **Authentifizierung, Autorisierung und serverseitige Eingabevalidierung**.
- Die im Hilfestellen-Test enthaltenen Schutzunterkunftsadressen sind **fiktiv**. Reale vertrauliche Schutzstandorte nicht unkontrolliert bereitstellen.
- Für Notfallkontakte sollte ein verifizierter **Offline-Fallback** geprüft werden.
- Später typisierte API-Fehler, explizite Response-Modelle, Pagination und einen austauschbaren HTTP-Client ergänzen.

Weitere Informationen: [Controller und Lebenszyklus](flutter-controller.md), [API-Referenz](api-referenz.md), [Betrieb und Sicherheit](betrieb-sicherheit.md).
