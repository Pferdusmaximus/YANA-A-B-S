from pathlib import Path
from fastapi.staticfiles import StaticFiles
from website import router as website_router

from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from psycopg import Error
from database import get_connection

app = FastAPI(
    title="YANA API",
    description="Backend für die YANA Sicherheits-App",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

app.include_router(website_router)

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
