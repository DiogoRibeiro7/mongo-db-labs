-- =====================================================
-- Script: common_integrity_queries.sql
-- Description: Common data integrity check queries for MySQL databases
-- Usage: Run individual queries or entire script to check data integrity
-- Database: Generic (customize table/column names as needed)
-- =====================================================

-- =====================================================
-- SECTION 1: ORPHAN RECORDS CHECKS
-- =====================================================

-- Generic orphan check template
-- Find records in child table with no matching parent
SELECT 'Orphan Records Check' AS check_type;

-- Example: Find appointments with non-existent patients
SELECT
    'Orphaned Appointments (No Patient)' AS issue,
    COUNT(*) AS record_count,
    GROUP_CONCAT(appointment_id SEPARATOR ', ') AS sample_ids
FROM appointment a
WHERE NOT EXISTS (
    SELECT 1 FROM patient p
    WHERE p.patient_id = a.patient_id
);

-- Example: Find prescriptions with non-existent doctors
SELECT
    'Orphaned Prescriptions (No Doctor)' AS issue,
    COUNT(*) AS record_count,
    GROUP_CONCAT(prescription_id SEPARATOR ', ') AS sample_ids
FROM prescription pr
WHERE NOT EXISTS (
    SELECT 1 FROM doctor d
    WHERE d.doctor_id = pr.doctor_id
);

-- Generic query to find all orphans based on foreign keys
SELECT
    kcu.table_name AS child_table,
    kcu.column_name AS fk_column,
    kcu.referenced_table_name AS parent_table,
    kcu.referenced_column_name AS parent_column,
    CONCAT('SELECT COUNT(*) FROM ', kcu.table_name,
           ' WHERE ', kcu.column_name, ' NOT IN (SELECT ',
           kcu.referenced_column_name, ' FROM ', kcu.referenced_table_name,
           ' WHERE ', kcu.referenced_column_name, ' IS NOT NULL)') AS check_query
FROM information_schema.key_column_usage kcu
WHERE kcu.table_schema = DATABASE()
    AND kcu.referenced_table_name IS NOT NULL
ORDER BY kcu.table_name, kcu.column_name;

-- Comprehensive orphan detection procedure
DELIMITER $$

DROP PROCEDURE IF EXISTS sp_check_orphans$$
CREATE PROCEDURE sp_check_orphans()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_table_name VARCHAR(64);
    DECLARE v_column_name VARCHAR(64);
    DECLARE v_ref_table VARCHAR(64);
    DECLARE v_ref_column VARCHAR(64);
    DECLARE v_count INT;
    DECLARE v_sql TEXT;

    DECLARE cur CURSOR FOR
        SELECT table_name, column_name, referenced_table_name, referenced_column_name
        FROM information_schema.key_column_usage
        WHERE table_schema = DATABASE()
            AND referenced_table_name IS NOT NULL;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    CREATE TEMPORARY TABLE IF NOT EXISTS orphan_report (
        child_table VARCHAR(64),
        fk_column VARCHAR(64),
        parent_table VARCHAR(64),
        orphan_count INT
    );

    TRUNCATE TABLE orphan_report;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_table_name, v_column_name, v_ref_table, v_ref_column;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET v_sql = CONCAT(
            'SELECT COUNT(*) INTO @orphan_count FROM ',
            v_table_name,
            ' WHERE ', v_column_name,
            ' IS NOT NULL AND ', v_column_name,
            ' NOT IN (SELECT ', v_ref_column,
            ' FROM ', v_ref_table,
            ' WHERE ', v_ref_column, ' IS NOT NULL)'
        );

        SET @orphan_count = 0;
        SET @sql = v_sql;
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        IF @orphan_count > 0 THEN
            INSERT INTO orphan_report VALUES (v_table_name, v_column_name, v_ref_table, @orphan_count);
        END IF;
    END LOOP;

    CLOSE cur;

    SELECT * FROM orphan_report
    WHERE orphan_count > 0
    ORDER BY orphan_count DESC;

    DROP TEMPORARY TABLE IF EXISTS orphan_report;
