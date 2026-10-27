# Flutter-/Dart-Entwicklungsumgebung einrichten

**Stand: 27. Oktober 2026 · Zielgruppe: Entwicklerinnen und Entwickler · Plattform: Windows**

Diese Anleitung dokumentiert die tatsächliche Einrichtung des mobilen YANA-Projekts auf einem Windows-Rechner. Sie ergänzt den [Server-Quick-Start](index.md), der Ubuntu, PostgreSQL, FastAPI, Nginx und HTTPS beschreibt. Die mobile Anwendung wird **lokal** entwickelt und greift über HTTPS auf das bereits bestehende Backend zu. Ein direkter PostgreSQL-Zugang vom Mobilgerät ist weder erforderlich noch vorgesehen.

> **Status:** Flutter-Projekt initialisiert, Android-Debug-APK erfolgreich gebaut, Dart-Abhängigkeiten installiert, API-Kommunikation manuell getestet. Die mobile Benutzeroberfläche wird parallel entwickelt; die fachlichen Seiten sind noch nicht vollständig verbunden.

## Voraussetzungen

| Werkzeug | Im Projekt beobachteter Stand | Zweck |
|---|---|---|
| Windows | Windows 11 | Entwicklungsrechner |
| VS Code | Mit aktivierten Erweiterungen **Flutter** und **Dart** | Editor, Debugger |
| Flutter SDK | **3.44.4**, Stable (lokal gemessen) | Mobile Entwicklungsumgebung |
| Dart SDK | **3.12.2** (in Flutter enthalten) | Programmiersprache und CLI |
| Android SDK / Build-Tools | **36.0.0** | Android-Build |
| Git | Vorhanden | Versionsverwaltung |
| Android Studio / Android SDK | SDK-Komponenten vorhanden | SDK-Manager, Android-Toolchain |
| Backend | Bestehende FastAPI unter `https://SERVER_IP` | REST-Datenschnittstelle |

Die Versionsangaben dokumentieren **den damaligen Einrichtungsschritt** und sind keine zwingend festzupinnenden Versionsanforderungen. `SERVER_IP` bezeichnet in öffentlichen Codebeispielen die tatsächliche Serveradresse, nicht ein Passwort.

## 1. Flutter SDK auffinden und im PATH verfügbar machen

Die Flutter-Erweiterung in VS Code ersetzt **nicht** das Flutter SDK. Im Projekt lag das SDK lokal in einem Verzeichnis nach folgendem Muster:

```text
%USERPROFILE%\Documents\Flutter\flutter\bin
```

Dort muss die Datei `flutter.bat` vorhanden sein. Den `bin`-Pfad in Windows unter **Umgebungsvariablen → Benutzervariablen → Path → Neu** ergänzen und VS Code vollständig neu starten.

In PowerShell prüfen:

```powershell
Get-Command flutter
where.exe flutter
flutter.bat --version
```

**Warum `flutter.bat`?** Beim Einrichten wurde `flutter --version` zeitweise mit `Could not find an option with short name "-e"` abgebrochen. Die direkte Batch-Datei funktionierte dagegen einwandfrei. Deshalb nutzen die nachfolgenden Windows-Beispiele ausdrücklich `flutter.bat`.

## 2. Repository außerhalb von OneDrive klonen

Der erste Entwicklungsordner befand sich in einem OneDrive-Synchronisationsverzeichnis. Dort scheiterte `flutter pub get` bzw. `flutter analyze` daran, das generierte iOS-Verzeichnis `ios/Flutter/ephemeral/Packages/.packages` zu löschen. Die Ursache wurde nicht forensisch bewiesen; ein Dateilock bzw. Synchronisationskonflikt war plausibel.

**Wirksame Maßnahme:** Die generierten Flutter-Dateien wurden erst nach GitHub gepusht und das Repository anschließend **neu in ein lokales, nicht synchronisiertes Verzeichnis** geklont. Im Projekt wurde zuletzt ein Ordner unter `Documents/Programmieren/Projektarbeit/` verwendet.

Beispiel für einen reproduzierbaren lokalen Klon:

```powershell
cd "$env:USERPROFILE\Documents\Programmieren\Projektarbeit"
git clone https://github.com/Pferdusmaximus/YANA-A-B-S.git
cd .\YANA-A-B-S
code .
```

Vor dem Entfernen eines alten Arbeitsverzeichnisses unbedingt `git status` prüfen und **alle zu sichernden Änderungen committen und pushen**. Insbesondere die neu erzeugten Dateien unter `apps/mobile/` waren anfangs noch `untracked`.

```powershell
git status
git add apps/mobile/
git status
# Nur nach Kontrolle der gestagten Dateien:
git commit -m "Initialize Flutter project"
git push origin main
```

