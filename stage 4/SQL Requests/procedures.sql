
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

CREATE OR REPLACE PROCEDURE check_and_block_account_if_overdraft(
    acc_id INT,
    seuil_negatif NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    solde NUMERIC;
BEGIN
    -- Vérifier que le compte existe
    IF NOT EXISTS (
        SELECT 1 FROM "account" WHERE "account_id" = acc_id
    ) THEN
        RAISE EXCEPTION 'Le compte % n''existe pas.', acc_id;
    END IF;

    -- Récupérer le solde actuel
    SELECT "current_balan"
    INTO solde
    FROM "account"
    WHERE "account_id" = acc_id;

    -- Si le solde est en dessous du seuil, bloquer le compte
    IF solde < seuil_negatif THEN

        -- Mettre à jour le statut du compte
        UPDATE "account"
        SET "status" = 'blocked'
        WHERE "account_id" = acc_id;

        -- Ajouter une restriction complète
        INSERT INTO "accountrestriction" (
            "account_id",
            "restriction_type",
            "start_date",
            "reason"
        ) VALUES (
            acc_id,
            'Full',
            CURRENT_DATE,
            'Solde insuffisant (en dessous de ' || seuil_negatif || ')'
        );

        RAISE NOTICE 'Compte % bloqué pour dépassement de découvert.', acc_id;

    ELSE
        RAISE NOTICE 'Aucune action nécessaire. Solde actuel : %', solde;
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur dans check_and_block_account_if_overdraft : %', SQLERRM;
END;
$$;
