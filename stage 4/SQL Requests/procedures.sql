
-- ====================================
-- Procédure : update_inactive_accounts
-- ====================================

CREATE OR REPLACE PROCEDURE update_inactive_accounts()
LANGUAGE plpgsql
AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT "account_id"
        FROM "account"
        WHERE "status" = 'active'
          AND NOT EXISTS (
              SELECT 1
              FROM "accountactivity"
              WHERE "account_id" = "account"."account_id"
                AND "activity_date" >= CURRENT_DATE - INTERVAL '180 days'
          )
    LOOP
        UPDATE "account"
        SET "status" = 'inactive'
        WHERE "account_id" = r."account_id";

        RAISE NOTICE 'Compte % marqué inactif', r."account_id";
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur dans update_inactive_accounts : %', SQLERRM;
END;
$$;

-- ====================================
-- Procédure : check_and_block_account_if_overdraft
-- ====================================

CREATE OR REPLACE PROCEDURE check_and_block_overdrafts(
    seuil_negatif NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    rec RECORD;         -- contiendra chaque compte (id + solde)
BEGIN
    -- Parcourir tous les comptes
    FOR rec IN
        SELECT account_id, current_balan
        FROM "account"
    LOOP
        -- Si le solde du compte est en dessous du seuil
        IF rec.current_balan < seuil_negatif THEN

            -- Mettre à jour le statut du compte
            UPDATE "account"
            SET "status" = 'blocked'
            WHERE "account_id" = rec.account_id;

            -- Insérer une restriction dans accountrestriction
            INSERT INTO "accountrestriction" (
                "account_id",
                "restriction_type",
                "start_date",
                "reason"
            ) VALUES (
                rec.account_id,
                'Full',
                CURRENT_DATE,
                'Solde insuffisant (en dessous de ' || seuil_negatif || ')'
            );

            RAISE NOTICE 'Compte % bloqué : solde % < seuil %',
                         rec.account_id, rec.current_balan, seuil_negatif;
        ELSE
            RAISE NOTICE 'Compte % OK (solde %)', rec.account_id, rec.current_balan;
        END IF;
    END LOOP;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur dans check_and_block_overdrafts : %', SQLERRM;
END;
$$;
