-- =========================================================
-- LISTE DE TOUTES LES COLONNES DE TOUS LES TABLEAUX
-- =========================================================

SELECT 
    table_name, 
    ordinal_position as pos,
    column_name, 
    data_type, 
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_schema = 'public'
ORDER BY 
    table_name, 
    ordinal_position;