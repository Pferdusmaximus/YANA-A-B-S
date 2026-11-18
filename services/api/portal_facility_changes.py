"""YANA: Änderungsvorschläge für bereits veröffentlichte Hilfestellen.

Bestehende öffentliche Daten bleiben bis zur Admin-Freigabe unangetastet.
Nur die bereits unterstützten Felder name/phone/email/opening_hours.
"""

import re
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from database import get_connection
from portal import check_csrf, csrf_token
from portal_access import require_account, require_admin

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter(prefix="/portal", include_in_schema=False)

FIELDS = ("name", "phone", "email", "opening_hours")


def current_data(row):
    return {key: row[key] for key in FIELDS}


def validated_data(name, phone, email, opening_hours):
    values = {
        "name": name.strip(),
        "phone": phone.strip() or None,
        "email": email.strip() or None,
        "opening_hours": opening_hours.strip() or None,
    }
    if not values["name"] or len(values["name"]) > 100:
        raise ValueError("Name erforderlich, höchstens 100 Zeichen.")
    if not values["name"].casefold().startswith("yana test"):
        raise ValueError("Bis zur Freigabe echter Daten sind nur YANA-Testeinträge erlaubt.")
    if len(values["phone"] or "") > 30:
        raise ValueError("Telefonnummer zu lang (maximal 30 Zeichen).")
    if len(values["email"] or "") > 150:
        raise ValueError("E-Mail-Adresse zu lang (maximal 150 Zeichen).")
    if values["email"] and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", values["email"]
    ):
        raise ValueError("Bitte eine gültige E-Mail-Adresse eingeben.")
    if len(values["opening_hours"] or "") > 200:
        raise ValueError("Öffnungszeiten zu lang (maximal 200 Zeichen).")
    return values


def accessible_facility(cur, account, facility_id, lock=False):
    # Wichtig: Partnerzuordnung Teil derselben SQL-Abfrage, nicht nur HTML-Filter.
    sql = """
        SELECT h.facility_id, h.name, h.phone, h.email,
               h.opening_hours, h.publication_status
        FROM public.hilfestelle AS h
        WHERE h.facility_id = %s
          AND (%s = 'admin' OR EXISTS (
              SELECT 1 FROM public.portal_facility_assignment AS pfa
              WHERE pfa.facility_id = h.facility_id
                AND pfa.account_id = %s
          ))
    """
    if lock:
        sql += " FOR UPDATE OF h"
    cur.execute(sql, (facility_id, account["role"], account["account_id"]))
    item = cur.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="Hilfestelle nicht gefunden")
    return item


def active_change(cur, facility_id, lock=False):
    sql = """
        SELECT change_id, facility_id, created_by_account_id, status,
               base_data, proposed_data, submitted_at
        FROM public.portal_facility_change
        WHERE facility_id = %s AND status IN ('draft', 'pending_review')
    """
    if lock:
        sql += " FOR UPDATE"
    cur.execute(sql, (facility_id,))
    return cur.fetchone()