END$$

DELIMITER ;

-- Run orphan check
-- CALL sp_check_orphans();

-- =====================================================
-- SECTION 2: DUPLICATE RECORDS CHECKS
-- =====================================================

SELECT 'Duplicate Records Check' AS check_type;

-- Find duplicate emails in patient table
SELECT
    'Duplicate Patient Emails' AS issue,
    email_address,
    COUNT(*) AS duplicate_count,
    GROUP_CONCAT(patient_id SEPARATOR ', ') AS patient_ids
FROM patient
WHERE email_address IS NOT NULL
GROUP BY email_address
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- Find duplicate phone numbers
SELECT
    'Duplicate Phone Numbers' AS issue,
    phone_number,
    COUNT(*) AS duplicate_count,
    GROUP_CONCAT(patient_id SEPARATOR ', ') AS patient_ids
FROM patient
WHERE phone_number IS NOT NULL
GROUP BY phone_number
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- Find duplicate appointments (same patient, doctor, time)
SELECT
    'Duplicate Appointments' AS issue,
    patient_id,
    doctor_id,
    appointment_date,
    appointment_time,
    COUNT(*) AS duplicate_count,
    GROUP_CONCAT(appointment_id SEPARATOR ', ') AS appointment_ids
FROM appointment
GROUP BY patient_id, doctor_id, appointment_date, appointment_time
HAVING COUNT(*) > 1;

-- Generic duplicate finder for any unique constraint
DELIMITER $$

