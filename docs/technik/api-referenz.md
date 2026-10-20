# REST-API: Referenz (aktueller Stand)

Die REST-API wird mit **FastAPI 0.150.0** implementiert und durch **Uvicorn** bereitgestellt. Nginx übernimmt den öffentlichen HTTPS-Zugang. Die Swagger-Dokumentation wird automatisch unter `/docs` aus dem OpenAPI-Schema erzeugt.

## Zugriffswege

| Umgebung | Basisadresse | Zugriff |
|---|---|---|
| Uvicorn direkt | `http://127.0.0.1:8000` | Nur VPS-intern |
| Nginx intern | `http://127.0.0.1:8080` | Nur VPS-intern |
| Nginx extern | `https://SERVER_IP` | Öffentlich via HTTPS |

`SERVER_IP` ist ein **Platzhalter** für die öffentliche IPv4 des IONOS-VPS. Bitte nicht als DNS-Namen interpretieren. **PostgreSQL ist nicht direkt extern freigegeben.**

## Implementierte Endpunkte

| Methode | Endpunkt | Zweck | Authentifizierung | Status |
|---|---|---|---|---|
| `GET` | `/` | Willkommens- und Statusmeldung | Nein | Getestet |
| `GET` | `/health` | Erreichbarkeit FastAPI | Nein | Getestet |
| `GET` | `/hilfestellen` | Alle Hilfestellen abrufen | Nein | Getestet |
| `GET` | `/kategorien` | Alle Kategorien abrufen | Nein | Getestet |
| `GET` | `/notfallnummern` | Alle Notfallkontakte abrufen | Nein | Endpunkt vorhanden; Tabelle anfangs leer |
| `GET` | `/docs` | Interaktive Swagger-Dokumentation | Nein | Getestet |

Die eigentlichen Routen sind in [`main.py`](../installation/fastapi.md#4-api-endpunkte-implementieren) definiert.

## `GET /`

**Antwort:** `200 OK`

```json
{
  "message": "Willkommen bei der YANA API",
  "status": "online"
}
```

## `GET /health`

**Antwort:** `200 OK`

```json
{"status":"ok"}
```

Dieser Endpunkt prüft aktuell **nur**, ob FastAPI antwortet. Es wird keine gesonderte DB-Abfrage ausgeführt.

## `GET /hilfestellen`

Liest alle Datensätze aus der Tabelle `hilfestelle` (`SELECT * FROM hilfestelle`). Nach dem Einspielen von zwei Testeinträgen wurde folgender **beispielhafter Auszug** zurückgegeben:

```json
[
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
]
```

Die reale Testantwort enthält **zwei** Datensätze; das Beispiel zeigt aus Platzgründen nur einen. Vor dem Einfügen der Testdaten lautete die Antwort `[]` bei HTTP-Status 200.

## `GET /kategorien`

Liest `SELECT * FROM kategorie` aus. Erwarteter Antwortauszug nach dem Seed-Skript:

```json
[
  {
    "category_id": 1,
    "name": "Frauenberatung",
    "description": "Beratungsangebote für Frauen"
  },
  {
    "category_id": 2,
    "name": "Schutzunterkunft",
    "description": "Schutz und vorübergehende Unterbringung"
  }
]
```

## `GET /notfallnummern`

Liest die Tabelle `notfallnummer`. Solange noch keine Kontakte eingefügt wurden, lautet die Rückgabe:

```json
[]
```

**Wichtig:** Es wurden noch keine fachlich verifizierten Notfallnummern in der öffentlichen App freigegeben. Eine leere Liste ist daher derzeit erwartbar.

## Fehlerantwort bei DB-Problemen

Bei einem von Psycopg erfassten Datenbankfehler gibt FastAPI derzeit zurück:

**HTTP 503 Service Unavailable**

```json
{"detail":"Datenbankabfrage fehlgeschlagen"}
```

Diese generische Meldung verhindert, dass interne SQL- oder DB-Verbindungsdetails an externe Clients ausgegeben werden. Andere nicht behandelte Fehler können derzeit zu `500 Internal Server Error` führen.

## API per curl testen

Lokal auf dem VPS:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8080/hilfestellen
```

Extern (nur wenn HTTPS gültig eingerichtet):

```bash
curl -i https://SERVER_IP/hilfestellen
```

Für HTTPS **nicht** `curl -k` verwenden, weil damit die Zertifikatsprüfung umgangen würde.

## Nicht implementierte Endpunkte

Insbesondere die folgenden Funktionen sind **noch nicht Teil des bestätigten API-Standes**:

- Chat starten, Nachrichten senden und abrufen.
- Authentifizierung, anonyme Erstberatung und differenzierte Rechte.
- POST/PUT/PATCH/DELETE für Administrationsdaten.
- Geoabfragen und Filterung nach Nutzerstandort.
- Uploads, Echtzeitkommunikation und Push-Benachrichtigungen.

Für diese Funktionen müssen Anforderungs-, Datenschutz-, Sicherheits- und Testkonzept erweitert werden, bevor echte Nutzerinnen die Anwendung verwenden.
