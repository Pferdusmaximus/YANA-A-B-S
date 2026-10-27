# Flutter/Dart – Fehlerprotokoll und Lösungen

**Stand: 27. Oktober 2026**

Diese Seite enthält die **tatsächlich beobachteten Meldungen** bei der Einrichtung von Flutter, der API-Anbindung und der Testumgebung. Wo die Ursache nicht eindeutig bewiesen wurde, wird dies ausdrücklich gekennzeichnet.

## Chronologischer Überblick

| Situation | Originalmeldung (Auszug) | Befund und tatsächlich wirksamer Schritt |
|---|---|---|
| Flutter-CLI zunächst nicht gefunden | `flutter ... not recognized` | Flutter SDK vorhanden; `.../flutter/bin` zum Benutzer-`PATH` ergänzt, VS Code neu gestartet. |
| `flutter --version` verhielt sich unerwartet | `Could not find an option with short name "-e"` | `flutter.bat --version` funktionierte; weitere Befehle als `flutter.bat ...` ausgeführt. Exakte Ursache der Befehlsauflösung nicht bewiesen. |
| Flutter-Extension-Befehl fehlte | `Flutter: Change SDK` nicht auswählbar | SDK-Pfad direkt im Dateisystem ermittelt; Erweiterungen waren installiert. |
| Projekt unter OneDrive | `Flutter failed to delete a directory ... ios/Flutter/ephemeral/Packages/.packages` | Generierte Projektdateien zu GitHub gepusht, danach lokaler **neuer Klon außerhalb von OneDrive**; `pub get` und `analyze` liefen wieder. |
| Generierte Dateien noch nicht versioniert | `Untracked files: apps/mobile/...` | `git add apps/mobile/`, Commit und Push vor Entfernen des alten lokalen Ordners. |
| Android-Lizenzprüfung | `Android license status unknown` | `flutter doctor --android-licenses` und `sdkmanager.bat --licenses` meldeten, dass `--licenses` nicht mehr nötig sei. Lizenzwarnung blieb; **Android-Debug-APK erfolgreich gebaut**. |
| `android.bat` nicht vorhanden | Pfad zu `cmdline-tools/latest/bin/android.bat` nicht gefunden | Vorhandene Dateien mit PowerShell aufgelistet; `sdkmanager.bat` war vorhanden. Keine unbestätigte CLI erzwungen. |
| Android/Gradle-Extension | `No connection to Gradle server` | Editorhinweis; kein kausal nachgewiesener Buildfehler. Relevanter Gegencheck: `flutter.bat build apk --debug` erfolgreich. |
| Ursprünglicher Flutter-Widget-Test | `The name 'MyApp' isn't a class` | Generierter `widget_test.dart` verwies auf eine nicht vorhandene Demo-Klasse. Durch einen kleinen, zum aktuellen Projekt passenden Platzhaltertest ersetzt. |
| Früher Test lud nicht | `Undefined name 'main'` bzw. `File truncated before or at offset 0x0` | Datei bzw. Speichervorgang überprüft; ein eigenständiger `tool/`-Test mit `Future<void> main()` lief erfolgreich. Ursache der einmaligen Truncation nicht eindeutig bestätigt. |
| Live-HTTP-Anfrage unter `flutter test` | `API-Fehler: HTTP 400` + Warnung zu `TestWidgetsFlutterBinding` | Flutter-Tests blockierten echten HTTP-Request; Live-Test in `tool/` per `dart run` belassen, fehlerhaften `test/help_repository_test.dart` entfernt. |
| Dart-Analyzer meldete viele Hinweise | `info - Don't invoke 'print' in production code` | Bei bewusst manuellen `tool/`-Tests `// ignore_for_file: avoid_print` ergänzt. Es handelte sich um Lint-Hinweise, nicht um fehlgeschlagene API-Abfragen. |
| Modellname `Category` kollidierte | `The name 'Category' is defined in the libraries ...` | Eigenes Datenmodell in **`YanaCategory`** umbenannt. |
| Repository verwendete alten Typ | `The name 'Category' isn't a type` / `Undefined name 'Category'` | `Future<List<YanaCategory>>` und `YanaCategory.fromJson()` eingesetzt. |
| Controller blieb auf altem Typ | `List<YanaCategory> can't be assigned to List<Category>`; `Unused import` | Liste und Getter des `CategoryController` zu `List<YanaCategory>` korrigiert. Danach Analyse erfolgreich. |
| Verfügbare Paketupdates | `8 packages have newer versions incompatible with dependency constraints` | Kein Installationsfehler; Abhängigkeiten wurden trotzdem erfolgreich geladen. Updates später geplant prüfen. |

