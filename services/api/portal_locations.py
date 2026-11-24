from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row

from database import get_connection
from portal import session_account, csrf_token, check_csrf


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter(
    prefix="/portal",
    include_in_schema=False
)


# ---------------------------------------
# Administratorberechtigung
# ---------------------------------------

def require_admin(request: Request):
    account = session_account(request)

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Anmeldung erforderlich"
        )

    if account["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Nur für Administratoren"
        )

    return account


# ---------------------------------------
# Standortfreigaben anzeigen
# ---------------------------------------

@router.get(
    "/standorte",
    response_class=HTMLResponse
)
def location_management(request: Request):

    account = session_account(request)

    if account is None:
        return RedirectResponse(
            "/portal/login",
            status_code=303
        )

    if account["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung"
        )

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute(
                """
                SELECT
                    h.facility_id,
                    h.name,
                    h.facility_type,
                    h.publication_status,
                    h.address,
                    h.latitude,
                    h.longitude,
                    h.is_location_public,
                    (
                        allowed.facility_type IS NOT NULL
                    ) AS type_allowed

                FROM public.hilfestelle AS h

                LEFT JOIN
                    public.portal_public_location_type AS allowed
                    ON allowed.facility_type = h.facility_type

                ORDER BY h.name, h.facility_id
                """
            )

            facilities = cur.fetchall()

    for facility in facilities:
        address = facility["address"]

        has_address = bool(
            address and address.strip()
        )

        has_coordinates = (
            facility["latitude"] is not None
            and facility["longitude"] is not None
        )

        facility["has_location"] = (
            has_address or has_coordinates
        )

        facility["can_approve"] = (
            facility["type_allowed"]
            and facility["publication_status"] == "published"
            and facility["has_location"]
        )

    return templates.TemplateResponse(
        request=request,
        name="portal/standorte.html",
        context={
            "account": account,
            "facilities": facilities,
            "csrf_token": csrf_token(request),
        },
        headers={"Cache-Control": "no-store"},
    )


# ---------------------------------------
# Standort öffentlich freigeben
# ---------------------------------------

@router.post("/standorte/{facility_id}/freigeben")
def approve_location(
    request: Request,
    facility_id: int,
    submitted_csrf: str = Form(
        ...,
        alias="csrf_token"
    ),
):
    require_admin(request)
    check_csrf(request, submitted_csrf)

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            # Datensatz während der Prüfung sperren
            cur.execute(
                """
                SELECT
                    h.facility_id,
                    h.facility_type,
                    h.publication_status,
                    h.address,
                    h.latitude,
                    h.longitude,
                    (
                        SELECT COUNT(*)
                        FROM public.portal_public_location_type AS t
                        WHERE t.facility_type = h.facility_type
                    ) AS allowed_count

                FROM public.hilfestelle AS h
                WHERE h.facility_id = %s

                FOR UPDATE
                """,
                (facility_id,)
            )

            facility = cur.fetchone()

            if facility is None:
                raise HTTPException(
                    status_code=404,
                    detail="Hilfestelle nicht gefunden"
                )

            # Einrichtungsart muss zugelassen sein
            if facility["allowed_count"] != 1:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Standortfreigabe für diese "
                        "Einrichtungsart nicht erlaubt"
                    )
                )

            # Nur veröffentlichte Einrichtungen
            if facility["publication_status"] != "published":
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Hilfestelle muss zuerst "
                        "veröffentlicht werden"
                    )
                )

            has_address = bool(
                facility["address"]
                and facility["address"].strip()
            )

            has_coordinates = (
                facility["latitude"] is not None
                and facility["longitude"] is not None
            )

            if not (has_address or has_coordinates):
                raise HTTPException(
                    status_code=409,
                    detail="Keine Standortdaten vorhanden"
                )

            # Freigabe speichern
            cur.execute(
                """
                UPDATE public.hilfestelle
                SET is_location_public = TRUE
                WHERE facility_id = %s
                """,
                (facility_id,)
            )

    return RedirectResponse(
        "/portal/standorte",
        status_code=303
    )


# ---------------------------------------
# Standortfreigabe zurücknehmen
# ---------------------------------------

@router.post("/standorte/{facility_id}/sperren")
def revoke_location(
    request: Request,
    facility_id: int,
    submitted_csrf: str = Form(
        ...,
        alias="csrf_token"
    ),
):
    require_admin(request)
    check_csrf(request, submitted_csrf)

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE public.hilfestelle
                SET is_location_public = FALSE
                WHERE facility_id = %s
                RETURNING facility_id
                """,
                (facility_id,)
            )

            if cur.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Hilfestelle nicht gefunden"
                )

    return RedirectResponse(
        "/portal/standorte",
        status_code=303
    )