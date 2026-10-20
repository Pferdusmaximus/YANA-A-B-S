# FastAPI einrichten und als Dienst betreiben

Ziel: Die in PostgreSQL angelegte Datenbank `app_db` wird über eine lokale FastAPI-REST-Schnittstelle angesprochen. Die API selbst wird dauerhaft von **systemd** betrieben; Nginx und HTTPS sind im [nächsten Kapitel](nginx-https.md) beschrieben.

## 1. Laufzeitumgebung vorbereiten

```bash
python3 --version
sudo apt update
sudo apt install python3-pip python3-venv -y
mkdir -p ~/yana-backend
cd ~/yana-backend
python3 -m venv .venv
source .venv/bin/activate
pip install "fastapi[standard]" "psycopg[binary]" python-dotenv
python -c "import fastapi; print(fastapi.__version__)"
```

Zum Zeitpunkt der Einrichtung wurde **FastAPI 0.150.0** angezeigt. `fastapi[standard]` installiert u. a. den ASGI-Server Uvicorn. `psycopg[binary]` ist der PostgreSQL-Treiber. `python-dotenv` liest lokale Konfigurationswerte ein.

Die Python-Umgebung `.venv` trennt Projektausgaben von den globalen Ubuntu-Paketen. Alle folgenden Python-Dateien liegen im Ordner `~/yana-backend`.

Für spätere Reproduzierbarkeit wird empfohlen, die geprüften Abhängigkeiten in einer `requirements.txt` zu fixieren, z. B. nach erfolgreicher Installation:

```bash
pip freeze > requirements.txt
```

**Hinweis:** Dies war eine ergänzende Dokumentationsempfehlung; die Erstellung dieser Datei wurde im bisherigen Verlauf **noch nicht bestätigt**.

## 2. Konfiguration ohne Klartextpasswort im Repository

Datei `~/yana-backend/.env` **lokal** anlegen:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=app_db
DB_USER=app_user
DB_PASSWORD=PASSWORT_NUR_LOKAL_EINSETZEN
```

Rechte absichern:

```bash
chmod 600 ~/yana-backend/.env
```

`.env` ist bewusst **nicht** Teil dieser öffentlichen Dokumentation oder des exportierten Projektarchivs. Sie wird nicht committet. Die Variablen steuern die DB-Verbindung; `DB_HOST=127.0.0.1` verhindert eine unnötige Netzwerkverbindung ins öffentliche Internet.

Als Git-Schutz (`~/yana-backend/.gitignore`, sofern dort ein Git-Repository angelegt wird) empfiehlt sich:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
```

## 3. Datenbankzugriff kapseln

Datei `~/yana-backend/database.py`:

```python
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    )
```

`get_connection()` erstellt eine neue PostgreSQL-Verbindung mit einem fünfsekündigen Verbindungstimeout. Für die geringe Last im Schulprojekt genügt dieses einfache Vorgehen zunächst; für höheren Durchsatz sollte ein Connection-Pool geprüft werden.

## 4. API-Endpunkte implementieren

Datei `~/yana-backend/main.py` (Stand bis zur abgeschlossenen Servereinrichtung):

```python
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from psycopg import Error
from database import get_connection

app = FastAPI(
    title="YANA API",
    description="Backend für die YANA Sicherheits-App",
    version="1.0.0"
)

@app.get("/")
def startseite():
    return {
        "message": "Willkommen bei der YANA API",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/hilfestellen")
def get_hilfestellen():
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM hilfestelle")
                hilfestellen = cur.fetchall()
        return hilfestellen
    except Error:
        raise HTTPException(
            status_code=503,
            detail="Datenbankabfrage fehlgeschlagen"
        )

@app.get("/kategorien")
def get_kategorien():
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM kategorie")
                kategorien = cur.fetchall()
        return kategorien
    except Error:
        raise HTTPException(
            status_code=503,
            detail="Datenbankabfrage fehlgeschlagen"
        )

@app.get("/notfallnummern")
def get_notfallnummern():
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM notfallnummer")
                nummern = cur.fetchall()
        return nummern
    except Error:
        raise HTTPException(
            status_code=503,
            detail="Datenbankabfrage fehlgeschlagen"
        )
```

Die drei Daten-Endpunkte lesen alle Zeilen aus den jeweiligen Tabellen und geben sie als JSON zurück. Der Kontextmanager schließt die Datenbankverbindung nach Verarbeitung der Anfrage.

!!! warning "Gegenwärtiger Entwicklungsstand"
    Die Endpunkte sind aktuell **ohne Authentifizierung** aufrufbar. `/health` meldet nur die Erreichbarkeit von FastAPI, **nicht** die Funktionsfähigkeit von PostgreSQL. Die vorhandenen Hilfestellen sind fiktive Testdaten; echte Chat-/Nutzerinnen-Daten dürfen so nicht bereitgestellt werden.

## 5. Lokaler Funktionstest

```bash
cd ~/yana-backend
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
```

Im Browser **direkt auf dem VPS** öffnen:

- `http://127.0.0.1:8000/` – Statusmeldung.
- `http://127.0.0.1:8000/health` – `{"status":"ok"}`.
- `http://127.0.0.1:8000/docs` – Swagger/OpenAPI-Dokumentation.

In Swagger wurde `GET /hilfestellen` zunächst mit `HTTP 200` und `[]` (leere Tabelle) getestet. Nach dem Einspielen der [Testdaten](../technik/datenmodell.md#testdaten-entwicklungszwecke) lieferte die API zwei Datensätze und weiterhin `HTTP 200`.

## 6. FastAPI dauerhaft über systemd starten

Die manuelle Uvicorn-Instanz mit `Strg+C` beenden. Aktuellen Benutzer und Projektverzeichnis prüfen:

```bash
whoami
realpath ~/yana-backend
```

Für den eingerichteten VPS waren dies `yana` und `/home/yana/yana-backend`. Der folgende systemd-Dienst verwendet diese Pfade; bei einer Neuinstallation auf einem anderen Server unbedingt anpassen.

Datei `/etc/systemd/system/yana-api.service`:

```ini
[Unit]
Description=YANA FastAPI Backend
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=yana
Group=yana
WorkingDirectory=/home/yana/yana-backend
ExecStart=/home/yana/yana-backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktivieren und kontrollieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now yana-api
sudo systemctl status yana-api
```

**Bestätigtes Ergebnis:** `Active: active (running)` und Swagger weiterhin erreichbar, **ohne** dass Uvicorn manuell in einem Terminal laufen musste.

Wichtige Betriebsbefehle:

```bash
sudo systemctl restart yana-api
sudo systemctl stop yana-api
sudo systemctl start yana-api
sudo journalctl -u yana-api -n 100 --no-pager
```

### Warum nur ein Prozess?

Der Server verfügt über **2 vCores und 4 GB RAM** und betreibt zusätzlich GNOME, PostgreSQL, Nginx und den Backup-Agent. Ein einzelner Uvicorn-Prozess ist für die bisherige Entwicklungs- und Testlast ein ressourcenschonender Ausgangspunkt. Eine spätere Skalierung sollte erst auf Basis von Messwerten erfolgen.
