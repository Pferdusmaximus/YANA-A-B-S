from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from psycopg.rows import dict_row

from database import get_connection
from portal import (
    session_account,
    csrf_token,
    check_csrf,
    password_hash,
    templates,
)


router = APIRouter(
    prefix="/portal",
    include_in_schema=False
)


def render_password_form(
    request,
    account,
    error=None,
    status_code=200,
):
    return templates.TemplateResponse(
        request=request,
        name="portal/passwort_aendern.html",
        context={
            "account": account,
            "csrf_token": csrf_token(request),
            "error": error,
        },
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )


@router.get(
    "/passwort-aendern",
    response_class=HTMLResponse
)
def password_change_page(request: Request):

    account = session_account(request)

    if account is None:
        return RedirectResponse(
            "/portal/login",
            status_code=303
        )

    return render_password_form(
        request,
        account
    )


@router.post("/passwort-aendern")
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_repeat: str = Form(...),
    submitted_csrf: str = Form(
        ...,
        alias="csrf_token"
    ),
):
    account = session_account(request)

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Anmeldung erforderlich"
        )

    check_csrf(request, submitted_csrf)

    # Eingaben kontrollieren
    if not 14 <= len(new_password) <= 128:
        return render_password_form(
            request,
            account,
            error=(
                "Das neue Passwort muss zwischen "
                "14 und 128 Zeichen lang sein."
            ),
            status_code=422
        )

    if new_password != new_password_repeat:
        return render_password_form(
            request,
            account,
            error="Die neuen Passwörter stimmen nicht überein.",
            status_code=422
        )

    if len(current_password) > 1024:
        raise HTTPException(
            status_code=422,
            detail="Ungültige Passworteingabe"
        )

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute(
                """
                SELECT
                    password_hash,
                    is_active
                FROM public.portal_account
                WHERE account_id = %s
                FOR UPDATE
                """,
                (account["account_id"],)
            )

            stored = cur.fetchone()

            if stored is None or not stored["is_active"]:
                raise HTTPException(
                    status_code=401,
                    detail="Account nicht verfügbar"
                )

            if not password_hash.verify(
                current_password,
                stored["password_hash"]
            ):
                return render_password_form(
                    request,
                    account,
                    error="Das bisherige Passwort ist ungültig.",
                    status_code=403
                )

            # Neues Passwort muss sich unterscheiden
            if password_hash.verify(
                new_password,
                stored["password_hash"]
            ):
                return render_password_form(
                    request,
                    account,
                    error=(
                        "Das neue Passwort muss sich "
                        "vom bisherigen unterscheiden."
                    ),
                    status_code=422
                )

            # Passwort ausschließlich gehasht speichern
            new_hash = password_hash.hash(new_password)

            cur.execute(
                """
                UPDATE public.portal_account
                SET
                    password_hash = %s,
                    must_change_password = FALSE,
                    failed_attempts = 0,
                    locked_until = NULL
                WHERE account_id = %s
                """,
                (
                    new_hash,
                    account["account_id"]
                )
            )

            # Alle bestehenden Sitzungen beenden
            cur.execute(
                """
                DELETE FROM public.portal_session
                WHERE account_id = %s
                """,
                (account["account_id"],)
            )

    request.session.clear()

    return RedirectResponse(
        "/portal/login",
        status_code=303
    )