**Geheimnisschutz:** Vor `git add` kontrollieren, dass keine `.env`-Dateien, Zugangsdaten, privaten Schlüssel oder nutzerbezogenen Exporte in den Commit gelangen. Im Team bevorzugt einen eigenen Feature-Branch und einen Pull Request verwenden; direkte Pushes auf `main` waren nur Teil der anfänglichen Einrichtung.

## 3. Flutter-App im Monorepo initialisieren

Das bestehende YANA-Repository verwendet einen Monorepo-Ansatz. Der Ordner für die App liegt unter `apps/mobile/`.

```powershell
cd apps/mobile
flutter.bat create --platforms=android,ios --project-name yana .
flutter.bat pub get
flutter.bat analyze
```

Der abschließende Punkt `.` erstellt die Dateien **im aktuellen Ordner**. Der Paketname `yana` ist relevant für Dart-Imports der Form `package:yana/...`. Erzeugte Plattformordner sind unter anderem `android/` und `ios/`; außerdem `pubspec.yaml`, `analysis_options.yaml` und `test/widget_test.dart`.

> **iOS:** Die iOS-Projektdateien können auf Windows erzeugt und versioniert werden. Zum Bauen/Signieren einer iOS-App ist später ein macOS-Rechner mit Xcode erforderlich.

## 4. Android-Toolchain kontrollieren

```powershell
flutter.bat doctor
flutter.bat devices
```

Während der Einrichtung waren SDK und Build-Tools **36.0.0** installiert, aber `flutter doctor` meldete `Android license status unknown`. Die üblichen Befehle

```powershell
flutter.bat doctor --android-licenses
& "$env:LOCALAPPDATA\Android\Sdk\cmdline-tools\latest\bin\sdkmanager.bat" --licenses
```

führten lediglich zu `The --licenses option is no longer needed`. Eine in älteren Beispielen angenommene Datei `android.bat` war an diesem Speicherort **nicht vorhanden**. Statt auf Verdacht Komponenten herunterzustufen, wurde ein **realer Android-Debug-Build** ausgeführt:

```powershell
flutter.bat build apk --debug
```

**Ergebnis:** Der Build wurde ohne Fehler abgeschlossen. Die weiterhin bestehende `doctor`-Lizenzwarnung ist zu beobachten; der erfolgreiche Build beweist, dass der verwendete SDK-Stand zumindest die aktuelle Debug-App erzeugen kann. Für Release-Builds müssen die Toolchain und Signierung nochmals kontrolliert werden.

Eine zusätzliche Warnung zu **Visual Studio Desktop Development with C++** betrifft Windows-Desktop-Apps und blockiert den hier angestrebten Android-Build nicht.

## 5. Abhängigkeit für die REST-Schnittstelle installieren

```powershell
cd apps/mobile
flutter.bat pub add http
flutter.bat pub get
```

Damit wird das Paket [`http`](https://pub.dev/packages/http) in `pubspec.yaml` eingetragen. `pubspec.lock` sollte bei dieser Flutter-Anwendung mitversioniert werden, um nachvollziehbare Abhängigkeitsstände im Team zu erhalten. Der Hinweis auf neuere, mit aktuellen Versionsgrenzen inkompatible Pakete ist zunächst lediglich ein **Update-Hinweis**, kein Buildfehler.

In `android/app/src/main/AndroidManifest.xml` innerhalb von `<manifest>` und außerhalb von `<application>` prüfen:

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

Die Verbindung verwendet **HTTPS**. Es ist keine Android-Freigabe für unsicheren HTTP-Cleartext-Traffic erforderlich.

## 6. Qualitätssicherung und erste App-Ausführung

```powershell
flutter.bat analyze
flutter.bat test
flutter.bat build apk --debug
```

Nach Bereinigung der generierten Testdatei und Trennung von Live-Verbindungstests und Unit-Tests liefen `flutter analyze` und `flutter test` erfolgreich. Der Debug-Build wurde ebenfalls bestätigt.

Für ein angeschlossenes Android-Gerät oder den Emulator:

```powershell
flutter.bat devices
flutter.bat run
```

Die tatsächliche **Darstellung der fertigen YANA-Benutzeroberfläche auf dem Mobilgerät** ist im hier dokumentierten Projektstand **noch kein bestätigter Testschritt**. Die Dart-API-Kommunikation wurde bereits separat erfolgreich geprüft; siehe [API-Anbindung](../technik/flutter-api-anbindung.md).

## 7. Wo geht es weiter?

- [Flutter-Datenzugriff und REST-API-Anbindung](../technik/flutter-api-anbindung.md)
- [Drei-Schichtenmodell und Controller](../technik/flutter-architektur.md)
- [Automatisierte Tests und Live-Verbindungstests](../technik/flutter-tests.md)
- [Flutter-Fehlerprotokoll](../technik/flutter-troubleshooting.md)
- [Zusammenarbeit und Übergabe an die UI-Entwicklung](../technik/flutter-teamworkflow.md)
