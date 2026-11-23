from pathlib import Path
import re
import secrets

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row

from database import get_connection
from portal import (
    session_account,
    csrf_token,
    check_csrf,
    password_hash,
)


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

def admin_account(request: Request):
    account = session_account(request)

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Anmeldung erforderlich"
        )

    if account["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Nur für YANA-Administratoren"
        )

    return account


def ensure_partner(cur, account_id: int):
    cur.execute(
        """
        SELECT account_id
        FROM public.portal_account
        WHERE account_id = %s
          AND role = 'partner'
          AND is_active = TRUE
        FOR UPDATE
        """,
        (account_id,)
    )

    if cur.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail="Aktiver Partner nicht gefunden"
        )


# ---------------------------------------
# Partnerverwaltung darstellen
# ---------------------------------------

def render_partner_page(
    request: Request,
    account,
    error=None,
    new_email="",
    status_code=200,
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute(
                """
                SELECT account_id, email, is_active
                FROM public.portal_account
                WHERE role = 'partner'
                ORDER BY email
                """
            )
            partners = cur.fetchall()

            cur.execute(
                """
                SELECT facility_id, name
                FROM public.hilfestelle
                ORDER BY name, facility_id
                """
            )
            facilities = cur.fetchall()

            cur.execute(
                """
                SELECT
                    pfa.account_id,
                    pfa.facility_id,
                    h.name AS facility_name
                FROM public.portal_facility_assignment AS pfa
                JOIN public.portal_account AS a
                    ON a.account_id = pfa.account_id
                JOIN public.hilfestelle AS h
                    ON h.facility_id = pfa.facility_id
                WHERE a.role = 'partner'
                ORDER BY h.name, h.facility_id
                """
            )
            assignments = cur.fetchall()

    assignments_by_account = {
        partner["account_id"]: []
        for partner in partners
    }

    for item in assignments:
        assignments_by_account.setdefault(
            item["account_id"], []
        ).append(item)

    return templates.TemplateResponse(
        request=request,
        name="portal/partner.html",
        context={
            "account": account,
            "partners": partners,
            "facilities": facilities,
            "assignments_by_account": assignments_by_account,
            "csrf_token": csrf_token(request),
            "error": error,
            "new_email": new_email,
        },
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )


@router.get("/partner", response_class=HTMLResponse)
def list_partners(request: Request):
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

    return render_partner_page(request, account)


# ---------------------------------------
# NEU: Partner-Account erstellen
# ---------------------------------------

@router.post(
    "/partner/create",
    response_class=HTMLResponse
)
def create_partner(
    request: Request,
    email: str = Form(...),
    submitted_csrf: str = Form(
        ..., alias="csrf_token"
    ),
):
    # Administratorrechte und CSRF prüfen
    account = admin_account(request)
    check_csrf(request, submitted_csrf)

    email = email.strip().lower()

    if (
        len(email) > 254
        or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        )
    ):
        return render_partner_page(
            request,
            account,
            error="Bitte eine gültige E-Mail-Adresse eingeben.",
            new_email=email,
            status_code=422,
        )

    # Sicheres zufälliges Startpasswort erzeugen
    start_password = secrets.token_urlsafe(24)

    # Nur den Passwort-Hash speichern
    hashed_password = password_hash.hash(
        start_password
    )

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO public.portal_account (
                    email,
                    password_hash,
                    role,
                    is_active,
                    failed_attempts,
                    locked_until,
                    must_change_password
                )
                VALUES (
                    %s, %s, 'partner', TRUE,
                    0, NULL, TRUE
                )
                ON CONFLICT DO NOTHING
                RETURNING account_id
                """,
                (email, hashed_password)
            )

            result = cur.fetchone()

    if result is None:
        return render_partner_page(
            request,
            account,
            error=(
                "Ein Account mit dieser "
                "E-Mail-Adresse existiert bereits."
            ),
            new_email=email,
            status_code=409,
        )

    # Passwort einmalig in der Antwort anzeigen
    return templates.TemplateResponse(
        request=request,
        name="portal/partner_erstellt.html",
        context={
            "account": account,
            "partner_email": email,
            "start_password": start_password,
        },
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
        },
    )


# ---------------------------------------
# Hilfestelle zuweisen
# ---------------------------------------

@router.post("/partner/{account_id}/assign")
def assign_facility(
    request: Request,
    account_id: int,
    facility_id: int = Form(...),
    submitted_csrf: str = Form(
        ..., alias="csrf_token"
    ),
):
    admin_account(request)
    check_csrf(request, submitted_csrf)

    with get_connection() as conn:
        with conn.cursor() as cur:

            ensure_partner(cur, account_id)

            cur.execute(
                """
                SELECT 1
                FROM public.hilfestelle
                WHERE facility_id = %s
                """,
                (facility_id,)
            )

            if cur.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Hilfestelle nicht gefunden"
                )

            cur.execute(
                """
                INSERT INTO public.portal_facility_assignment (
                    account_id,
                    facility_id
                )
                VALUES (%s, %s)
                ON CONFLICT (account_id, facility_id)
                DO NOTHING
                """,
                (account_id, facility_id)
            )

    return RedirectResponse(
        "/portal/partner",
        status_code=303
    )


# ---------------------------------------
# Zuordnung entfernen
# ---------------------------------------

@router.post("/partner/{account_id}/unassign")
def unassign_facility(
    request: Request,
    account_id: int,
    facility_id: int = Form(...),
    submitted_csrf: str = Form(
        ..., alias="csrf_token"
    ),
):
    admin_account(request)
    check_csrf(request, submitted_csrf)

    with get_connection() as conn:
        with conn.cursor() as cur:

            ensure_partner(cur, account_id)

            cur.execute(
                """
                DELETE FROM public.portal_facility_assignment
                WHERE account_id = %s
                  AND facility_id = %s
                """,
                (account_id, facility_id)
            )

    return RedirectResponse(
        "/portal/partner",
        status_code=303
    )


# ---------------------------------------
# Partner deaktivieren
# ---------------------------------------

@router.post("/partner/{account_id}/deactivate")
def deactivate_partner(
    request: Request,
    account_id: int,
    submitted_csrf: str = Form(
        ..., alias="csrf_token"
    ),
):
    admin_account(request)
    check_csrf(request, submitted_csrf)

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Ausschließlich aktive Partner erlauben
            cur.execute(
                """
                SELECT account_id
                FROM public.portal_account
                WHERE account_id = %s
                  AND role = 'partner'
                  AND is_active = TRUE
                FOR UPDATE
                """,
                (account_id,)
            )

            if cur.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Aktiver Partner nicht gefunden"
                )

            # Partner deaktivieren
            cur.execute(
                """
                UPDATE public.portal_account
                SET is_active = FALSE
                WHERE account_id = %s
                """,
                (account_id,)
            )

            # Alle bestehenden Sitzungen beenden
            cur.execute(
                """
                DELETE FROM public.portal_session
                WHERE account_id = %s
                """,
                (account_id,)
            )

    return RedirectResponse(
        "/portal/partner",
        status_code=303
    )


# ---------------------------------------
# Hilfsfunktion:
# Neues Startpasswort festlegen
# ---------------------------------------

def generate_new_start_password(cur, account_id: int):

    # Kryptografisch zufälliges Passwort
    start_password = secrets.token_urlsafe(24)

    # Ausschließlich den Hash speichern
    hashed_password = password_hash.hash(
        start_password
    )

    cur.execute(
        """
        UPDATE public.portal_account
        SET
            password_hash = %s,
            must_change_password = TRUE,
            failed_attempts = 0,
            locked_until = NULL
        WHERE account_id = %s
          AND role = 'partner'
        """,
        (hashed_password, account_id)
    )

    # Bisherige Sitzungen ungültig machen
    cur.execute(
        """
        DELETE FROM public.portal_session
        WHERE account_id = %s
        """,
        (account_id,)
    )

    return start_password


# ---------------------------------------
# Einmalige Passwortanzeige
# ---------------------------------------

def show_start_password(
    request: Request,
    account,
    partner_email: str,
    start_password: str,
    operation: str,
):
    return templates.TemplateResponse(
        request=request,
        name="portal/partner_erstellt.html",
        context={
            "account": account,
            "partner_email": partner_email,
            "start_password": start_password,
            "operation": operation,
        },
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
        },
    )


# ---------------------------------------
# Partner reaktivieren
# ---------------------------------------

@router.post(
    "/partner/{account_id}/reactivate",
    response_class=HTMLResponse
)
def reactivate_partner(
    request: Request,
    account_id: int,
    submitted_csrf: str = Form(
        ..., alias="csrf_token"
    ),
):
    account = admin_account(request)
    check_csrf(request, submitted_csrf)

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute(
                """
                SELECT email, is_active
                FROM public.portal_account
                WHERE account_id = %s
                  AND role = 'partner'
                FOR UPDATE
                """,
                (account_id,)
            )

            partner = cur.fetchone()

            if partner is None:
                raise HTTPException(
                    status_code=404,
                    detail="Partner nicht gefunden"
                )

            if partner["is_active"]:
                raise HTTPException(
                    status_code=409,
                    detail="Partner ist bereits aktiv"
                )

            # Bei Reaktivierung automatisch ein
            # neues Startpasswort festlegen.
            start_password = generate_new_start_password(
                cur, account_id
            )

            cur.execute(
                """
                UPDATE public.portal_account
                SET is_active = TRUE
                WHERE account_id = %s
                """,
                (account_id,)
            )

    return show_start_password(
        request=request,
        account=account,
        partner_email=partner["email"],
        start_password=start_password,
        operation="reactivated",
    )


# ---------------------------------------
# Passwort eines aktiven Partners
# zurücksetzen
# ---------------------------------------

@router.post(
    "/partner/{account_id}/reset-password",
    response_class=HTMLResponse
)
def reset_partner_password(
    request: Request,
    account_id: int,
    submitted_csrf: str = Form(
        ..., alias="csrf_token"
    ),
):
    account = admin_account(request)
    check_csrf(request, submitted_csrf)

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute(
                """
                SELECT email, is_active
                FROM public.portal_account
                WHERE account_id = %s
                  AND role = 'partner'
                FOR UPDATE
                """,
                (account_id,)
            )

            partner = cur.fetchone()

            if partner is None:
                raise HTTPException(
                    status_code=404,
                    detail="Partner nicht gefunden"
                )

            if not partner["is_active"]:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Deaktivierten Partner zuerst "
                        "reaktivieren"
                    )
                )

            start_password = generate_new_start_password(
                cur, account_id
            )

    return show_start_password(
        request=request,
        account=account,
        partner_email=partner["email"],
        start_password=start_password,
        operation="reset",
    )