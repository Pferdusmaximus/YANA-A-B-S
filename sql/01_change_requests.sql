-- YANA / Änderungsvorschläge für veröffentlichte Hilfestellen.
-- Vor Ausführung: pg_dump-Backup erstellen. In app_db über pgAdmin ausführen.
-- Fügt ausschließlich eine neue Tabelle, Indexe und Berechtigungen hinzu.
BEGIN;
DO $$
DECLARE
    account_type text;
    facility_type text;
BEGIN
    SELECT atttypid::regtype::text INTO account_type
    FROM pg_attribute
    WHERE attrelid = 'public.portal_account'::regclass
      AND attname = 'account_id' AND NOT attisdropped;

    SELECT atttypid::regtype::text INTO facility_type
    FROM pg_attribute
    WHERE attrelid = 'public.hilfestelle'::regclass
      AND attname = 'facility_id' AND NOT attisdropped;

    IF account_type NOT IN ('integer', 'bigint')
       OR facility_type NOT IN ('integer', 'bigint') THEN
        RAISE EXCEPTION 'Unerwarteter Typ: account_id %, facility_id %',
                        account_type, facility_type;
    END IF;

    IF to_regclass('public.portal_facility_change') IS NOT NULL THEN
        RAISE EXCEPTION 'portal_facility_change existiert bereits. Schema prüfen, nicht erneut ausführen.';
    END IF;

    EXECUTE format($ddl$
        CREATE TABLE public.portal_facility_change (
            change_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            facility_id %s NOT NULL
                REFERENCES public.hilfestelle(facility_id) ON DELETE RESTRICT,
            created_by_account_id %s NOT NULL
                REFERENCES public.portal_account(account_id) ON DELETE RESTRICT,
            status VARCHAR(20) NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'pending_review',
                                 'approved', 'rejected', 'cancelled')),
            base_data JSONB NOT NULL,
            proposed_data JSONB NOT NULL,
            review_note VARCHAR(500),
            reviewed_by_account_id %s
                REFERENCES public.portal_account(account_id) ON DELETE RESTRICT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            submitted_at TIMESTAMPTZ,
            reviewed_at TIMESTAMPTZ
        )
    $ddl$, facility_type, account_type, account_type);
END $$;

-- Pro Hilfestelle höchstens ein aktiver Entwurf oder Prüfantrag.
CREATE UNIQUE INDEX portal_facility_change_one_open
ON public.portal_facility_change (facility_id)
WHERE status IN ('draft', 'pending_review');

CREATE INDEX portal_facility_change_review_queue
ON public.portal_facility_change (submitted_at, change_id)
WHERE status = 'pending_review';

GRANT SELECT, INSERT, UPDATE
ON public.portal_facility_change TO app_user;

-- Die Identitätsspalte benötigt keine zusätzlichen Rechte auf die Sequenz.
COMMIT;

-- Kontrolle nach Migration:
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'portal_facility_change'
ORDER BY ordinal_position;