## Praktische Diagnose in VS Code / PowerShell

Vom Repository-Root in den Flutter-Ordner wechseln:

```powershell
cd apps/mobile
```

Aktuelle Flutter- und SDK-Konfiguration:

```powershell
where.exe flutter
flutter.bat --version
flutter.bat doctor -v
```

Projektbezogene Prüfungen:

```powershell
flutter.bat pub get
flutter.bat analyze
flutter.bat test
flutter.bat build apk --debug
```

**Interpretation:**

- `pub get` erfolgreich = Pub-Abhängigkeiten aufgelöst, **nicht** automatisch ein erfolgreicher Android-Build.
- `analyze` erfolgreich = keine erkannten statischen Probleme, **nicht** automatisch eine erreichbare REST-API.
- `test` erfolgreich = automatisierte Tests bestanden; hier verwenden die Controller-Tests Fake-Repositories.
- `build apk --debug` erfolgreich = Android-Debug-APK gebaut; **nicht** gleichbedeutend mit einem signierten Release oder realem Benutzertest.
- `dart run tool/...` erfolgreich = echte Live-Verbindung über HTTPS für genau den getesteten Endpunkt und Datensatzstand.

## HTTP 400 bei `flutter test` vs. HTTP 400 vom echten Server

Wird die Meldung zusammen mit `TestWidgetsFlutterBinding` und dem Hinweis ausgegeben, dass HTTP-Requests im Test automatisch `400` zurückgeben, handelt es sich **um die Testumgebung**, nicht um die Backendantwort. Ein echter Backend-HTTP-400 muss gesondert durch eine externe Anfrage oder durch Logs untersucht werden.

```powershell
# Echten GET-Request manuell prüfen:
dart run tool/api_connection_test.dart
```

Das tatsächliche Backend hat im dokumentierten Live-Test zwei fiktive Hilfestellen zurückgegeben.

## Kategorie-Typen nach Umbenennung prüfen

Alle beteiligten Dateien müssen **denselben** Dart-Typ verwenden:

```dart
// category_model.dart
class YanaCategory { /* ... */ }

// category_repository.dart
Future<List<YanaCategory>> getCategories() async { /* ... */ }

// category_controller.dart
List<YanaCategory> _categories = [];
List<YanaCategory> get categories => List.unmodifiable(_categories);
```

Der Spaltenname in PostgreSQL bleibt **`kategorie`**, der Endpunkt bleibt **`/kategorien`**. Die Umbenennung betrifft nur die Client-seitige Dart-Klasse.

## Projektverzeichnis und Geheimnisse

Der lokale Entwicklungsordner liegt außerhalb von OneDrive; ein beispielhafter Pfad ist:

```text
%USERPROFILE%\Documents\Programmieren\Projektarbeit\YANA-A-B-S
```

Windows-Benutzernamen und absolute Home-Pfade wurden absichtlich generalisiert. In öffentlichen GitHub-Issues oder Screenshots **keine Passwörter, Tokens, SSH-Schlüssel, Datenbank-Exports oder sensible Standortdaten veröffentlichen**.

Weitere Fehler zum Server, Nginx, Zertifikaten und Backup-Agent stehen im [Server-Fehlerprotokoll](troubleshooting.md). Eine Übersicht der Testarten befindet sich unter [Flutter-Tests](flutter-tests.md).
