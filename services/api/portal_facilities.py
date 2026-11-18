import re
from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)
from fastapi.templating import Jinja2Templates

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from database import get_connection
from portal import (
    session_account,
    check_csrf,
    csrf_token,
)


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter(
    prefix="/portal",
    include_in_schema=False,
)


# Bestehender Name aus Kompatibilitaetsgruenden beibehalten.
# Admins und Partner duerfen das Portal benutzen; einzelne
# Einrichtungen werden zusaetzlich per SQL gefiltert.
def get_staff_account(request: Request):
    account = session_account(request)
    if account is not None and account["role"] not in ("admin", "partner"):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    return account


# Bearbeitungsformular darstellen
def edit_template(
    request,
    facility,
    error=None,
    saved=False,
    status_code=200,
):
    return templates.TemplateResponse(
        request=request,
        name="portal/hilfestellen_bearbeiten.html",
        context={
            "facility": facility,
            "csrf_token": csrf_token(request),
            "error": error,
            "saved": saved,
        },
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )


# ---------------------------------------
# Hilfestellenübersicht
# ---------------------------------------

@router.get(
    "/hilfestellen",
    response_class=HTMLResponse,
)
def list_facilities(request: Request):

    account = get_staff_account(request)

    if account is None:
        return RedirectResponse(
            "/portal/login",
            status_code=303,
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
                    h.phone,
                    h.email,
                    h.opening_hours,
                    h.capacity,
                    k.name AS category_name
                FROM public.hilfestelle AS h
                LEFT JOIN public.kategorie AS k
                    ON h.category_id = k.category_id
                WHERE (
                    %s = 'admin'
                    OR EXISTS (
                        SELECT 1
                        FROM public.portal_facility_assignment AS pfa
                        WHERE pfa.account_id = %s
                          AND pfa.facility_id = h.facility_id
                    )
                )
                ORDER BY h.name ASC
                LIMIT 100
                """,
                (account["role"], account["account_id"]),
            )

            facilities = cur.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="portal/hilfestellen.html",
        context={
            "account": account,
            "facilities": facilities,
            "csrf_token": csrf_token(request),
        },
        headers={"Cache-Control": "no-store"},
    )


# ---------------------------------------
# Einzelne Hilfestelle bearbeiten
# ---------------------------------------

@router.get(
    "/hilfestellen/{facility_id}/edit",
    response_class=HTMLResponse,
)
def edit_facility_page(
    request: Request,
    facility_id: int,
    saved: str | None = None,
):

    account = get_staff_account(request)

    if account is None:
        return RedirectResponse(
            "/portal/login",
            status_code=303,
        )

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    facility_id,
                    name,
                    phone,
                    email,
                    opening_hours,
                    publication_status
                FROM public.hilfestelle AS h
                WHERE h.facility_id = %s
                  AND (
                      %s = 'admin'
                      OR EXISTS (
                          SELECT 1
                          FROM public.portal_facility_assignment AS pfa
                          WHERE pfa.account_id = %s
                            AND pfa.facility_id = h.facility_id
                      )
                  )
                """,
                (facility_id, account["role"], account["account_id"]),
            )

            facility = cur.fetchone()

    if facility is None:
        raise HTTPException(
            status_code=404,
            detail="Hilfestelle nicht gefunden",
        )

    if facility["publication_status"] != "draft":
        raise HTTPException(
            status_code=409,
            detail=(
                "Nur Entwürfe dürfen bearbeitet werden. "
                "Die Hilfestelle muss gegebenenfalls "
                "zuerst zurückgewiesen oder die "
                "Veröffentlichung zurückgenommen werden."
            ),
        )

    return edit_template(
        request=request,
        facility=facility,
        saved=(saved == "1"),
    )


# ---------------------------------------
# Änderungen speichern
# ---------------------------------------

@router.post(
    "/hilfestellen/{facility_id}/edit",
)
def save_facility(
    request: Request,
    facility_id: int,
    name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    opening_hours: str = Form(""),
    submitted_csrf: str = Form(
        ...,
        alias="csrf_token",
    ),
):

    account = get_staff_account(request)

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Anmeldung erforderlich",
        )

    # CSRF-Schutz
    check_csrf(request, submitted_csrf)

    # Eingaben normalisieren
    new_data = {
        "name": name.strip(),
        "phone": phone.strip() or None,
        "email": email.strip() or None,
        "opening_hours": (
            opening_hours.strip() or None
        ),
    }

    error = None

    # Serverseitige Validierung
    if not new_data["name"]:
        error = "Bitte einen Namen eingeben."

    elif len(new_data["name"]) > 100:
        error = "Der Name ist zu lang."

    elif len(new_data["phone"] or "") > 30:
        error = "Die Telefonnummer ist zu lang."

    elif len(new_data["email"] or "") > 150:
        error = "Die E-Mail-Adresse ist zu lang."

    elif (
        new_data["email"]
        and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            new_data["email"],
        )
    ):
        error = "Bitte eine gültige E-Mail-Adresse eingeben."

    elif len(new_data["opening_hours"] or "") > 200:
        error = "Die Öffnungszeiten sind zu lang."

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            # Eintrag während der Änderung sperren
            cur.execute(
                """
                SELECT
                    facility_id,
                    name,
                    phone,
                    email,
                    opening_hours,
                    publication_status
                FROM public.hilfestelle AS h
                WHERE h.facility_id = %s
                  AND (
                      %s = 'admin'
                      OR EXISTS (
                          SELECT 1
                          FROM public.portal_facility_assignment AS pfa
                          WHERE pfa.account_id = %s
                            AND pfa.facility_id = h.facility_id
                      )
                  )
                FOR UPDATE OF h
                """,
                (facility_id, account["role"], account["account_id"]),
            )

            facility = cur.fetchone()

            if facility is None:
                raise HTTPException(
                    status_code=404,
                    detail="Hilfestelle nicht gefunden",
                )

            if facility["publication_status"] != "draft":
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Nur Entwürfe dürfen bearbeitet werden. "
                        "Die Hilfestelle muss gegebenenfalls "
                        "zuerst zurückgewiesen oder die "
                        "Veröffentlichung zurückgenommen werden."
                    ),
                )

            if error:
                return edit_template(
                    request=request,
                    facility={
                        "facility_id": facility_id,
                        **new_data,
                    },
                    error=error,
                    status_code=422,
                )

            # Vorherigen Zustand sichern
            before_data = {
                "name": facility["name"],
                "phone": facility["phone"],
                "email": facility["email"],
                "opening_hours": facility["opening_hours"],
            }

            # Nur bei Änderungen speichern
            if before_data != new_data:

                cur.execute(
                    """
                    UPDATE public.hilfestelle
                    SET
                        name = %s,
                        phone = %s,
                        email = %s,
                        opening_hours = %s
                    WHERE facility_id = %s
                    """,
                    (
                        new_data["name"],
                        new_data["phone"],
                        new_data["email"],
                        new_data["opening_hours"],
                        facility_id,
                    ),
                )

                # Änderung protokollieren
                cur.execute(
                    """
                    INSERT INTO public.portal_facility_audit (
                        facility_id,
                        account_id,
                        before_data,
                        after_data
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        facility_id,
                        account["account_id"],
                        Jsonb(before_data),
                        Jsonb(new_data),
                    ),
                )

    # Zur Bearbeitungsseite zurückkehren
    return RedirectResponse(
        url=(
            f"/portal/hilfestellen/"
            f"{facility_id}/edit?saved=1"
        ),
        status_code=303,
    )
