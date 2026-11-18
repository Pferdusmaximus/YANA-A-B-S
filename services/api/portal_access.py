from fastapi import HTTPException, Request
from database import get_connection
from portal import session_account


def require_account(request: Request):
    """Prüft, ob ein zulässiger Portal-Account angemeldet ist."""

    account = session_account(request)

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Anmeldung erforderlich"
        )

    if account["role"] not in ("admin", "partner"):
        raise HTTPException(
            status_code=403,
            detail="Unzulässige Benutzerrolle"
        )

    return account


def require_admin(request: Request):
    """Erlaubt ausschließlich YANA-Administratoren."""

    account = require_account(request)

    if account["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Nur für YANA-Administratoren"
        )

    return account


def can_access_facility(account, facility_id: int):
    """Prüft die Zuordnung einer Hilfestelle zum Account."""

    if account["role"] == "admin":
        return True

    if account["role"] != "partner":
        return False

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM public.portal_facility_assignment
                    WHERE account_id = %s
                      AND facility_id = %s
                )
                """,
                (
                    account["account_id"],
                    facility_id
                )
            )

            return bool(cur.fetchone()[0])


def require_facility_access(request: Request, facility_id: int):
    """Erlaubt nur Zugriff auf zugewiesene Einrichtungen."""

    account = require_account(request)

    if not can_access_facility(account, facility_id):
        raise HTTPException(
            status_code=404,
            detail="Hilfestelle nicht gefunden"
        )

    return account