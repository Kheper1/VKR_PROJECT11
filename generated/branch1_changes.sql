USE branch1_db;

-- Филиал 1: обновление существующего читателя.

UPDATE readers SET phone = '+7-900-111-99-99', email = 'ivanov.updated@example.com' WHERE reader_id = 1;

-- Филиал 1: добавление нового читателя.

INSERT INTO readers (reader_id, full_name, birth_date, phone, email, branch_id, is_deleted)
VALUES (4, 'Kuznetsova Maria Pavlovna', '2001-03-12', '+7-900-444-44-44', 'kuznetsova@example.com', 1, 0)
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), birth_date = VALUES(birth_date), phone = VALUES(phone), email = VALUES(email), branch_id = VALUES(branch_id), is_deleted = VALUES(is_deleted);
