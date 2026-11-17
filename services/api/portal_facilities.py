from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row

from database import get_connection
from portal import session_account


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter(
    prefix="/portal",
    include_in_schema=False
)


@router.get(
    "/hilfestellen",
    response_class=HTMLResponse
)
def list_facilities(request: Request):

    # 1. Anmeldung überprüfen
    account = session_account(request)

    if account is None:
        return RedirectResponse(
            "/portal/login",
            status_code=303
        )

    # 2. Berechtigung überprüfen
    if account["role"] not in ("admin", "team"):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung"
        )

    # 3. Hilfestellen aus PostgreSQL laden
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    h.facility_id,
                    h.name,
                    h.facility_type,
                    h.address,
                    h.phone,
                    h.email,
                    h.opening_hours,
                    h.capacity,
                    k.name AS category_name
                FROM public.hilfestelle AS h
                LEFT JOIN public.kategorie AS k
                    ON h.category_id = k.category_id
                ORDER BY h.name ASC
                LIMIT 100
                """
            )

            facilities = cur.fetchall()

    # 4. HTML-Seite darstellen
    return templates.TemplateResponse(
        request=request,
        name="portal/hilfestellen.html",
        context={
            "account": account,
            "facilities": facilities
        },
        headers={"Cache-Control": "no-store"}
    )