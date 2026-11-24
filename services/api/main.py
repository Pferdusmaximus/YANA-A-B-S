import os

from portal_facilities import router as facilities_router
from portal_facilities_status import router as status_router
from portal_facility_changes import router as changes_router
from portal_facilities_create import router as facilities_create_router
from portal_partners import router as partners_router
from portal_password import router as password_router
from portal_locations import router as locations_router

from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

from fastapi.middleware.cors import CORSMiddleware

from portal import router as portal_router

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

app.include_router(facilities_router)
app.include_router(facilities_create_router)
app.include_router(status_router)
app.include_router(changes_router)
app.include_router(partners_router)
app.include_router(password_router)
app.include_router(locations_router)

load_dotenv()

session_secret = os.getenv("PORTAL_SESSION_SECRET")

if not session_secret or len(session_secret) < 32:
    raise RuntimeError(
        "PORTAL_SESSION_SECRET fehlt oder ist zu kurz."
    )

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="yana_portal_session",
    max_age=1800,
    same_site="strict",
    https_only=True
)


# CORS für lokale Flutter-Web-Entwicklung
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["GET"],
    allow_headers=["*"],
    allow_credentials=False,
)


app.include_router(portal_router)

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

                cur.execute(
                    """
                    SELECT
                        h.facility_id,
                        h.name,
                        h.facility_type,

                        -- Adresse nur veröffentlichen,
                        -- wenn beide Freigaben vorliegen.
                        CASE
                            WHEN h.is_location_public IS TRUE
                             AND allowed.facility_type IS NOT NULL
                            THEN h.address
                            ELSE NULL
                        END AS address,

                        -- Breitengrad schützen
                        CASE
                            WHEN h.is_location_public IS TRUE
                             AND allowed.facility_type IS NOT NULL
                            THEN h.latitude
                            ELSE NULL
                        END AS latitude,

                        -- Längengrad schützen
                        CASE
                            WHEN h.is_location_public IS TRUE
                             AND allowed.facility_type IS NOT NULL
                            THEN h.longitude
                            ELSE NULL
                        END AS longitude,

                        h.phone,
                        h.email,
                        h.opening_hours,
                        h.capacity,
                        h.category_id

                    FROM public.hilfestelle AS h

                    LEFT JOIN public.portal_public_location_type
                        AS allowed
                        ON allowed.facility_type = h.facility_type

                    WHERE h.publication_status = 'published'

                    ORDER BY h.name ASC
                    """
                )

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
