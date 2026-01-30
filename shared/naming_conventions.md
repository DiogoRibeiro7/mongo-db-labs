# MySQL Database Naming Conventions

This document defines naming standards for MySQL database objects to ensure consistency, readability, and maintainability.

## Table of Contents

1. [General Rules](#general-rules)
2. [Database Names](#database-names)
3. [Table Names](#table-names)
4. [Column Names](#column-names)
5. [Index Names](#index-names)
6. [Constraint Names](#constraint-names)
7. [View Names](#view-names)
8. [Stored Procedure Names](#stored-procedure-names)
9. [Function Names](#function-names)
10. [Trigger Names](#trigger-names)
11. [Examples](#examples)

---

## General Rules

### Universal Principles

1. **Use lowercase** with underscores (snake_case)
   ```sql
   -- Good
   patient_records, appointment_date, total_amount

   -- Bad
   PatientRecords, appointmentDate, TotalAmount
   ```

2. **Be descriptive but concise**
   ```sql
   -- Good
   birth_date, phone_number, is_active

   -- Bad
   dob, ph_no, flag
   ```

3. **Avoid reserved keywords**
   ```sql
   -- Bad
   `order`, `select`, `table`, `user`

   -- Good
   customer_order, selection_type, data_table, system_user
   ```

4. **Use singular for entity names**
   ```sql
   -- Good (tables)
   patient, doctor, appointment

   -- Acceptable for junction tables
   patient_allergies, doctor_specialties
   ```

5. **Maximum length: 64 characters** (MySQL limit)

6. **No spaces or special characters** except underscore

7. **Use consistent abbreviations**
   ```sql
   -- Define and stick to abbreviations
   num = number
   max = maximum
   min = minimum
   qty = quantity
   amt = amount
   desc = description
   ```

---

## Database Names

### Format: `project_environment` or `project_db`

```sql
-- Production
clinic_db
clinic_prod

-- Development
clinic_dev
clinic_test

-- Module-specific
clinic_billing
clinic_inventory
```

### Rules:
- All lowercase
- Use underscores for separation
- Keep under 32 characters
- Include environment suffix when needed

---

## Table Names

### Format: `entity_name` (singular) or `entity_subtype`

```sql
-- Core entities (singular)
patient
doctor
appointment
invoice
medication

-- Subtypes or categories
patient_insurance
patient_allergy
doctor_specialty
appointment_reminder

-- Junction/Bridge tables
patient_medication   -- Many-to-many relationship
doctor_patient      -- Many-to-many relationship

-- Lookup/Reference tables
payment_method
appointment_status
blood_type
```

### Rules:
- Use singular form for main entities
- Use descriptive names for junction tables
- Prefix with module name if needed: `billing_invoice`
- Avoid generic names: `data`, `info`, `table1`

---

## Column Names

### Format: `attribute_name` or `entity_attribute`

### Primary Keys
```sql
-- Pattern 1: id (simple)
CREATE TABLE patient (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ...
);

-- Pattern 2: entity_id (explicit)
CREATE TABLE patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    ...
);
```

### Foreign Keys
```sql
-- Always use referenced_table_id
CREATE TABLE appointment (
    appointment_id INT PRIMARY KEY,
    patient_id INT,  -- References patient.patient_id
    doctor_id INT,   -- References doctor.doctor_id
    ...
);
```

### Common Patterns

**Timestamps:**
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
deleted_at TIMESTAMP NULL,  -- Soft delete
scheduled_at TIMESTAMP,
completed_at TIMESTAMP
```

**Status/Flags:**
```sql
is_active BOOLEAN DEFAULT TRUE,
is_deleted BOOLEAN DEFAULT FALSE,
is_verified BOOLEAN DEFAULT FALSE,
has_insurance BOOLEAN,
can_book_online BOOLEAN
```

**Amounts/Numbers:**
```sql
total_amount DECIMAL(10,2),
unit_price DECIMAL(10,2),
quantity INT,
max_capacity INT,
min_threshold INT,
item_count INT
```

**Strings:**
```sql
first_name VARCHAR(50),
last_name VARCHAR(50),
email_address VARCHAR(100),
phone_number VARCHAR(20),
street_address VARCHAR(255),
description TEXT,
notes TEXT
```

**Codes/Identifiers:**
```sql
patient_code VARCHAR(20),     -- Human-readable codes
reference_number VARCHAR(50),  -- External references
tax_id VARCHAR(20),
license_number VARCHAR(30)
```

### Rules:
- Boolean columns start with `is_`, `has_`, `can_`, `should_`
- Timestamp columns end with `_at` or `_date`
- Count/quantity columns often end with `_count`, `_qty`, `_total`
- Avoid redundant table name in column: `patient.patient_name` → `patient.name`

---

## Index Names

### Format: `idx_tablename_columns` or `uk_tablename_columns`

```sql
-- Single column index
CREATE INDEX idx_patient_email ON patient(email_address);
CREATE INDEX idx_appointment_date ON appointment(appointment_date);

-- Composite index
CREATE INDEX idx_appointment_patient_date ON appointment(patient_id, appointment_date);
CREATE INDEX idx_invoice_patient_status ON invoice(patient_id, status);

-- Unique index
CREATE UNIQUE INDEX uk_patient_email ON patient(email_address);
CREATE UNIQUE INDEX uk_doctor_license ON doctor(license_number);

-- Full-text index
CREATE FULLTEXT INDEX ft_patient_notes ON patient(medical_notes);
```

### Rules:
- Prefix: `idx_` for regular, `uk_` for unique, `ft_` for fulltext
- Include table name
- List columns in order of appearance
- Keep under 64 characters (abbreviate if needed)

---

## Constraint Names

### Foreign Key Format: `fk_childtable_parenttable`

```sql
-- Foreign key constraints
ALTER TABLE appointment
    ADD CONSTRAINT fk_appointment_patient
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id);

ALTER TABLE prescription
    ADD CONSTRAINT fk_prescription_doctor
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id);
```

### Check Constraint Format: `chk_tablename_rule`

```sql
-- Check constraints (MySQL 8.0.16+)
ALTER TABLE patient
    ADD CONSTRAINT chk_patient_age
    CHECK (birth_date <= CURRENT_DATE);

ALTER TABLE appointment
    ADD CONSTRAINT chk_appointment_duration
    CHECK (end_time > start_time);

ALTER TABLE invoice
    ADD CONSTRAINT chk_invoice_amount
    CHECK (total_amount >= 0);
```

### Unique Constraint Format: `uk_tablename_columns`

```sql
-- Unique constraints
ALTER TABLE patient
    ADD CONSTRAINT uk_patient_ssn
    UNIQUE (social_security_number);

ALTER TABLE doctor
    ADD CONSTRAINT uk_doctor_npi
    UNIQUE (npi_number);
```

---

## View Names

### Format: `v_description` or `vw_description`

```sql
-- Simple views
CREATE VIEW v_active_patients AS ...;
CREATE VIEW v_today_appointments AS ...;
CREATE VIEW v_pending_invoices AS ...;

-- Reporting views
CREATE VIEW v_monthly_revenue AS ...;
CREATE VIEW v_patient_demographics AS ...;

-- Materialized view pattern (using tables)
CREATE TABLE mv_daily_statistics AS ...;  -- Refreshed by procedure
```

### Rules:
- Prefix with `v_` or `vw_`
- Use descriptive names indicating content
- For complex views, include purpose: `v_report_monthly_billing`

---

## Stored Procedure Names

### Format: `sp_action_entity` or `sp_module_action`

```sql
-- CRUD operations
CREATE PROCEDURE sp_create_patient(...);
CREATE PROCEDURE sp_update_patient(...);
CREATE PROCEDURE sp_delete_patient(...);
CREATE PROCEDURE sp_get_patient(...);

-- Business logic
CREATE PROCEDURE sp_schedule_appointment(...);
CREATE PROCEDURE sp_process_payment(...);
CREATE PROCEDURE sp_generate_invoice(...);

-- Utility procedures
CREATE PROCEDURE sp_util_cleanup_logs(...);
CREATE PROCEDURE sp_util_rebuild_indexes(...);

-- Reporting procedures
CREATE PROCEDURE sp_report_daily_summary(...);
CREATE PROCEDURE sp_report_patient_history(...);
```

### Rules:
- Prefix with `sp_`
- Use verb_noun format
- Group by module when needed: `sp_billing_calculate_total`
- Utility procedures: `sp_util_*`
- Reports: `sp_report_*`

---

## Function Names

### Format: `fn_action_description` or `f_action_description`

```sql
-- Calculation functions
CREATE FUNCTION fn_calculate_age(birth_date DATE) ...;
CREATE FUNCTION fn_calculate_bmi(height FLOAT, weight FLOAT) ...;

-- Formatting functions
CREATE FUNCTION fn_format_phone(phone VARCHAR(20)) ...;
CREATE FUNCTION fn_format_name(first VARCHAR(50), last VARCHAR(50)) ...;

-- Validation functions
CREATE FUNCTION fn_validate_email(email VARCHAR(100)) ...;
CREATE FUNCTION fn_validate_ssn(ssn VARCHAR(11)) ...;

-- Business logic functions
CREATE FUNCTION fn_get_next_appointment_slot(...) ...;
CREATE FUNCTION fn_check_insurance_coverage(...) ...;
```

### Rules:
- Prefix with `fn_` or `f_`
- Return single values only
- Use descriptive verb_noun format
- Keep pure (no side effects)

---

## Trigger Names

### Format: `tr_tablename_timing_action`

```sql
-- Before triggers
CREATE TRIGGER tr_patient_before_insert ...;
CREATE TRIGGER tr_patient_before_update ...;
CREATE TRIGGER tr_appointment_before_delete ...;

-- After triggers
CREATE TRIGGER tr_invoice_after_insert ...;
CREATE TRIGGER tr_payment_after_update ...;
CREATE TRIGGER tr_patient_after_delete ...;

-- Audit triggers
CREATE TRIGGER tr_patient_audit_update ...;
CREATE TRIGGER tr_invoice_audit_delete ...;
```

### Timing options:
- `before` or `bf`
- `after` or `af`

### Action options:
- `insert` or `ins`
- `update` or `upd`
- `delete` or `del`

---

## Examples

### Complete Table Example

```sql
-- Patient table with all naming conventions
CREATE TABLE patient (
    -- Primary key
    patient_id INT AUTO_INCREMENT PRIMARY KEY,

    -- Personal information
    medical_record_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    birth_date DATE NOT NULL,
    gender ENUM('M', 'F', 'O') NOT NULL,

    -- Contact information
    email_address VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    mobile_number VARCHAR(20),

    -- Address
    street_address VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(50),
    postal_code VARCHAR(20),
    country_code CHAR(2) DEFAULT 'US',

    -- Status flags
    is_active BOOLEAN DEFAULT TRUE,
    is_deceased BOOLEAN DEFAULT FALSE,
    has_insurance BOOLEAN DEFAULT FALSE,

    -- References
    primary_doctor_id INT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),

    -- Indexes
    INDEX idx_patient_name (last_name, first_name),
    INDEX idx_patient_birth (birth_date),
    INDEX idx_patient_mrn (medical_record_number),

    -- Constraints
    CONSTRAINT fk_patient_doctor
        FOREIGN KEY (primary_doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_patient_birth
        CHECK (birth_date <= CURRENT_DATE),

    CONSTRAINT chk_patient_email
        CHECK (email_address REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Related Objects Example

```sql
-- Index
CREATE INDEX idx_patient_active_created
ON patient(is_active, created_at DESC);

-- View
CREATE VIEW v_active_patients AS
SELECT
    patient_id,
    CONCAT(first_name, ' ', last_name) AS full_name,
    email_address,
    phone_number
FROM patient
WHERE is_active = TRUE;

-- Stored procedure
DELIMITER $$
CREATE PROCEDURE sp_get_patient_by_id(
    IN p_patient_id INT
)
BEGIN
    SELECT * FROM patient
    WHERE patient_id = p_patient_id
    AND is_active = TRUE;
END$$
DELIMITER ;

-- Function
DELIMITER $$
CREATE FUNCTION fn_calculate_patient_age(
    p_birth_date DATE
) RETURNS INT
DETERMINISTIC
BEGIN
    RETURN TIMESTAMPDIFF(YEAR, p_birth_date, CURDATE());
END$$
DELIMITER ;

-- Trigger
DELIMITER $$
CREATE TRIGGER tr_patient_before_update
BEFORE UPDATE ON patient
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
    SET NEW.updated_by = USER();
END$$
DELIMITER ;
```

---

## Anti-Patterns to Avoid

### Don't Use:

1. **Mixed case**: `PatientRecord`, `appointmentDate`
2. **Spaces**: `patient record`, `appointment date`
3. **Special characters**: `patient-record`, `patient#1`
4. **Reserved words**: `order`, `select`, `table`
5. **Meaningless names**: `table1`, `col1`, `data`
6. **Hungarian notation**: `tblPatient`, `intAge`, `strName`
7. **Excessive abbreviations**: `pt_rcrd`, `appt_dt`
8. **Inconsistent pluralization**: Mix of `patient` and `doctors`

---

## Quick Reference Card

| Object Type | Prefix/Pattern | Example |
|------------|---------------|---------|
| Database | lowercase_underscore | clinic_db |
| Table | singular_noun | patient |
| Column | attribute_name | first_name |
| Primary Key | id or entity_id | patient_id |
| Foreign Key | referenced_table_id | doctor_id |
| Index | idx_table_columns | idx_patient_email |
| Unique Index | uk_table_columns | uk_patient_ssn |
| Foreign Key Constraint | fk_child_parent | fk_appointment_patient |
| Check Constraint | chk_table_rule | chk_patient_age |
| View | v_description | v_active_patients |
| Stored Procedure | sp_action_entity | sp_create_patient |
| Function | fn_action_description | fn_calculate_age |
| Trigger | tr_table_timing_action | tr_patient_before_insert |

---

## Enforcement

### Using SQL Mode

```sql
-- Set strict SQL mode for development
SET GLOBAL sql_mode = 'TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY';

-- Check current SQL mode
SELECT @@sql_mode;
```

### Validation Query

```sql
-- Check for naming convention violations
SELECT
    table_name,
    column_name,
    CASE
        WHEN column_name != LOWER(column_name) THEN 'Not lowercase'
        WHEN column_name LIKE '% %' THEN 'Contains spaces'
        WHEN column_name REGEXP '[^a-z0-9_]' THEN 'Invalid characters'
        ELSE 'OK'
    END AS issue
FROM information_schema.columns
WHERE table_schema = 'clinic_db'
    AND (
        column_name != LOWER(column_name)
        OR column_name LIKE '% %'
        OR column_name REGEXP '[^a-z0-9_]'
    );
```

---

**Document Version**: 1.0
**Last Updated**: January 2024
**Applies to**: MySQL 8.0.x