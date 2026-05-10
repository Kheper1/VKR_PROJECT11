CREATE DATABASE IF NOT EXISTS branch3_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE branch3_db;

CREATE TABLE IF NOT EXISTS readers (
    reader_id INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE NULL,
    phone VARCHAR(30) NULL,
    email VARCHAR(255) NULL,
    branch_id INT NOT NULL DEFAULT 3,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_branch3_branch_id CHECK (branch_id = 3),
    CONSTRAINT chk_branch3_email CHECK (email IS NULL OR email LIKE '%@%')
);

INSERT INTO readers (reader_id, full_name, birth_date, phone, email, branch_id, is_deleted)
VALUES
    (3, 'Sidorov Petr Andreevich', '1995-09-10', '+7-900-333-33-33', 'sidorov@example.com', 3, FALSE)
ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    birth_date = VALUES(birth_date),
    phone = VALUES(phone),
    email = VALUES(email),
    branch_id = VALUES(branch_id),
    is_deleted = VALUES(is_deleted);
