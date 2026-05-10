USE branch3_db;

-- Филиал 3: обновление email существующего читателя.

UPDATE readers SET email = 'sidorov.new@example.com' WHERE reader_id = 3;

-- Филиал 3: добавление нового читателя.

INSERT INTO readers (reader_id, full_name, birth_date, phone, email, branch_id, is_deleted)
VALUES (6, 'Morozova Elena Igorevna', '1999-07-07', '+7-900-666-66-66', 'morozova@example.com', 3, 0)
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), birth_date = VALUES(birth_date), phone = VALUES(phone), email = VALUES(email), branch_id = VALUES(branch_id), is_deleted = VALUES(is_deleted);