def audit(cur, facility_id, account_id, event_type, before, after):
    cur.execute(
        """
        INSERT INTO public.portal_facility_audit
            (facility_id, account_id, event_type, before_data, after_data)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (facility_id, account_id, event_type, Jsonb(before), Jsonb(after)),
    )


def form_page(request, account, facility, proposal=None,
              error=None, status_code=200, values=None, last_result=None):
    editable = proposal is None or proposal["status"] == "draft"
    # Andere berechtigte Accounts derselben Einrichtung sollen keine
    # privaten Entwürfe eines anderen Accounts bearbeiten oder lesen.
    owner = proposal is None or (
        proposal["created_by_account_id"] == account["account_id"]
        or account["role"] == "admin"
    )
    if not owner:
        editable = False
    displayed = values or (
        proposal["proposed_data"] if proposal and owner
        else current_data(facility)
    )
    return templates.TemplateResponse(
        request=request,
        name="portal/aenderung_bearbeiten.html",
        context={
            "account": account,
            "facility": facility,
            "proposal": proposal if owner else None,
            "another_editor": not owner,
            "values": displayed,
            "editable": editable,
            "last_result": last_result,
            "error": error,
            "csrf_token": csrf_token(request),
        },
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )


@router.get("/hilfestellen/{facility_id}/aenderung", response_class=HTMLResponse)
def change_form(request: Request, facility_id: int):
    account = require_account(request)
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            facility = accessible_facility(cur, account, facility_id)
            if facility["publication_status"] != "published":
                raise HTTPException(
                    status_code=409,
                    detail="Änderungsvorschläge sind nur für veröffentlichte Einträge möglich.",
                )
            proposal = active_change(cur, facility_id)
            cur.execute(
                """
                SELECT status, review_note, reviewed_at
                FROM public.portal_facility_change
                WHERE facility_id = %s AND created_by_account_id = %s
                  AND status IN ('approved', 'rejected')
                ORDER BY change_id DESC
                LIMIT 1
                """,
                (facility_id, account["account_id"]),
            )
            last_result = cur.fetchone()
    return form_page(request, account, facility, proposal, last_result=last_result)


@router.post("/hilfestellen/{facility_id}/aenderung")
def save_change(
    request: Request,
    facility_id: int,
    name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    opening_hours: str = Form(""),
    mode: str = Form(...),
    submitted_csrf: str = Form(..., alias="csrf_token"),
):
    account = require_account(request)
    check_csrf(request, submitted_csrf)
    if mode not in ("save", "submit"):
        raise HTTPException(status_code=422, detail="Unbekannte Formularaktion")
    try:
        proposed = validated_data(name, phone, email, opening_hours)
    except ValueError as exc:
        # Formular mit eigenen Eingaben erneut anzeigen (kein Datenbank-Write).
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                facility = accessible_facility(cur, account, facility_id)
                existing = active_change(cur, facility_id)
        if facility["publication_status"] != "published":
            raise HTTPException(status_code=409, detail="Nicht mehr veröffentlicht")
        if existing and existing["status"] == "pending_review":
            raise HTTPException(status_code=409, detail="Bereits in Prüfung")
        if existing and existing["created_by_account_id"] != account["account_id"] and account["role"] != "admin":
            raise HTTPException(status_code=409, detail="Ein anderer Berechtigter bearbeitet diesen Entwurf")
        return form_page(
            request, account, facility, existing, str(exc), 422,
            {"name": name, "phone": phone, "email": email, "opening_hours": opening_hours},
        )

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            facility = accessible_facility(cur, account, facility_id, lock=True)
            if facility["publication_status"] != "published":
                raise HTTPException(status_code=409, detail="Nicht mehr veröffentlicht")
            proposal = active_change(cur, facility_id, lock=True)
            baseline = current_data(facility)
            if proposal is not None:
                if proposal["status"] != "draft":
                    raise HTTPException(status_code=409, detail="Änderung ist bereits in Prüfung")
                if proposal["created_by_account_id"] != account["account_id"] and account["role"] != "admin":
                    raise HTTPException(status_code=409, detail="Entwurf eines anderen Bearbeiters")
                if proposal["base_data"] != baseline:
                    raise HTTPException(status_code=409, detail="Öffentliche Daten haben sich geändert. Entwurf verwerfen und neu beginnen.")
            if proposed == baseline and mode == "submit":
                raise HTTPException(status_code=422, detail="Keine Änderungen gegenüber den veröffentlichten Daten")

            status = "pending_review" if mode == "submit" else "draft"
            if proposal is None:
                cur.execute(
                    """
                    INSERT INTO public.portal_facility_change
                       (facility_id, created_by_account_id, status,
                        base_data, proposed_data, submitted_at)
                    VALUES (%s, %s, %s, %s, %s,
                            CASE WHEN %s = 'pending_review' THEN NOW() ELSE NULL END)
                    RETURNING change_id
                    """,
                    (facility_id, account["account_id"], status,
                     Jsonb(baseline), Jsonb(proposed), status),
                )
                change_id = cur.fetchone()["change_id"]
            else:
                change_id = proposal["change_id"]
                cur.execute(
                    """
                    UPDATE public.portal_facility_change
                    SET proposed_data = %s, status = %s, updated_at = NOW(),
                        submitted_at = CASE WHEN %s = 'pending_review'
                                            THEN NOW() ELSE submitted_at END
                    WHERE change_id = %s
                    """,
                    (Jsonb(proposed), status, status, change_id),
                )
            if mode == "submit":
                audit(cur, facility_id, account["account_id"],
                      "change_submitted",
                      {"change_id": change_id, "status": "draft", "data": baseline},
                      {"change_id": change_id, "status": status, "data": proposed})

    suffix = "submitted" if mode == "submit" else "saved"
    return RedirectResponse(
        f"/portal/hilfestellen/{facility_id}/aenderung?{suffix}=1",
        status_code=303,
    )


@router.post("/hilfestellen/{facility_id}/aenderung/discard")
def discard_change(
    request: Request,
    facility_id: int,
    submitted_csrf: str = Form(..., alias="csrf_token"),
):
    account = require_account(request)
    check_csrf(request, submitted_csrf)
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            facility = accessible_facility(cur, account, facility_id, lock=True)
            proposal = active_change(cur, facility_id, lock=True)
            if proposal is None or proposal["status"] != "draft":
                raise HTTPException(status_code=409, detail="Kein offener Entwurf")
            if proposal["created_by_account_id"] != account["account_id"] and account["role"] != "admin":
                raise HTTPException(status_code=404, detail="Entwurf nicht gefunden")
            cur.execute(
                """
                UPDATE public.portal_facility_change
                SET status = 'cancelled', updated_at = NOW()
                WHERE change_id = %s
                """,
                (proposal["change_id"],),
            )
            audit(cur, facility_id, account["account_id"], "change_cancelled",
                  {"change_id": proposal["change_id"], "status": "draft"},
                  {"change_id": proposal["change_id"], "status": "cancelled"})
    return RedirectResponse("/portal/hilfestellen", status_code=303)


@router.get("/aenderungen", response_class=HTMLResponse)
def review_list(request: Request):
    account = require_admin(request)
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT c.change_id, c.facility_id, c.status,
                       c.base_data, c.proposed_data, c.submitted_at,
                       h.name AS facility_name, a.email AS author_email
                FROM public.portal_facility_change AS c
                JOIN public.hilfestelle AS h ON h.facility_id = c.facility_id
                JOIN public.portal_account AS a
                    ON a.account_id = c.created_by_account_id
                WHERE c.status = 'pending_review'
                ORDER BY c.submitted_at ASC, c.change_id ASC
                LIMIT 100
                """
            )
            changes = cur.fetchall()
    return templates.TemplateResponse(
        request=request,
        name="portal/aenderungen_pruefen.html",
        context={"account": account, "changes": changes,
                 "fields": FIELDS, "csrf_token": csrf_token(request)},
        headers={"Cache-Control": "no-store"},
    )