DROP PROCEDURE IF EXISTS sp_find_duplicates$$
CREATE PROCEDURE sp_find_duplicates(
    IN p_table_name VARCHAR(64),
    IN p_column_list VARCHAR(255)
)
BEGIN
    SET @sql = CONCAT(
        'SELECT ''Duplicates in ', p_table_name, ''' AS issue, ',
        p_column_list, ', ',
        'COUNT(*) AS duplicate_count ',
        'FROM ', p_table_name, ' ',
        'GROUP BY ', p_column_list, ' ',
        'HAVING COUNT(*) > 1 ',
        'ORDER BY duplicate_count DESC'
    );

    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

-- Usage examples:
-- CALL sp_find_duplicates('patient', 'first_name, last_name, birth_date');
-- CALL sp_find_duplicates('doctor', 'license_number');

-- =====================================================
-- SECTION 3: INVALID DATE/TIME CHECKS
-- =====================================================

SELECT 'Invalid Date/Time Check' AS check_type;

-- Find future birth dates
SELECT
    'Future Birth Dates' AS issue,
    COUNT(*) AS record_count,
    MIN(birth_date) AS earliest_invalid,
    MAX(birth_date) AS latest_invalid
FROM patient
WHERE birth_date > CURDATE();

-- Find appointments with end time before start time
SELECT
    'Invalid Appointment Times' AS issue,
    COUNT(*) AS record_count,
    GROUP_CONCAT(appointment_id SEPARATOR ', ') AS sample_ids
FROM appointment
WHERE end_time <= start_time;

-- Find records with updated_at before created_at
SELECT
    'Invalid Timestamp Sequence' AS issue,
    table_name,
    COUNT(*) AS record_count
FROM (
    SELECT 'patient' AS table_name FROM patient WHERE updated_at < created_at
    UNION ALL
    SELECT 'doctor' FROM doctor WHERE updated_at < created_at
    UNION ALL
    SELECT 'appointment' FROM appointment WHERE updated_at < created_at
) AS invalid_timestamps
GROUP BY table_name;

-- Check for invalid dates (year 0000, etc.)
SELECT
    'Invalid Date Values' AS issue,
    'Appointments' AS table_name,
    COUNT(*) AS record_count
FROM appointment
WHERE appointment_date < '1900-01-01'
   OR appointment_date > '2100-01-01'
   OR appointment_date = '0000-00-00';

-- Find overlapping appointments for same doctor
SELECT
    'Overlapping Doctor Appointments' AS issue,
    a1.doctor_id,
    COUNT(*) AS overlap_count
FROM appointment a1
INNER JOIN appointment a2 ON a1.doctor_id = a2.doctor_id
    AND a1.appointment_id != a2.appointment_id
    AND a1.appointment_date = a2.appointment_date
    AND (
        (a1.start_time <= a2.start_time AND a1.end_time > a2.start_time)
        OR (a1.start_time < a2.end_time AND a1.end_time >= a2.end_time)
        OR (a1.start_time >= a2.start_time AND a1.end_time <= a2.end_time)
    )
GROUP BY a1.doctor_id;

-- =====================================================
-- SECTION 4: TOTAL/SUMMARY MISMATCHES
-- =====================================================

SELECT 'Total/Summary Mismatch Check' AS check_type;

-- Check invoice totals match line items
SELECT
    'Invoice Total Mismatches' AS issue,
    i.invoice_id,
    i.total_amount AS stored_total,
    COALESCE(SUM(il.quantity * il.unit_price), 0) AS calculated_total,
    ABS(i.total_amount - COALESCE(SUM(il.quantity * il.unit_price), 0)) AS difference
FROM invoice i
LEFT JOIN invoice_line il ON i.invoice_id = il.invoice_id
GROUP BY i.invoice_id, i.total_amount
HAVING ABS(difference) > 0.01;

-- Check payment totals match invoice
SELECT
    'Payment Amount Mismatches' AS issue,
    p.payment_id,
    p.invoice_id,
    p.amount AS payment_amount,
    i.total_amount AS invoice_amount,
    ABS(p.amount - i.total_amount) AS difference
FROM payment p
INNER JOIN invoice i ON p.invoice_id = i.invoice_id
WHERE ABS(p.amount - i.total_amount) > 0.01;

-- Check inventory quantities
SELECT
    'Inventory Quantity Mismatches' AS issue,
    inv.item_id,
    inv.quantity_on_hand AS stored_quantity,
    (
        COALESCE(received.total_received, 0) -
        COALESCE(dispensed.total_dispensed, 0)
    ) AS calculated_quantity,
    ABS(inv.quantity_on_hand - (
        COALESCE(received.total_received, 0) -
        COALESCE(dispensed.total_dispensed, 0)
    )) AS difference
FROM inventory inv
LEFT JOIN (
    SELECT item_id, SUM(quantity) AS total_received
    FROM inventory_receipt
    GROUP BY item_id
) AS received ON inv.item_id = received.item_id
LEFT JOIN (
    SELECT item_id, SUM(quantity) AS total_dispensed
    FROM inventory_dispensing
    GROUP BY item_id
) AS dispensed ON inv.item_id = dispensed.item_id
HAVING ABS(difference) > 0;

-- =====================================================
-- SECTION 5: REFERENTIAL INTEGRITY CHECKS
-- =====================================================

SELECT 'Referential Integrity Check' AS check_type;

-- Check for missing foreign key constraints
SELECT
    'Tables Without Foreign Keys' AS issue,
    t.table_name,
    COUNT(DISTINCT c.column_name) AS total_columns,
    COUNT(DISTINCT kcu.column_name) AS fk_columns
FROM information_schema.tables t
INNER JOIN information_schema.columns c
    ON t.table_schema = c.table_schema
    AND t.table_name = c.table_name
LEFT JOIN information_schema.key_column_usage kcu
    ON t.table_schema = kcu.table_schema
    AND t.table_name = kcu.table_name
    AND kcu.referenced_table_name IS NOT NULL
WHERE t.table_schema = DATABASE()
    AND t.table_type = 'BASE TABLE'
GROUP BY t.table_name
HAVING fk_columns = 0
    AND t.table_name NOT IN ('migration_history', 'db_metadata'); -- Exclude metadata tables

-- Check for self-referencing records
SELECT
    'Self-Referencing Records' AS issue,
    'Employee' AS table_name,
    employee_id,
    manager_id
FROM employee
WHERE employee_id = manager_id
    AND manager_id IS NOT NULL;

-- =====================================================
-- SECTION 6: DATA TYPE AND CONSTRAINT VIOLATIONS
-- =====================================================

SELECT 'Data Type and Constraint Check' AS check_type;

-- Check for invalid email formats
SELECT
    'Invalid Email Formats' AS issue,
    COUNT(*) AS record_count,
    GROUP_CONCAT(patient_id SEPARATOR ', ') AS sample_ids
FROM patient
WHERE email_address IS NOT NULL
    AND email_address NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'
LIMIT 10;

-- Check for invalid phone number formats
SELECT
    'Invalid Phone Numbers' AS issue,
    COUNT(*) AS record_count,
    GROUP_CONCAT(patient_id SEPARATOR ', ') AS sample_ids
FROM patient
WHERE phone_number IS NOT NULL
    AND phone_number NOT REGEXP '^[0-9+()\\s-]+$'
LIMIT 10;

-- Check for negative values where they shouldn't exist
SELECT
    'Negative Values in Positive-Only Fields' AS issue,
    'Invoice' AS table_name,
    COUNT(*) AS record_count
FROM invoice
WHERE total_amount < 0
UNION ALL
SELECT
    'Negative Values in Positive-Only Fields',
    'Inventory',
    COUNT(*)
FROM inventory
WHERE quantity_on_hand < 0;

-- Check for NULL values in NOT NULL columns (shouldn't happen with constraints)
SELECT
    'NULL Values in Required Fields' AS issue,
    table_name,
    column_name,
    CONCAT('SELECT COUNT(*) FROM ', table_name, ' WHERE ', column_name, ' IS NULL') AS check_query
FROM information_schema.columns
WHERE table_schema = DATABASE()
    AND is_nullable = 'NO'
    AND column_default IS NULL
    AND column_name NOT IN ('id', 'created_at', 'updated_at'); -- Exclude auto-populated

-- =====================================================
-- SECTION 7: BUSINESS RULE VIOLATIONS
-- =====================================================

SELECT 'Business Rule Violations Check' AS check_type;

-- Check for appointments outside business hours
SELECT
    'Appointments Outside Business Hours' AS issue,
    COUNT(*) AS record_count,
    MIN(appointment_time) AS earliest,
    MAX(appointment_time) AS latest
FROM appointment
WHERE HOUR(appointment_time) < 7
   OR HOUR(appointment_time) >= 20;

-- Check for expired medications still marked as active
SELECT
    'Expired Active Medications' AS issue,
    COUNT(*) AS record_count,
    GROUP_CONCAT(medication_id SEPARATOR ', ') AS sample_ids
FROM medication
WHERE expiry_date < CURDATE()
    AND is_active = TRUE;

-- Check for patients with impossible ages
SELECT
    'Patients with Invalid Ages' AS issue,
    COUNT(*) AS record_count,
    MIN(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS min_age,
    MAX(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS max_age
FROM patient
WHERE TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) > 150
   OR TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) < 0;

-- =====================================================
-- SECTION 8: COMPREHENSIVE INTEGRITY REPORT
-- =====================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_comprehensive_integrity_check$$
CREATE PROCEDURE sp_comprehensive_integrity_check()
BEGIN
    DECLARE v_orphan_count INT DEFAULT 0;
    DECLARE v_duplicate_count INT DEFAULT 0;
    DECLARE v_date_issue_count INT DEFAULT 0;
    DECLARE v_total_issues INT DEFAULT 0;

    -- Create temporary report table
    CREATE TEMPORARY TABLE IF NOT EXISTS integrity_report (
        check_category VARCHAR(50),
        issue_type VARCHAR(100),
        severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
        record_count INT,
        details TEXT
    );

    TRUNCATE TABLE integrity_report;

    -- Check for orphans (simplified example)
    INSERT INTO integrity_report
    SELECT
        'Referential Integrity',
        CONCAT('Orphaned ', table_name, ' records'),
        'CRITICAL',
        COUNT(*),
        CONCAT('Foreign key: ', column_name, ' -> ', referenced_table_name)
    FROM information_schema.key_column_usage
    WHERE table_schema = DATABASE()
        AND referenced_table_name IS NOT NULL
    GROUP BY table_name, column_name, referenced_table_name;

    -- Check for duplicates (example for patient emails)
    INSERT INTO integrity_report
    SELECT
        'Duplicates',
        'Duplicate patient emails',
        'HIGH',
        COUNT(*),
        GROUP_CONCAT(email_address SEPARATOR ', ')
    FROM (
        SELECT email_address
        FROM patient
        WHERE email_address IS NOT NULL
        GROUP BY email_address
        HAVING COUNT(*) > 1
    ) AS dup;

    -- Check for date issues
    INSERT INTO integrity_report
    SELECT
        'Date/Time Issues',
        'Future birth dates',
        'CRITICAL',
        COUNT(*),
        CONCAT('Latest: ', MAX(birth_date))
    FROM patient
    WHERE birth_date > CURDATE();

    -- Generate summary
    SELECT
        '======================================' AS '',
        'DATA INTEGRITY REPORT' AS '',
        '======================================' AS '';

    SELECT
        check_category AS 'Category',
        COUNT(*) AS 'Issues',
        SUM(record_count) AS 'Affected Records'
    FROM integrity_report
    GROUP BY check_category;

    SELECT '' AS '', '=== Detailed Issues ===' AS '';

    SELECT
        check_category AS 'Category',
        issue_type AS 'Issue',
        severity AS 'Severity',
        record_count AS 'Records',
        LEFT(details, 100) AS 'Details'
    FROM integrity_report
    ORDER BY
        FIELD(severity, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
        record_count DESC;

    -- Calculate total issues
    SELECT COUNT(*) INTO v_total_issues FROM integrity_report;

    IF v_total_issues = 0 THEN
        SELECT 'No integrity issues found!' AS 'Result';
    ELSE
        SELECT CONCAT(v_total_issues, ' integrity issues found - review details above') AS 'Result';
    END IF;

    DROP TEMPORARY TABLE IF EXISTS integrity_report;
END$$

DELIMITER ;

-- Run comprehensive check
-- CALL sp_comprehensive_integrity_check();

-- =====================================================
-- SECTION 9: UTILITY QUERIES
-- =====================================================

-- Get row counts for all tables
SELECT
    table_name AS 'Table',
    table_rows AS 'Row Count (Approx)',
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = DATABASE()
    AND table_type = 'BASE TABLE'
ORDER BY table_rows DESC;

-- Find columns that might need indexes (frequently in WHERE clauses)
SELECT
    'Potential Missing Indexes' AS check_type,
    CONCAT('Consider index on ', table_name, '.', column_name) AS suggestion
FROM information_schema.columns c
WHERE c.table_schema = DATABASE()
    AND c.column_name LIKE '%_id'
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.statistics s
        WHERE s.table_schema = c.table_schema
            AND s.table_name = c.table_name
            AND s.column_name = c.column_name
    );

-- Check character set consistency
SELECT
    'Character Set Inconsistencies' AS issue,
    table_name,
    column_name,
    character_set_name,
    collation_name
FROM information_schema.columns
WHERE table_schema = DATABASE()
    AND character_set_name IS NOT NULL
    AND character_set_name != 'utf8mb4'
ORDER BY table_name, column_name;

-- =====================================================
-- SECTION 10: QUICK HEALTH CHECK
-- =====================================================

-- One-line health check
SELECT
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM information_schema.key_column_usage
            WHERE table_schema = DATABASE()
                AND referenced_table_name IS NOT NULL
        ) > 0
        AND (
            SELECT COUNT(*)
            FROM information_schema.table_constraints
            WHERE table_schema = DATABASE()
                AND constraint_type = 'PRIMARY KEY'
        ) > 0
        THEN 'HEALTHY'
        ELSE 'NEEDS ATTENTION'
    END AS 'Database Health Status';

-- =====================================================
-- END OF INTEGRITY CHECKS
-- =====================================================

-- Usage Instructions:
-- 1. Run entire script for all checks
-- 2. Run individual sections as needed
-- 3. Customize table/column names for your schema
-- 4. Schedule regular integrity checks
-- 5. Add results to monitoring dashboard