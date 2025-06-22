
-- programme_principal2.sql
-- Utilise get_transactions_by_status avec refcursor
-- À exécuter dans pgAdmin

DO $$
DECLARE
    cur refcursor;
    rec RECORD;
BEGIN
    -- Appel de la fonction
    cur := get_transactions_by_status(270, 'completed');

    -- Lecture ligne par ligne via le curseur
    LOOP
        FETCH cur INTO rec;
        EXIT WHEN NOT FOUND;
        RAISE NOTICE 'Transaction ID: %, Montant: %, Date: %',
            rec.transaction_id, rec.amount, rec.transaction_date;
    END LOOP;

    -- Fermeture du curseur
    CLOSE cur;
END $$;
