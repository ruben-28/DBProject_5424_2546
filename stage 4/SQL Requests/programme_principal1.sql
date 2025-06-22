
-- Programme Principal 1
-- 👉 Calcul du total des frais d’un compte
-- 👉 Blocage automatique si solde trop bas

-- 🔹 Étape 1 : Calcul des frais sur l’année 2025 pour le compte 270
SELECT calculate_total_fees(
    270,                     -- identifiant du compte
    DATE '2025-01-01',       -- début de période
    DATE '2025-12-31'        -- fin de période
) AS total_frais;

-- 🔹 Étape 2 : Blocage du compte si solde < -500
CALL check_and_block_account_if_overdraft(
    270,        -- identifiant du compte
    -500        -- seuil de solde minimal toléré
);