@router.post("/aenderungen/{change_id}/{decision}")
def review_change(
    request: Request,
    change_id: int,
    decision: str,
    submitted_csrf: str = Form(..., alias="csrf_token"),
    review_note: str = Form(""),
):
    account = require_admin(request)
    check_csrf(request, submitted_csrf)
    if decision not in ("approve", "reject"):
        raise HTTPException(status_code=404, detail="Unbekannte Aktion")
    review_note = review_note.strip()
    if len(review_note) > 500:
        raise HTTPException(status_code=422, detail="Begründung zu lang")

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Einheitliche Sperrreihenfolge in Statusänderung und Freigabe:
            # erst Hilfestelle, dann Änderungsvorschlag (verhindert Deadlocks).
            cur.execute(
                "SELECT facility_id FROM public.portal_facility_change WHERE change_id = %s",
                (change_id,),
            )
            result = cur.fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Antrag nicht gefunden")
            facility_id = result["facility_id"]
            cur.execute(
                """
                SELECT facility_id, name, phone, email, opening_hours,
                       publication_status
                FROM public.hilfestelle
                WHERE facility_id = %s
                FOR UPDATE
                """,
                (facility_id,),
            )
            facility = cur.fetchone()
            if facility is None:
                raise HTTPException(status_code=404, detail="Hilfestelle nicht gefunden")
            cur.execute(
                """
                SELECT change_id, facility_id, status, base_data, proposed_data
                FROM public.portal_facility_change
                WHERE change_id = %s
                FOR UPDATE
                """,
                (change_id,),
            )
            proposal = cur.fetchone()
            if proposal is None or proposal["status"] != "pending_review":
                raise HTTPException(status_code=409, detail="Antrag wurde bereits bearbeitet")
            if proposal["facility_id"] != facility_id:
                raise HTTPException(status_code=409, detail="Antrag wurde verändert")

            if decision == "approve":
                if facility["publication_status"] != "published":
                    raise HTTPException(status_code=409, detail="Hilfestelle nicht mehr veröffentlicht")
                baseline = current_data(facility)
                if baseline != proposal["base_data"]:
                    raise HTTPException(status_code=409, detail="Veröffentlichte Daten wurden zwischenzeitlich geändert")
                proposed = proposal["proposed_data"]
                # Auch beim Freigeben nochmals serverseitig kontrollieren.
                try:
                    checked = validated_data(
                        proposed["name"], proposed.get("phone") or "",
                        proposed.get("email") or "", proposed.get("opening_hours") or "",
                    )
                except (ValueError, KeyError, TypeError) as exc:
                    raise HTTPException(status_code=422, detail="Ungültige Antragsdaten") from exc
                cur.execute(
                    """
                    UPDATE public.hilfestelle
                    SET name = %s, phone = %s, email = %s, opening_hours = %s
                    WHERE facility_id = %s AND publication_status = 'published'
                    """,
                    (checked["name"], checked["phone"], checked["email"],
                     checked["opening_hours"], facility_id),
                )
                event = "change_approved"
                after = {"change_id": change_id, **checked}
                before = {"change_id": change_id, **baseline}
                status = "approved"
            else:
                event = "change_rejected"
                before = {"change_id": change_id, "status": "pending_review"}
                after = {"change_id": change_id, "status": "rejected", "review_note": review_note}
                status = "rejected"

            cur.execute(
                """
                UPDATE public.portal_facility_change
                SET status = %s, review_note = %s,
                    reviewed_by_account_id = %s, reviewed_at = NOW(),
                    updated_at = NOW()
                WHERE change_id = %s
                """,
                (status, review_note or None, account["account_id"], change_id),
            )
            audit(cur, facility_id, account["account_id"], event, before, after)

    return RedirectResponse("/portal/aenderungen", status_code=303)
