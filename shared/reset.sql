-- =====================================================
-- Script: reset.sql
-- Description: Complete reset of clinic_db database
-- Usage: mysql -u root -p < shared/reset.sql
-- Warning: This will DROP all data and recreate database!
-- =====================================================

-- Prompt user for confirmation (when run interactively)
SELECT '=============================================' AS '';
SELECT 'WARNING: This will DROP clinic_db database!' AS '';
SELECT 'All data will be permanently deleted!' AS '';
SELECT '=============================================' AS '';
SELECT SLEEP(3) AS 'Starting in 3 seconds...';

-- Store current user for privilege restoration
SET @current_user = USER();

-- =====================================================
-- STEP 1: Drop existing database and connections
-- =====================================================

-- Kill any active connections to clinic_db
DELIMITER $$

DROP PROCEDURE IF EXISTS kill_clinic_connections$$
CREATE PROCEDURE kill_clinic_connections()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE conn_id INT;
    DECLARE cur CURSOR FOR
        SELECT id FROM information_schema.processlist
        WHERE db = 'clinic_db' AND id != CONNECTION_ID();
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO conn_id;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET @sql = CONCAT('KILL ', conn_id);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END LOOP;

    CLOSE cur;
END$$

DELIMITER ;

-- Execute connection killer
CALL kill_clinic_connections();
DROP PROCEDURE kill_clinic_connections;

-- Drop the database if it exists
DROP DATABASE IF EXISTS clinic_db;

SELECT 'Database clinic_db dropped successfully' AS 'Status';

-- =====================================================
-- STEP 2: Recreate database with proper settings
-- =====================================================

-- Create database with UTF8MB4 for full Unicode support
CREATE DATABASE clinic_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT = 'Clinic Management System Database';

SELECT 'Database clinic_db created successfully' AS 'Status';

-- =====================================================
-- STEP 3: Set database defaults
-- =====================================================

-- Use the new database
USE clinic_db;

-- Set session defaults for this script
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection = utf8mb4;

-- Set SQL mode for strict data integrity
SET sql_mode = 'TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY';

-- =====================================================
-- STEP 4: Create clinic_admin user if not exists
-- =====================================================

-- Check if user exists and create/update accordingly
DELIMITER $$

DROP PROCEDURE IF EXISTS create_clinic_admin$$
CREATE PROCEDURE create_clinic_admin()
BEGIN
    DECLARE user_exists INT DEFAULT 0;

    -- Check if user exists
    SELECT COUNT(*) INTO user_exists
    FROM mysql.user
    WHERE user = 'clinic_admin' AND host = 'localhost';

    IF user_exists = 0 THEN
        -- Create new user
        CREATE USER 'clinic_admin'@'localhost'
        IDENTIFIED BY 'Cl1n1c@dm1n2024!'
        PASSWORD EXPIRE NEVER
        COMMENT 'Clinic database administrator';

        SELECT 'User clinic_admin created successfully' AS 'Status';
    ELSE
        -- Update existing user password
        ALTER USER 'clinic_admin'@'localhost'
        IDENTIFIED BY 'Cl1n1c@dm1n2024!';

        SELECT 'User clinic_admin password updated' AS 'Status';
    END IF;

    -- Grant privileges on clinic_db
    GRANT ALL PRIVILEGES ON clinic_db.* TO 'clinic_admin'@'localhost';

    -- Grant ability to create routines
    GRANT CREATE ROUTINE, ALTER ROUTINE, EXECUTE ON clinic_db.* TO 'clinic_admin'@'localhost';

    -- Grant ability to create temporary tables
    GRANT CREATE TEMPORARY TABLES ON clinic_db.* TO 'clinic_admin'@'localhost';

    -- Grant ability to lock tables
    GRANT LOCK TABLES ON clinic_db.* TO 'clinic_admin'@'localhost';

    -- Grant ability to create views
    GRANT CREATE VIEW, SHOW VIEW ON clinic_db.* TO 'clinic_admin'@'localhost';

    -- Grant ability to create triggers
    GRANT TRIGGER ON clinic_db.* TO 'clinic_admin'@'localhost';

    -- Grant ability to use events
    GRANT EVENT ON clinic_db.* TO 'clinic_admin'@'localhost';

    FLUSH PRIVILEGES;

    SELECT 'Privileges granted to clinic_admin' AS 'Status';
END$$

DELIMITER ;

CALL create_clinic_admin();
DROP PROCEDURE create_clinic_admin;

-- =====================================================
-- STEP 5: Create metadata tables
-- =====================================================

