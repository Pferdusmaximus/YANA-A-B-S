from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from database import get_connection
from portal import check_csrf
from portal_access import require_account


router = APIRouter(
    prefix="/portal",
    include_in_schema=False
)


# Erlaubte Statusübergänge:
# Aktion: (alter Status, neuer Status,
#          erlaubte Rollen, Audit-Ereignis)

ACTIONS = {
    "submit": (
        "draft",
        "pending_review",
        ("admin", "partner"),
        "submitted",
    ),
    "approve": (
        "pending_review",
        "published",
        ("admin",),
        "published",
    ),
    "reject": (
        "pending_review",
        "draft",
        ("admin",),
        "rejected",
    ),
    "unpublish": (
        "published",
        "draft",
        ("admin",),
        "unpublished",
    ),
}


@router.post(
    "/hilfestellen/{facility_id}/status/{action}"
)
def change_facility_status(
    request: Request,
    facility_id: int,
    action: str,
    submitted_csrf: str = Form(
        ...,
        alias="csrf_token"
    ),
):

    # 1. Anmeldung und zulässige Rolle überprüfen
    account = require_account(request)

    # 2. Aktion überprüfen
    rule = ACTIONS.get(action)

    if rule is None:
        raise HTTPException(
            status_code=404,
            detail="Unbekannte Aktion"
        )

    old_status, new_status, roles, event_type = rule

    # 3. Benutzerrolle überprüfen
    if account["role"] not in roles:
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung"
        )

    # 4. CSRF-Schutz
    check_csrf(request, submitted_csrf)

    # 5. Datenbanktransaktion
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            # Datensatz sperren, damit keine
            # parallele Statusänderung dazwischenkommt
            cur.execute(
                """
                SELECT
                    facility_id,
                    name,
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
                (facility_id, account["role"], account["account_id"])
            )

            facility = cur.fetchone()

            if facility is None:
                raise HTTPException(
                    status_code=404,
                    detail="Hilfestelle nicht gefunden"
                )

            # 6. Statusübergang prüfen
            if facility["publication_status"] != old_status:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Aktion für den aktuellen "
                        "Status nicht zulässig"
                    )
                )

            # Solange keine vollständige Prüfung
            # echter Einrichtungen implementiert ist,
            # nur fiktive Testeinträge veröffentlichen.
            if new_status == "published":
                if not facility["name"].casefold().startswith(
                    "yana test"
                ):
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            "Aktuell dürfen nur "
                            "YANA-Testeinträge "
                            "veröffentlicht werden."
                        )
                    )

            # 7. Status aktualisieren
            cur.execute(
                """
                UPDATE public.hilfestelle
                SET publication_status = %s
                WHERE facility_id = %s
                """,
                (
                    new_status,
                    facility_id
                )
            )

            # 8. Änderung protokollieren
            before_data = {
                "name": facility["name"],
                "publication_status": old_status,
            }

            after_data = {
                "name": facility["name"],
                "publication_status": new_status,
            }

            cur.execute(
                """
                INSERT INTO public.portal_facility_audit (
                    facility_id,
                    account_id,
                    event_type,
                    before_data,
                    after_data
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    facility_id,
                    account["account_id"],
                    event_type,
                    Jsonb(before_data),
                    Jsonb(after_data)
                )
            )

    # 9. Zur Übersicht zurückkehren
    return RedirectResponse(
        url="/portal/hilfestellen",
        status_code=303
    )