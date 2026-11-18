
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from database import get_connection
from portal import check_csrf, csrf_token, session_account
from portal_access import require_admin


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter(
    prefix="/portal",
    include_in_schema=False
)


# Verfügbare Kategorien aus PostgreSQL laden
def get_categories():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT category_id, name
                FROM public.kategorie
                ORDER BY name
                """
            )
            return cur.fetchall()


# HTML-Formular darstellen
def render_form(
    request,
    values=None,
    error=None,
    status_code=200
):
    return templates.TemplateResponse(
        request=request,
        name="portal/hilfestellen_neu.html",
        context={
            "values": values or {},
            "categories": get_categories(),
            "csrf_token": csrf_token(request),
            "error": error
        },
        status_code=status_code,
        headers={"Cache-Control": "no-store"}
    )


# Geografische Koordinaten prüfen
def parse_coordinate(raw, label, lower, upper):
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError):
        raise ValueError(
            f"{label} muss eine Zahl sein."
        ) from None

    if not value.is_finite() or not lower <= value <= upper:
        raise ValueError(
            f"{label} muss zwischen {lower} und {upper} liegen."
        )

    if value.as_tuple().exponent < -7:
        raise ValueError(
            f"{label} darf maximal 7 Nachkommastellen haben."
        )

    return value


# Eingaben validieren
def validate(values, categories):
    name = values["name"].strip()
    facility_type = values["facility_type"].strip()
    address = values["address"].strip()
    phone = values["phone"].strip() or None
    email = values["email"].strip() or None
    opening_hours = values["opening_hours"].strip() or None

    if not name or len(name) > 150:
        raise ValueError(
            "Name ist erforderlich (maximal 150 Zeichen)."
        )

    # Solange ein Freigabesystem fehlt:
    # Ausschließlich gekennzeichnete Testdaten
    if not name.casefold().startswith("yana test"):
        raise ValueError(
            "Vorerst dürfen nur fiktive YANA-Testeinträge "
            "angelegt werden. Der Name muss mit "
            "'YANA Test' beginnen."
        )

    if not facility_type or len(facility_type) > 50:
        raise ValueError(
            "Typ ist erforderlich (maximal 50 Zeichen)."
        )

    if not address or len(address) > 255:
        raise ValueError(
            "Adresse ist erforderlich (maximal 255 Zeichen)."
        )

    if phone and len(phone) > 30:
        raise ValueError("Telefonnummer ist zu lang.")

    if email and (
        len(email) > 150
        or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", email
        )
    ):
        raise ValueError(
            "Bitte eine gültige E-Mail-Adresse eingeben."
        )

    if opening_hours and len(opening_hours) > 255:
        raise ValueError("Öffnungszeiten sind zu lang.")

    latitude = parse_coordinate(
        values["latitude"].strip(),
        "Breitengrad", -90, 90
    )

    longitude = parse_coordinate(
        values["longitude"].strip(),
        "Längengrad", -180, 180
    )

    try:
        capacity = int(values["capacity"].strip())
    except ValueError:
        raise ValueError(
            "Kapazität muss eine ganze Zahl sein."
        ) from None

    if not 0 <= capacity <= 100000:
        raise ValueError(
            "Kapazität muss zwischen 0 und 100000 liegen."
        )

    category_id = None

    if values["category_id"].strip():
        try:
            category_id = int(
                values["category_id"].strip()
            )
        except ValueError:
            raise ValueError(
                "Ungültige Kategorie."
            ) from None

        valid_ids = {
            category["category_id"]
            for category in categories
        }

        if category_id not in valid_ids:
            raise ValueError(
                "Die gewählte Kategorie existiert nicht."
            )

    return {
        "name": name,
        "facility_type": facility_type,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "capacity": capacity,
        "category_id": category_id,
        "phone": phone,
        "email": email,
        "opening_hours": opening_hours
    }


# Formular öffnen
@router.get(
    "/hilfestellen/neu",
    response_class=HTMLResponse
)
def new_facility_page(request: Request):
    if session_account(request) is None:
        return RedirectResponse("/portal/login", status_code=303)

    # Nur das YANA-Team darf neue Einrichtungen anlegen.
    require_admin(request)
    return render_form(request)


# Neue Hilfestelle speichern
@router.post("/hilfestellen/neu")
def create_facility(
    request: Request,
    name: str = Form(...),
    facility_type: str = Form(...),
    address: str = Form(...),
    latitude: str = Form(...),
    longitude: str = Form(...),
    capacity: str = Form(...),
    category_id: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    opening_hours: str = Form(""),
    submitted_csrf: str = Form(
        ..., alias="csrf_token"
    )
):
    account = require_admin(request)
    check_csrf(request, submitted_csrf)

    values = {
        "name": name,
        "facility_type": facility_type,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "capacity": capacity,
        "category_id": category_id,
        "phone": phone,
        "email": email,
        "opening_hours": opening_hours
    }

    try:
        cleaned = validate(
            values, get_categories()
        )
    except ValueError as error:
        return render_form(
            request,
            values=values,
            error=str(error),
            status_code=422
        )

    # INSERT und Audit in einer Transaktion
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.hilfestelle (
                    name,
                    facility_type,
                    address,
                    latitude,
                    longitude,
                    capacity,
                    category_id,
                    phone,
                    email,
                    opening_hours
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                RETURNING facility_id
                """,
                (
                    cleaned["name"],
                    cleaned["facility_type"],
                    cleaned["address"],
                    cleaned["latitude"],
                    cleaned["longitude"],
                    cleaned["capacity"],
                    cleaned["category_id"],
                    cleaned["phone"],
                    cleaned["email"],
                    cleaned["opening_hours"]
                )
            )

            facility_id = cur.fetchone()[0]

            audit_data = {
                **cleaned,
                "latitude": str(cleaned["latitude"]),
                "longitude": str(cleaned["longitude"])
            }

            cur.execute(
                """
                INSERT INTO public.portal_facility_audit (
                    facility_id,
                    account_id,
                    before_data,
                    after_data,
                    event_type
                )
                VALUES (%s, %s, %s, %s, 'created')
                """,
                (
                    facility_id,
                    account["account_id"],
                    Jsonb({}),
                    Jsonb(audit_data)
                )
            )

    return RedirectResponse(
        f"/portal/hilfestellen/{facility_id}/edit?saved=1",
        status_code=303
    )