SELECT
    reader_id,
    full_name,
    DATE_FORMAT(birth_date, '%Y-%m-%d') AS birth_date,
    phone,
    email,
    branch_id,
    CAST(is_deleted AS UNSIGNED) AS is_deleted
FROM readers
ORDER BY reader_id;
