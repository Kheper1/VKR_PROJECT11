CREATE DATABASE IF NOT EXISTS center_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE center_db;

CREATE TABLE IF NOT EXISTS readers (
    reader_id INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE NULL,
    phone VARCHAR(30) NULL,
    email VARCHAR(255) NULL,
    branch_id INT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_center_branch_id CHECK (branch_id IN (1, 2, 3)),
    CONSTRAINT chk_center_email CHECK (email IS NULL OR email LIKE '%@%')
);

CREATE TABLE IF NOT EXISTS consolidation_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    source_branch_id INT NOT NULL,
    reader_id INT NOT NULL,
    operation_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    message VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_readers_before_insert;
DROP TRIGGER IF EXISTS trg_readers_before_update;

DELIMITER //

CREATE TRIGGER trg_readers_before_insert
BEFORE INSERT ON readers
FOR EACH ROW
BEGIN
    IF NEW.full_name IS NULL OR TRIM(NEW.full_name) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'full_name cannot be empty';
    END IF;
END//

CREATE TRIGGER trg_readers_before_update
BEFORE UPDATE ON readers
FOR EACH ROW
BEGIN
    IF NEW.full_name IS NULL OR TRIM(NEW.full_name) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'full_name cannot be empty';
    END IF;
END//

DELIMITER ;

INSERT INTO readers (reader_id, full_name, birth_date, phone, email, branch_id, is_deleted)
VALUES
    (1, 'Ivanov Ivan Ivanovich', '1990-01-15', '+7-900-111-11-11', 'ivanov@example.com', 1, FALSE),
    (2, 'Petrova Anna Sergeevna', '1988-05-20', '+7-900-222-22-22', 'petrova@example.com', 2, FALSE),
    (3, 'Sidorov Petr Andreevich', '1995-09-10', '+7-900-333-33-33', 'sidorov@example.com', 3, FALSE)
ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    birth_date = VALUES(birth_date),
    phone = VALUES(phone),
    email = VALUES(email),
    branch_id = VALUES(branch_id),
    is_deleted = VALUES(is_deleted);
