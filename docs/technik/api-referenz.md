# HTTP-Schnittstellen: öffentliche API und Webportal

**Stand: 17. November 2026.** FastAPI betreibt auf dem IONOS-VPS sowohl die öffentliche JSON-API für Flutter als auch die HTML-Website und das geschützte Teamportal. Nginx stellt HTTPS bereit. Die Swagger-Oberfläche der öffentlichen API ist unter `/docs` verfügbar; Portal-Routen werden in der OpenAPI-Sicht ausgeblendet.

## Zugriffswege

| Umgebung | Adresse | Zweck |
|---|---|---|
| Uvicorn auf dem VPS | `http://127.0.0.1:8000` | FastAPI intern |
| Nginx intern | `http://127.0.0.1:8080` | Lokaler Proxy-Test |
| Nginx öffentlich | `https://SERVER_IP` | Website, Portal und Flutter-API über TLS |

`SERVER_IP` ist ein Platzhalter; niemals DB-Port `5432` und Uvicorn-Port `8000` ungeschützt veröffentlichen.

## 1. Öffentliche Endpunkte

| Methode | Pfad | Antwort | Status |
|---|---|---|---|
| `GET` | `/` | HTML-Landingpage von Jinja2 | Produktiv im Browser getestet |
| `GET` | `/static/css/style.css` | CSS-Datei | Produktiv geladen |
| `GET` | `/health` | `{"status":"ok"}` | API-Smoke-Test erfolgreich |
| `GET` | `/hilfestellen` | JSON-Liste aus `hilfestelle` | GET-Test erfolgreich; zwei fiktive Einträge |
| `GET` | `/kategorien` | JSON-Liste aus `kategorie` | Zwei fiktive Kategorien |
| `GET` | `/notfallnummern` | JSON-Liste aus `notfallnummer` | GET-Test erfolgreich; aktuell `[]` |
| `GET` | `/docs` | Swagger UI für die API | Vorhanden; Freigabe vor echtem Betrieb prüfen |

### Änderung gegenüber dem ursprünglichen Backend

Früher antwortete `GET /` mit einer JSON-Willkommensmeldung. **Seit der Website-Integration liefert `/` HTML.** Die übrigen GET-API-Endpunkte wurden beim Website-Deployment weiter getestet und beibehalten.

`GET /health` prüft aktuell primär die API-Erreichbarkeit, nicht die vollständige Datenbankgesundheit.

Beispielhafter Ausschnitt einer **fiktiven** Hilfestelle:

```json
{
  "facility_id": 1,
  "name": "YANA Test-Beratungsstelle",
  "facility_type": "Beratungsstelle",
  "address": "Musterstraße 1, Regensburg",
  "latitude": 49.0134,
  "longitude": 12.1016,
  "phone": null,
  "email": null,
  "opening_hours": "Mo-Fr 09:00-17:00 (Testdaten)",
  "capacity": 10,
  "category_id": 1
}
```

Der reale Inhalt kann sich durch Bearbeitungen im Teamportal ändern. Nicht davon ausgehen, dass die Test-Telefonnummer noch gespeichert ist; der Speichertest hat sie wiederhergestellt.

## 2. Geschützte Teamportal-Routen

| Methode | Pfad | Antwort | Voraussetzung |
|---|---|---|---|
| `GET` | `/portal/login` | HTML-Formular mit CSRF | Öffentlich |
| `POST` | `/portal/login` | Bei Erfolg 303 → Dashboard | CSRF, gültiger Account und Passwort |
| `GET` | `/portal/dashboard` | HTML-Dashboard | Gültige Session |
| `POST` | `/portal/logout` | Session löschen, HTTP 303 | CSRF / bestehende Session |
| `GET` | `/portal/hilfestellen` | HTML-Tabelle | `admin` oder `team` |
| `GET` | `/portal/hilfestellen/{facility_id}/edit` | HTML-Formular | `admin` oder `team` |
| `POST` | `/portal/hilfestellen/{facility_id}/edit` | UPDATE + Audit, HTTP 303 bei Erfolg | `admin` oder `team`, CSRF, valide Eingaben |

Anonymes GET auf eine geschützte Seite führt üblicherweise zu **HTTP 303** in Richtung `/portal/login`. Ungültiges CSRF wird mit **403**, ein ungültiges Bearbeitungsformular z. B. mit **422** beantwortet. Ein Account mit Rolle `facility` erhält für die allgemeine Hilfestellenverwaltung **403**.

Das Portal rendert HTML und verwendet Sessions/Cookies. Die Flutter-GET-API ist davon getrennt und benötigt derzeit **keinen** Portal-Login.

## 3. Flutter Web: CORS

Für die lokale Flutter-Web-Entwicklung wurde in `main.py` `CORSMiddleware` ergänzt. Sie erlaubt GET-Zugriffe von `http://localhost` bzw. `http://127.0.0.1` mit wechselnden lokalen Ports; `allow_credentials=False`. Das löst Browser-Origin-Probleme bei lokalen Flutter-Chrome-Tests. Es ist **keine** Freigabe für beliebige Websites und **kein** Ersatz für Backend-Berechtigungen.

```python
# Kern der Entwicklungsregel (Auszug)
allow_origin_regex = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"
```

## 4. Smoke-Tests

```bash
curl -i https://SERVER_IP/
curl -i https://SERVER_IP/health
curl -i https://SERVER_IP/hilfestellen
curl -i https://SERVER_IP/kategorien
curl -i https://SERVER_IP/notfallnummern
curl -i -H 'Origin: http://localhost:54321' https://SERVER_IP/hilfestellen
```

`curl` sendet ohne Browser-Session kein gültiges Portal-Cookie; daher `/portal/dashboard` als anonymer Aufruf typischerweise mit Weiterleitung. Für echte Login-Tests TestClient und Browser verwenden, siehe [Portal-Tests](teamportal-tests.md).

## 5. Noch nicht implementiert

- `POST /portal/hilfestellen/neu` und ein Formular zum **Anlegen** neuer Hilfestellen.
- Löschen, Deaktivieren, Veröffentlichungsfreigabe und Organisationszuordnung.
- Chat-/Nachrichten-API, echte anonyme Erstberatung, Standortsuche und Push.
- Vollständiges Rollen-/Datenschutzkonzept für reale Schutzstandorte.

Mehr unter [Hilfestellenverwaltung](teamportal-hilfestellen.md), [API-Datenzugriff in Flutter](flutter-api-anbindung.md) und [Wiedereinstieg](weiterarbeit.md).
