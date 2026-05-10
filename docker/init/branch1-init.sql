CREATE DATABASE IF NOT EXISTS branch1_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE branch1_db;

CREATE TABLE IF NOT EXISTS readers (
    reader_id INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE NULL,
    phone VARCHAR(30) NULL,
    email VARCHAR(255) NULL,
    branch_id INT NOT NULL DEFAULT 1,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_branch1_branch_id CHECK (branch_id = 1),
    CONSTRAINT chk_branch1_email CHECK (email IS NULL OR email LIKE '%@%')
);

INSERT INTO readers (reader_id, full_name, birth_date, phone, email, branch_id, is_deleted)
VALUES
    (1, 'Ivanov Ivan Ivanovich', '1990-01-15', '+7-900-111-11-11', 'ivanov@example.com', 1, FALSE)
ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    birth_date = VALUES(birth_date),
    phone = VALUES(phone),
    email = VALUES(email),
    branch_id = VALUES(branch_id),
    is_deleted = VALUES(is_deleted);
