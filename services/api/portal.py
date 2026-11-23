
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import hmac
from pathlib import Path
import secrets

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row
from pwdlib import PasswordHash

from database import get_connection


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter(
    prefix="/portal",
    include_in_schema=False
)

password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash("not-a-real-yana-password")

LOGIN_ERROR = "E-Mail-Adresse oder Passwort ungültig."


# CSRF-Sicherheitstoken erstellen
def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")

    if not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token

    return token


# Sicherheitstoken bei Formularen überprüfen
def check_csrf(request: Request, submitted: str) -> None:
    expected = request.session.get("csrf")

    if (
        not isinstance(expected, str)
        or not hmac.compare_digest(expected, submitted)
    ):
        raise HTTPException(
            status_code=403,
            detail="Ungültiges Sicherheitstoken"
        )


# Login-Seite darstellen
def login_template(
    request: Request,
    error: str | None = None,
    code: int = 200
):
    return templates.TemplateResponse(
        request=request,
        name="portal/login.html",
        context={
            "csrf_token": csrf_token(request),
            "error": error
        },
        status_code=code,
        headers={"Cache-Control": "no-store"}
    )


# Angemeldeten Benutzer ermitteln
def session_account(request: Request):
    sid = request.session.get("sid")

    if not isinstance(sid, str):
        return None

    session_hash = sha256(
        sid.encode("utf-8")
    ).hexdigest()

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    a.account_id,
                    a.email,
                    a.role,
                    a.must_change_password
                FROM public.portal_session s
                JOIN public.portal_account a
                    ON a.account_id = s.account_id
                WHERE s.session_hash = %s
                  AND s.expires_at > NOW()
                  AND a.is_active = TRUE
                """,
                (session_hash,)
            )

            account = cur.fetchone()

    # Ein Benutzer mit Startpasswort darf noch
    # keine regulären Portalfunktionen verwenden.
    if (
        account is not None
        and account["must_change_password"]
        and request.url.path not in (
            "/portal/login",
            "/portal/passwort-aendern",
            "/portal/logout",
        )
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Bitte zuerst das Startpasswort ändern."
            )
        )

    return account


# Login-Seite aufrufen
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    account = session_account(request)

    if account is not None:
        if account["must_change_password"]:
            target = "/portal/passwort-aendern"
        else:
            target = "/portal/dashboard"

        return RedirectResponse(
            target,
            status_code=303
        )

    return login_template(request)


# Login durchführen
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    submitted_csrf: str = Form(..., alias="csrf_token")
):
    check_csrf(request, submitted_csrf)

    email = email.strip().lower()

    if len(email) > 254 or len(password) > 1024:
        return login_template(request, LOGIN_ERROR, 401)

    sid = None

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute(
                """
                SELECT
                    account_id,
                    password_hash,
                    role,
                    is_active,
                    failed_attempts,
                    locked_until,
                    must_change_password
                FROM public.portal_account
                WHERE email = %s
                FOR UPDATE
                """,
                (email,)
            )

            account = cur.fetchone()

            if account is None:
                password_hash.verify(password, dummy_hash)

            elif (
                account["is_active"]
                and account["role"] in ("admin", "partner")
                and (
                    account["locked_until"] is None
                    or account["locked_until"]
                    <= datetime.now(timezone.utc)
                )
            ):
                valid = password_hash.verify(
                    password,
                    account["password_hash"]
                )

                if valid:
                    sid = secrets.token_urlsafe(48)

                    session_hash = sha256(
                        sid.encode("utf-8")
                    ).hexdigest()

                    cur.execute(
                        """
                        INSERT INTO public.portal_session
                            (session_hash, account_id, expires_at)
                        VALUES (
                            %s,
                            %s,
                            NOW() + INTERVAL '30 minutes'
                        )
                        """,
                        (
                            session_hash,
                            account["account_id"]
                        )
                    )

                    cur.execute(
                        """
                        UPDATE public.portal_account
                        SET failed_attempts = 0,
                            locked_until = NULL
                        WHERE account_id = %s
                        """,
                        (account["account_id"],)
                    )

                else:
                    failures = account["failed_attempts"] + 1
                    lock_until = None

                    if failures >= 5:
                        failures = 0
                        lock_until = (
                            datetime.now(timezone.utc)
                            + timedelta(minutes=15)
                        )

                    cur.execute(
                        """
                        UPDATE public.portal_account
                        SET failed_attempts = %s,
                            locked_until = %s
                        WHERE account_id = %s
                        """,
                        (
                            failures,
                            lock_until,
                            account["account_id"]
                        )
                    )

            else:
                password_hash.verify(password, dummy_hash)

    if sid is None:
        return login_template(
            request,
            LOGIN_ERROR,
            401
        )

    request.session.clear()
    request.session["sid"] = sid
    request.session["csrf"] = secrets.token_urlsafe(32)

    target = (
    "/portal/passwort-aendern"
    if account["must_change_password"]
    else "/portal/dashboard"
    )

    return RedirectResponse(
        target,
        status_code=303
    )


# Geschütztes Dashboard
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    account = session_account(request)

    if account is None:
        request.session.clear()

        return RedirectResponse(
            "/portal/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="portal/dashboard.html",
        context={
            "account": account,
            "csrf_token": csrf_token(request)
        },
        headers={"Cache-Control": "no-store"}
    )


# Abmelden
@router.post("/logout")
def logout(
    request: Request,
    submitted_csrf: str = Form(..., alias="csrf_token")
):
    check_csrf(request, submitted_csrf)

    sid = request.session.get("sid")

    if isinstance(sid, str):
        session_hash = sha256(
            sid.encode("utf-8")
        ).hexdigest()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM public.portal_session
                    WHERE session_hash = %s
                    """,
                    (session_hash,)
                )

    request.session.clear()

    return RedirectResponse(
        "/portal/login",
        status_code=303
    )
