from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row
from psycopg.errors import UniqueViolation, ForeignKeyViolation

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


def admin_account(request: Request):
    """Nur das YANA-Team darf Partner verwalten."""

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


def ensure_partner(cur, account_id):
    """Prüft, ob der Zielaccount ein Partner ist."""

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


@router.get(
    "/partner",
    response_class=HTMLResponse
)
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

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            # Vorhandene Partner-Accounts
            cur.execute(
                """
                SELECT
                    account_id,
                    email,
                    is_active
                FROM public.portal_account
                WHERE role = 'partner'
                ORDER BY email
                """
            )

            partners = cur.fetchall()

            # Einrichtungen für die Auswahl
            cur.execute(
                """
                SELECT facility_id, name
                FROM public.hilfestelle
                ORDER BY name, facility_id
                """
            )

            facilities = cur.fetchall()

            # Bestehende Zuordnungen
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

    for assignment in assignments:
        assignments_by_account.setdefault(
            assignment["account_id"], []
        ).append(assignment)

    return templates.TemplateResponse(
        request=request,
        name="portal/partner.html",
        context={
            "account": account,
            "partners": partners,
            "facilities": facilities,
            "assignments_by_account": assignments_by_account,
            "csrf_token": csrf_token(request),
        },
        headers={"Cache-Control": "no-store"}
    )


@router.post("/partner/{account_id}/assign")
def assign_facility(
    request: Request,
    account_id: int,
    facility_id: int = Form(...),
    submitted_csrf: str = Form(
        ...,
        alias="csrf_token"
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


@router.post("/partner/{account_id}/unassign")
def unassign_facility(
    request: Request,
    account_id: int,
    facility_id: int = Form(...),
    submitted_csrf: str = Form(
        ...,
        alias="csrf_token"
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