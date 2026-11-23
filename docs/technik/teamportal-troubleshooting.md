# Website und Teamportal: Fehlerprotokoll

**Stand: 18.11.2026.** Diese Tabelle unterscheidet beobachtete Fehlermeldungen von daraus gezogenen Schlussfolgerungen. Wo eine Ursache nicht endgültig überprüft wurde, ist das vermerkt.

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

## Nachträge: Partnerzugriff und Formular (18.11.2026)

- **Partner sieht „Keine Berechtigung“ statt Hilfestellen-Link:** Die Rollenfilterung in Python und PostgreSQL kann korrekt sein, während `templates/portal/dashboard.html` noch `admin`/`team` statt `admin`/`partner` prüft. HTML-Bedingung aktualisieren, danach Dashboard neu laden.
- **CSRF-Token im neuen Formular fehlt:** Kontrollieren, ob `hilfestellen_neu.html` in VS Code gespeichert, zu GitHub gepusht und anschließend in Test-/Produktivverzeichnis kopiert wurde. Im Formular muss `<input type="hidden" name="csrf_token" ...>` vorhanden sein.
- **Router über `app.routes` nicht angezeigt:** Bei der eingesetzten FastAPI-Version können verschachtelte Router in der einfachen Auflistung fehlen. Den tatsächlichen Endpunkt mit `TestClient` prüfen.
- **Änderungsantrag kann nicht freigegeben werden (HTTP 409):** Veröffentlichungsstatus, aktiven Antrag und Vergleich von `base_data` mit aktuellen Daten prüfen; veraltete Daten nicht blind überschreiben.

Die Testkopie greift auf dieselbe PostgreSQL-Instanz zu. Fehlgeschlagene Schreibtests erst anhand von `facility_id`/`change_id` kontrollieren, bevor erneut ausgeführt wird.

## Nachträge: Partner- und Passwortverwaltung (23.11.2026)

| Beobachtung | Diagnose und Lösung |
|---|---|
| `ImportError: cannot import name 'router' from 'portal_partners'` | Datei vorhanden, aber `router = APIRouter(prefix="/portal", include_in_schema=False)` fehlt bzw. falscher Stand kopiert; `grep -nE 'router =|@router' portal_partners.py` prüfen und GitHub-/Testkopie abgleichen. |
| `GET /portal/partner` gibt `404` | `main.py` muss `partners_router` importieren und `app.include_router(partners_router)` ausführen. Danach echten `TestClient` verwenden. |
| Test findet auf der Partnerseite keinen CSRF-Token | `grep -n csrf_token templates/portal/partner.html`; jede zustandsändernde `<form>` benötigt ein verstecktes Eingabefeld. Test-/GitHub-Version vergleichen. |
| Test findet `action="/portal/partner/create"` nicht | Formular fehlt in der übertragenen `partner.html` oder Test prüft zu strenge HTML-Formatierung. Zuerst tatsächliches Formular und korrekte Route prüfen, danach ggf. robuste Pfadprüfung verwenden. |
| Integrationstest mit `EOFError` bei `input()` | Test mit interaktiven Prompts als lokale `.py`-Datei speichern und `python datei.py` ausführen, nicht über stdin-Heredoc. |
| Neuer Partner erhält `403` für Hilfestellen | Bei `must_change_password=TRUE` **erwartet**, bis `/portal/passwort-aendern` erfolgreich durchgeführt wurde. Danach erneut anmelden und Zuordnung prüfen. |
| Nach Reset funktioniert altes Passwort / alte Sitzung nicht | **Erwartet:** Passwort-Hash wurde ersetzt und Sessions wurden gelöscht. Neues Startpasswort einmalig übergeben; Passwortwechsel erzwingen. |
| Statusänderung erfolgreich, Browser zeigt alte Verwaltung | GitHub-Push allein aktualisiert `~/yana-backend` nicht. Dateien erst nach Tests kopieren und `yana-api` neu starten. Browser ggf. neu laden. |

**Achtung:** Bei fehlgeschlagenen Schreibtests zuerst in PostgreSQL prüfen, ob der fiktive Testaccount bereits angelegt oder deaktiviert wurde. Keine Tests wiederholen, die versehentlich einen realen Account überschreiben könnten. Siehe [Partnerverwaltung](teamportal-benutzerverwaltung.md).
