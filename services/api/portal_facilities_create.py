"""Neue YANA-Hilfestelle anlegen und optionale öffentliche Adresse geocodieren."""

from pathlib import Path
import re

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from database import get_connection
from geocoding_service import (
    GeocodingError,
    geocode_public_address,
    issue_confirmation,
    normalize_address,
    verify_confirmation,
)
from portal import check_csrf, csrf_token, session_account
from portal_access import require_admin

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter(prefix="/portal", include_in_schema=False)


def get_categories():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT category_id, name FROM public.kategorie ORDER BY name")
            return cur.fetchall()


def type_allows_external_geocoding(facility_type):
    # Fail closed: Einrichtungsarten ohne explizite Freigabe verlassen nie den VPS.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT EXISTS (
                     SELECT 1 FROM public.portal_public_location_type
                     WHERE facility_type = %s
                   )""",
                (facility_type.strip(),),
            )
            return bool(cur.fetchone()[0])


def render_form(request, values=None, error=None, status_code=200, account=None):
    return templates.TemplateResponse(
        request=request,
        name="portal/hilfestellen_neu.html",
        context={
            "values": values or {},
            "categories": get_categories(),
            "csrf_token": csrf_token(request),
            "error": error,
            "account": account,
        },
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )


def validate(values, categories, account_id):
    name = values["name"].strip()
    facility_type = values["facility_type"].strip()
    phone = values["phone"].strip() or None
    email = values["email"].strip() or None
    opening_hours = values["opening_hours"].strip() or None

    if not name or len(name) > 150:
        raise ValueError("Name ist erforderlich (maximal 150 Zeichen).")
    # Bereits bestehende Projektsperre: Keine echten Einrichtungseinträge erstellen.
    if not name.casefold().startswith("yana test"):
        raise ValueError("Nur fiktive YANA-Testeinträge anlegen (Name beginnt mit 'YANA Test').")
    if not facility_type or len(facility_type) > 50:
        raise ValueError("Einrichtungsart ist erforderlich (maximal 50 Zeichen).")
    if phone and len(phone) > 30:
        raise ValueError("Telefonnummer ist zu lang.")
    if email and (len(email) > 150 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)):
        raise ValueError("Bitte eine gültige E-Mail-Adresse eingeben.")
    if opening_hours and len(opening_hours) > 255:
        raise ValueError("Öffnungszeiten sind zu lang.")

    address_fields = normalize_address(
        values["street"], values["housenumber"], values["postcode"], values["city"]
    )
    token = values["geocode_token"].strip()
    lat, lon = verify_confirmation(token, address_fields, facility_type, account_id)
    if token and not type_allows_external_geocoding(facility_type):
        raise ValueError("Diese Einrichtungsart darf nicht extern geocodiert werden.")

    try:
        capacity = int(values["capacity"].strip())
    except ValueError as exc:
        raise ValueError("Kapazität muss eine ganze Zahl sein.") from exc
    if not 0 <= capacity <= 100000:
        raise ValueError("Kapazität muss zwischen 0 und 100000 liegen.")

    category_id = None
    if values["category_id"].strip():
        try:
            category_id = int(values["category_id"].strip())
        except ValueError as exc:
            raise ValueError("Ungültige Kategorie.") from exc
        if category_id not in {item["category_id"] for item in categories}:
            raise ValueError("Die gewählte Kategorie existiert nicht.")

    return {
        "name": name,
        "facility_type": facility_type,
        "address": address_fields["address"],
        "latitude": lat,
        "longitude": lon,
        "capacity": capacity,
        "category_id": category_id,
        "phone": phone,
        "email": email,
        "opening_hours": opening_hours,
    }


@router.get("/hilfestellen/neu", response_class=HTMLResponse)
def new_facility_page(request: Request):
    if session_account(request) is None:
        return RedirectResponse("/portal/login", status_code=303)
    account = require_admin(request)
    return render_form(request, account=account)


@router.post("/hilfestellen/neu/standort-pruefen", response_class=JSONResponse)
def preview_location(
    request: Request,
    facility_type: str = Form(...),
    street: str = Form(""),
    housenumber: str = Form(""),
    postcode: str = Form(""),
    city: str = Form(""),
    non_confidential: str = Form(""),
    submitted_csrf: str = Form(..., alias="csrf_token"),
):
    account = require_admin(request)
    check_csrf(request, submitted_csrf)
    if non_confidential != "yes":
        raise HTTPException(422, "Bitte die öffentliche Unbedenklichkeit der Adresse bestätigen.")

    # Niemals sensible Adressen an den externen Anbieter übertragen.
    if not type_allows_external_geocoding(facility_type):
        raise HTTPException(403, "Diese Einrichtungsart ist für externes Geocoding gesperrt.")
    try:
        fields = normalize_address(street, housenumber, postcode, city)
        result = geocode_public_address(fields)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except GeocodingError as exc:
        raise HTTPException(503, str(exc)) from exc

    token = issue_confirmation(
        fields, facility_type, account["account_id"],
        result["latitude"], result["longitude"],
    )
    return JSONResponse(
        {
            "formatted": result["formatted"],
            "latitude": float(result["latitude"]),
            "longitude": float(result["longitude"]),
            "confidence": result["confidence"],
            "confirmation_token": token,
        },
        headers={"Cache-Control": "no-store"},
    )


@router.post("/hilfestellen/neu")
def create_facility(
    request: Request,
    name: str = Form(...),
    facility_type: str = Form(...),
    street: str = Form(""),
    housenumber: str = Form(""),
    postcode: str = Form(""),
    city: str = Form(""),
    capacity: str = Form(...),
    category_id: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    opening_hours: str = Form(""),
    geocode_token: str = Form(""),
    submitted_csrf: str = Form(..., alias="csrf_token"),
):
    account = require_admin(request)
    check_csrf(request, submitted_csrf)
    values = {
        "name": name, "facility_type": facility_type,
        "street": street, "housenumber": housenumber,
        "postcode": postcode, "city": city,
        "capacity": capacity, "category_id": category_id,
        "phone": phone, "email": email, "opening_hours": opening_hours,
        "geocode_token": geocode_token,
    }
    try:
        cleaned = validate(values, get_categories(), account["account_id"])
    except ValueError as exc:
        return render_form(request, values=values, error=str(exc), status_code=422, account=account)

    # Eine neue Hilfestelle ist immer ein Entwurf und niemals automatisch standortfrei.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.hilfestelle (
                    name, facility_type, address, latitude, longitude,
                    capacity, category_id, phone, email, opening_hours
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING facility_id
                """,
                (
                    cleaned["name"], cleaned["facility_type"], cleaned["address"],
                    cleaned["latitude"], cleaned["longitude"], cleaned["capacity"],
                    cleaned["category_id"], cleaned["phone"], cleaned["email"],
                    cleaned["opening_hours"],
                ),
            )
            facility_id = cur.fetchone()[0]
            audit_data = {
                **cleaned,
                "latitude": str(cleaned["latitude"]) if cleaned["latitude"] is not None else None,
                "longitude": str(cleaned["longitude"]) if cleaned["longitude"] is not None else None,
            }
            cur.execute(
                """
                INSERT INTO public.portal_facility_audit (
                    facility_id, account_id, before_data, after_data, event_type
                ) VALUES (%s, %s, %s, %s, 'created')
                """,
                (facility_id, account["account_id"], Jsonb({}), Jsonb(audit_data)),
            )
    return RedirectResponse(
        f"/portal/hilfestellen/{facility_id}/edit?saved=1",
        status_code=303,
    )
