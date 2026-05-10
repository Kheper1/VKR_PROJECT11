USE branch2_db;

-- Филиал 2: логическое удаление читателя.

UPDATE readers SET is_deleted = TRUE WHERE reader_id = 2;

-- Филиал 2: добавление нового читателя.

INSERT INTO readers (reader_id, full_name, birth_date, phone, email, branch_id, is_deleted)
VALUES (5, 'Orlov Dmitry Viktorovich', '1992-11-01', '+7-900-555-55-55', 'orlov@example.com', 2, 0)
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), birth_date = VALUES(birth_date), phone = VALUES(phone), email = VALUES(email), branch_id = VALUES(branch_id), is_deleted = VALUES(is_deleted);
