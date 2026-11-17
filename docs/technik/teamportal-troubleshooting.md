# Website und Teamportal: Fehlerprotokoll

**Stand: 17.11.2026.** Diese Tabelle unterscheidet beobachtete Fehlermeldungen von daraus gezogenen Schlussfolgerungen. Wo eine Ursache nicht endgültig überprüft wurde, ist das vermerkt.

| Situation | Meldung / Beobachtung | Ursache und wirksame Maßnahme |
|---|---|---|
| Flutter Web (Chrome) kann API nicht lesen | In Flutter Chrome „Fehler beim Laden“, Dart-CLI-Test fand 2 Hilfestellen | Browser benötigt CORS-Freigabe für lokale Flutter-Web-Origin; `CORSMiddleware` in `main.py` eingerichtet, `yana-api` neu gestartet. Mobile/Windows-Plattformen sind nicht von derselben Browser-Same-Origin-Policy betroffen |
| CORS-Beispiel mit fehlerhafter Regex | Durch Markdown entstand ein Ausdruck ähnlich `[http://localhost:\d+]` | Für lokale Entwicklung korrekt verankerten Ausdruck `r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"` verwenden |
| Git-Push mehrfach abgewiesen | `! [rejected] main -> main (non-fast-forward)` | Ein anderes Teammitglied hatte zuvor gepusht. Lokalen Status sichern, `git pull --rebase origin main`, Konflikte kontrollieren, anschließend `git push origin main`. Kein `--force` |
| Python-Cache erscheint als Änderung | `modified: services/api/__pycache__/main.cpython-313.pyc` und `portal.cpython-313.pyc` | Vom Syntaxcheck automatisch generierte Cache-Dateien; `.gitignore` im Repo-Root ergänzt und bereits versionierte Dateien mit `git rm --cached` entfernt |
| Backend-Login-Test bricht vor Passworteingabe ab | `EOFError: EOF when reading a line` | `python - <<'PY'` verbraucht Standard-Input für das Skript; `input()`/`getpass()` benötigen anschließende Eingaben. Skript in Datei `login_test_local.py` speichern und mit `python login_test_local.py` ausführen |
| Eingabe Testobjekt-ID | `ValueError: invalid literal for int() with base 10: 'TEST'` | Das Skript erwartete zuerst eine numerische `facility_id` (`1` für die fiktive Beratungsstelle). `TEST` wurde erst in der darauf folgenden Bestätigungsfrage verlangt. Der Abbruch erfolgte vor dem Speichern |
| Bearbeitungsformular lässt sich nicht laden | `portal/hilfestelle_bearbeiten.html not found in search path` | Falscher Template-Verweis im Singular; tatsächliche Datei `templates/portal/hilfestellen_bearbeiten.html` im Plural. Referenz in `portal_facilities.py` korrigiert, Test wieder erfolgreich |
| Login-HTML vor Backend-Fertigstellung | Formular-POST wäre `405 Method Not Allowed` | Die HTML-Seite war bereits implementiert, POST-Route und Sessions noch nicht. Später vollständigen Login ergänzt und getestet |
| Neue GitHub-Änderung nicht auf Website | Browser zeigte alten Stand | Push aktualisiert nur das Repository; separate VPS-Arbeitskopie und produktiver Dateisatz müssen synchronisiert, getestet und ggf. `yana-api` neu gestartet werden |
| `sudo journalctl -u yana-api -n 40 --no-pager` versehentlich eingegeben | Dienstprotokoll erschien | Reiner Leseaufruf, keine System- oder DB-Veränderung |

## Diagnosereihenfolge

```bash
# 1. Dienst und Nginx kontrollieren
sudo systemctl status yana-api --no-pager
sudo nginx -t

# 2. Python-Import und Template-Dateiname kontrollieren
cd ~/yana-backend
source .venv/bin/activate
python -c "from main import app; print('Import OK')"
grep -n 'hilfestellen_bearbeiten.html' portal_facilities.py
ls templates/portal/hilfestellen_bearbeiten.html

# 3. Logs lesen, ohne Daten zu verändern
sudo journalctl -u yana-api -n 40 --no-pager

# 4. Öffentliche API unabhängig prüfen
curl -sS -o /dev/null -w '%{http_code}\n' https://SERVER_IP/hilfestellen
```

### CORS-Prüfung für Flutter Web

```bash
curl -i -H 'Origin: http://localhost:54321' https://SERVER_IP/hilfestellen
```

Erwartet: erfolgreiche Antwort und `Access-Control-Allow-Origin: http://localhost:54321` (bei korrekt geladener CORS-Middleware). Die konfigurierte Freigabe dient lokalen Entwicklungsursprüngen; sie darf nicht pauschal auf alle Origins erweitert werden, nur um Browserfehler zu unterdrücken.

### Vorsicht bei echten Fehlermeldungen

Logs, Tracebacks und Screenshots können reale Daten oder Zugangsinformationen enthalten. Vor dem Teilen personenbezogene Daten und Secrets entfernen. `SERVER_IP` ist in Beispielen nur ein Platzhalter.

Weiterführend: [Git-Workflow](git-deployment.md), [Portal-Tests](teamportal-tests.md), [Server-Fehlerbehebung](troubleshooting.md).