-- Create database metadata table
CREATE TABLE IF NOT EXISTS db_metadata (
    property_name VARCHAR(50) PRIMARY KEY,
    property_value VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Database metadata and versioning information';

-- Insert metadata
INSERT INTO db_metadata (property_name, property_value) VALUES
    ('database_version', '1.0.0'),
    ('created_date', DATE_FORMAT(NOW(), '%Y-%m-%d')),
    ('created_by', @current_user),
    ('character_set', 'utf8mb4'),
    ('collation', 'utf8mb4_unicode_ci'),
    ('reset_count', '1')
ON DUPLICATE KEY UPDATE
    property_value = VALUES(property_value),
    updated_at = NOW();

-- Create migration history table
CREATE TABLE IF NOT EXISTS migration_history (
    migration_id INT AUTO_INCREMENT PRIMARY KEY,
    script_name VARCHAR(255) NOT NULL,
    execution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INT,
    executed_by VARCHAR(100),
    status ENUM('SUCCESS', 'FAILED', 'PARTIAL') DEFAULT 'SUCCESS',
    error_message TEXT,
    INDEX idx_execution_date (execution_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Track database migration and script execution history';

-- Log this reset
INSERT INTO migration_history (script_name, executed_by, status)
VALUES ('reset.sql', @current_user, 'SUCCESS');

-- =====================================================
-- STEP 6: Create utility procedures
-- =====================================================

DELIMITER $$

-- Procedure to get database information
DROP PROCEDURE IF EXISTS get_db_info$$
CREATE PROCEDURE get_db_info()
BEGIN
    SELECT '=== Database Information ===' AS '';

    -- Database basics
    SELECT
        DATABASE() AS 'Current Database',
        @@character_set_database AS 'Character Set',
        @@collation_database AS 'Collation',
        @@sql_mode AS 'SQL Mode';

    -- Database size
    SELECT
        table_schema AS 'Database',
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)',
        COUNT(*) AS 'Tables'
    FROM information_schema.tables
    WHERE table_schema = 'clinic_db'
    GROUP BY table_schema;

    -- Table list
    SELECT
        table_name AS 'Table',
        engine AS 'Engine',
        table_rows AS 'Rows (Approx)',
        ROUND((data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
    FROM information_schema.tables
    WHERE table_schema = 'clinic_db'
        AND table_type = 'BASE TABLE'
    ORDER BY table_name;

    -- User privileges
    SELECT
        grantee AS 'User',
        privilege_type AS 'Privilege'
    FROM information_schema.schema_privileges
    WHERE table_schema = 'clinic_db'
        AND grantee LIKE '%clinic_admin%'
    LIMIT 10;
END$$

-- Procedure to check database health
DROP PROCEDURE IF EXISTS check_db_health$$
CREATE PROCEDURE check_db_health()
BEGIN
    DECLARE table_count INT;
    DECLARE db_charset VARCHAR(32);
    DECLARE db_collation VARCHAR(32);

    -- Get counts
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'clinic_db'
        AND table_type = 'BASE TABLE';

    -- Get character set
    SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
    INTO db_charset, db_collation
    FROM information_schema.SCHEMATA
    WHERE SCHEMA_NAME = 'clinic_db';

    -- Display health check results
    SELECT 'Database Health Check' AS 'Check',
           CASE
               WHEN DATABASE() = 'clinic_db' THEN 'PASS'
               ELSE 'FAIL'
           END AS 'Status'
    UNION ALL
    SELECT 'Character Set Check',
           CASE
               WHEN db_charset = 'utf8mb4' THEN 'PASS'
               ELSE 'FAIL'
           END
    UNION ALL
    SELECT 'Collation Check',
           CASE
               WHEN db_collation = 'utf8mb4_unicode_ci' THEN 'PASS'
               ELSE 'FAIL'
           END
    UNION ALL
    SELECT 'User Privileges Check',
           CASE
               WHEN EXISTS (
                   SELECT 1 FROM information_schema.schema_privileges
                   WHERE table_schema = 'clinic_db'
                   AND grantee LIKE '%clinic_admin%'
               ) THEN 'PASS'
               ELSE 'FAIL'
           END;

    -- Summary
    SELECT
        CONCAT('Database reset complete. ',
               table_count, ' table(s) found. ',
               'Character set: ', db_charset, '. ',
               'Ready for use.') AS 'Summary';
END$$

DELIMITER ;

-- =====================================================
-- STEP 7: Verification
-- =====================================================

-- Show summary
SELECT '=============================================' AS '';
SELECT 'Database Reset Complete!' AS '';
SELECT '=============================================' AS '';

-- Display database info
CALL get_db_info();

-- Run health check
CALL check_db_health();

-- Show connection info
SELECT '=============================================' AS '';
SELECT 'Connection Information:' AS '';
SELECT '=============================================' AS '';
SELECT 'Host: localhost' AS '';
SELECT 'Port: 3306' AS '';
SELECT 'Database: clinic_db' AS '';
SELECT 'Username: clinic_admin' AS '';
SELECT 'Password: Cl1n1c@dm1n2024!' AS '';
SELECT '=============================================' AS '';

-- =====================================================
-- STEP 8: Next Steps
-- =====================================================

SELECT 'Next steps:' AS '';
SELECT '1. Run schema creation scripts' AS '';
SELECT '2. Load reference data' AS '';
SELECT '3. Create stored procedures and views' AS '';
SELECT '4. Test with sample data' AS '';
SELECT '=============================================' AS '';

-- End of reset script