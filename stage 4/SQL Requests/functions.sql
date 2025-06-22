
-- ====================================
-- Fonction : calculate_total_fees
-- ====================================

CREATE OR REPLACE FUNCTION calculate_total_fees(
    acc_id INT, 
    start_period DATE, 
    end_period DATE
) RETURNS NUMERIC AS $$
DECLARE
    total_fees NUMERIC := 0;
BEGIN
    SELECT COALESCE(SUM(tf.amount),0)
    INTO total_fees
    FROM "TransactionFee" tf
    INNER JOIN "Transaction" t ON tf.transaction_id = t.transaction_id
    WHERE t."account_id_FK" = acc_id
      AND t.transaction_date BETWEEN start_period AND end_period
      AND tf.waived = 'NO';

    RETURN total_fees;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors du calcul des frais : %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- ====================================
-- Fonction : get_active_restrictions
-- ====================================

CREATE OR REPLACE FUNCTION get_active_restrictions(acc_id INT)
RETURNS TEXT AS $$
DECLARE
    restriction RECORD;
    result TEXT := '';
    today DATE := CURRENT_DATE;
BEGIN
    FOR restriction IN 
        SELECT "restriction_type", "reason", "start_date", "end_date"
        FROM AccountRestriction
        WHERE "account_id" = acc_id
          AND "start_date" <= today
          AND ("end_date" IS NULL OR "end_date" >= today)
    LOOP
        result := result || FORMAT(
            'Restriction: %s | Raison: %s | Du: %s Au: %s; ',
            restriction.restriction_type,
            restriction.reason,
            restriction.start_date,
            COALESCE(restriction.end_date::TEXT, 'Indéfini')
        );
    END LOOP;

    IF result = '' THEN
        result := 'Aucune restriction active.';
    END IF;

    RETURN result;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors de la vérification des restrictions : %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
