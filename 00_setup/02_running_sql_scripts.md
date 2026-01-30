# Running SQL Scripts in MySQL

This guide covers various methods for executing SQL scripts in MySQL on Windows, including command line, MySQL Workbench, and batch processing.

## Table of Contents

1. [Script File Preparation](#script-file-preparation)
2. [Method 1: MySQL Command Line](#method-1-mysql-command-line)
3. [Method 2: MySQL Workbench](#method-2-mysql-workbench)
4. [Method 3: MySQL Shell](#method-3-mysql-shell)
5. [Method 4: Batch Files](#method-4-batch-files)
6. [Running Multiple Scripts](#running-multiple-scripts)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Script File Preparation

### File Organization

Recommended structure for SQL scripts:

```
clinic_project/
├── 00_setup/
│   ├── 01_create_database.sql
│   ├── 02_create_users.sql
│   └── 03_privileges.sql
├── 01_schema/
│   ├── 01_create_tables.sql
│   ├── 02_create_indexes.sql
│   └── 03_create_constraints.sql
├── 02_data/
│   ├── 01_reference_data.sql
│   ├── 02_sample_data.sql
│   └── 03_test_data.sql
├── 03_procedures/
│   ├── 01_stored_procedures.sql
│   ├── 02_functions.sql
│   └── 03_triggers.sql
└── 04_views/
    └── 01_create_views.sql
```

### Script Header Template

Start each script with metadata:

```sql
-- =====================================================
-- Script: 01_create_tables.sql
-- Description: Creates all tables for clinic database
-- Author: Your Name
-- Date: 2024-01-30
-- Version: 1.0
-- Database: clinic_db
-- Prerequisites: Database clinic_db must exist
-- =====================================================

-- Use the target database
USE clinic_db;

-- Set session variables for safety
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'TRADITIONAL';
SET AUTOCOMMIT = 0;

-- Start transaction
START TRANSACTION;

-- Your SQL statements here...

-- Commit if successful
COMMIT;

-- Reset session variables
SET FOREIGN_KEY_CHECKS = 1;
SET AUTOCOMMIT = 1;
```

---

## Method 1: MySQL Command Line

### Basic Execution

1. **Navigate to Script Directory**
   ```cmd
   cd C:\clinic_project\01_schema
   ```

2. **Execute Single Script**
   ```cmd
   mysql -u clinic_admin -p clinic_db < 01_create_tables.sql
   ```

3. **With Full Path**
   ```cmd
   mysql -u clinic_admin -p clinic_db < "C:\clinic_project\01_schema\01_create_tables.sql"
   ```

### Advanced Options

```cmd
# Verbose output (show statements)
mysql -u clinic_admin -p clinic_db -v < script.sql

# Very verbose (show statements and results)
mysql -u clinic_admin -p clinic_db -vv < script.sql

# Force continue on errors
mysql -u clinic_admin -p clinic_db --force < script.sql

# Specify character set
mysql -u clinic_admin -p clinic_db --default-character-set=utf8mb4 < script.sql

# Save output to file
mysql -u clinic_admin -p clinic_db < script.sql > output.txt 2>&1

# Without password prompt (INSECURE - dev only)
mysql -u clinic_admin -pYourPassword123! clinic_db < script.sql
```

### Using source Command

1. **Connect to MySQL**
   ```cmd
   mysql -u clinic_admin -p clinic_db
   ```

2. **Execute Script**
   ```sql
   source C:/clinic_project/01_schema/01_create_tables.sql;
   -- Or with forward slashes
   source C:\clinic_project\01_schema\01_create_tables.sql;
   ```

### Batch Mode Execution

```cmd
# Execute inline SQL
mysql -u clinic_admin -p clinic_db -e "SELECT COUNT(*) FROM patients;"

# Execute multiple statements
mysql -u clinic_admin -p clinic_db -e "USE clinic_db; SHOW TABLES; SELECT DATABASE();"

# Format output as table (default)
mysql -u clinic_admin -p clinic_db -t -e "SELECT * FROM patients LIMIT 5;"

# Format output as tab-separated
mysql -u clinic_admin -p clinic_db -B -e "SELECT * FROM patients;" > patients.tsv

# Format output as XML
mysql -u clinic_admin -p clinic_db -X -e "SELECT * FROM patients;" > patients.xml
```

---

## Method 2: MySQL Workbench

### Opening and Running Scripts

1. **Open SQL Script**
   - File → Open SQL Script (Ctrl+O)
   - Navigate to script file
   - Click "Open"

2. **Review Script**
   - Script appears in new tab
   - Syntax highlighting shows errors
   - Check database context (top toolbar)

3. **Execute Entire Script**
   - Click lightning bolt icon (Execute)
   - Or press Ctrl+Shift+Enter
   - Monitor Action Output panel

4. **Execute Selected Portions**
   - Select specific statements
   - Click lightning bolt (Execute Selection)
   - Or press Ctrl+Enter

### Running Multiple Files

1. **File → Run SQL Script**
   - Opens file dialog
   - Select script file
   - Choose connection
   - Click "Run"

2. **Batch Processing**
   - Create master script:
   ```sql
   -- master_script.sql
   source C:/clinic_project/01_schema/01_create_tables.sql;
   source C:/clinic_project/01_schema/02_create_indexes.sql;
   source C:/clinic_project/01_schema/03_create_constraints.sql;
   ```
   - Execute master script

### Script Output Options

1. **Configure Output**
   - Edit → Preferences → SQL Editor
   - SQL Execution:
     - ✅ Save snapshot of open editors
     - ✅ Show query stats
     - Max result set size: 50000

2. **Export Results**
   - Right-click result grid
   - Export Options:
     - CSV
     - JSON
     - XML
     - SQL INSERT statements

---

## Method 3: MySQL Shell

MySQL Shell offers modern scripting capabilities:

### Installation Check

```cmd
mysqlsh --version
```

If not installed, download from MySQL website.

### Running Scripts

1. **JavaScript Mode**
   ```cmd
   mysqlsh clinic_admin@localhost:3306/clinic_db

   MySQL> \js
   MySQL JS> \source C:/clinic_project/scripts/setup.js
   ```

2. **Python Mode**
   ```cmd
   mysqlsh clinic_admin@localhost:3306/clinic_db

   MySQL> \py
   MySQL Py> \source C:/clinic_project/scripts/setup.py
   ```

3. **SQL Mode**
   ```cmd
   mysqlsh clinic_admin@localhost:3306/clinic_db --sql

   MySQL SQL> \source C:/clinic_project/01_schema/01_create_tables.sql
   ```

4. **Direct Execution**
   ```cmd
   mysqlsh clinic_admin@localhost:3306/clinic_db --sql --file="C:/clinic_project/01_schema/01_create_tables.sql"
   ```

---

## Method 4: Batch Files

### Create Windows Batch File

Create `run_all_scripts.bat`:

```batch
@echo off
setlocal enabledelayedexpansion

:: Configuration
set MYSQL_USER=clinic_admin
set MYSQL_DB=clinic_db
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set SCRIPT_DIR=C:\clinic_project

:: Prompt for password
echo Enter MySQL password for %MYSQL_USER%:
set /p MYSQL_PWD=

:: Create log file
set LOG_FILE=%SCRIPT_DIR%\execution_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
echo Execution started at %date% %time% > "%LOG_FILE%"

:: Function to run script
:RunScript
set script_path=%~1
set script_name=%~nx1
echo.
echo Running: %script_name%
echo ===================================
mysql -u %MYSQL_USER% -p%MYSQL_PWD% -h %MYSQL_HOST% -P %MYSQL_PORT% %MYSQL_DB% < "%script_path%" 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Script %script_name% failed! >> "%LOG_FILE%"
    echo ERROR: Script %script_name% failed!
    pause
    exit /b %errorlevel%
) else (
    echo SUCCESS: Script %script_name% completed >> "%LOG_FILE%"
    echo SUCCESS: Script %script_name% completed
)
goto :eof

:: Main execution
echo.
echo ===================================
echo Starting Database Setup
echo ===================================

:: Run scripts in order
call :RunScript "%SCRIPT_DIR%\00_setup\01_create_database.sql"
call :RunScript "%SCRIPT_DIR%\00_setup\02_create_users.sql"
call :RunScript "%SCRIPT_DIR%\01_schema\01_create_tables.sql"
call :RunScript "%SCRIPT_DIR%\01_schema\02_create_indexes.sql"
call :RunScript "%SCRIPT_DIR%\02_data\01_reference_data.sql"

echo.
echo ===================================
echo All scripts completed successfully!
echo Log file: %LOG_FILE%
echo ===================================
pause
```

### PowerShell Script

Create `run_all_scripts.ps1`:

```powershell
# MySQL Configuration
$mysqlUser = "clinic_admin"
$mysqlDb = "clinic_db"
$mysqlHost = "localhost"
$mysqlPort = 3306
$scriptDir = "C:\clinic_project"

# Prompt for password
$mysqlPassword = Read-Host "Enter MySQL password for $mysqlUser" -AsSecureString
$mysqlPasswordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword))

# Create log file
$logFile = "$scriptDir\execution_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
"Execution started at $(Get-Date)" | Out-File $logFile

# Function to run SQL script
function Run-MySQLScript {
    param (
        [string]$ScriptPath
    )

    $scriptName = Split-Path $ScriptPath -Leaf
    Write-Host "`nRunning: $scriptName" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan

    $output = mysql -u $mysqlUser -p$mysqlPasswordText -h $mysqlHost -P $mysqlPort $mysqlDb 2>&1 < $ScriptPath

    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: $scriptName completed" -ForegroundColor Green
        "SUCCESS: $scriptName completed" | Out-File $logFile -Append
    } else {
        Write-Host "ERROR: $scriptName failed!" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        "ERROR: $scriptName failed! $output" | Out-File $logFile -Append
        throw "Script execution failed"
    }
}

# Main execution
try {
    Write-Host "`n===================================" -ForegroundColor Yellow
    Write-Host "Starting Database Setup" -ForegroundColor Yellow
    Write-Host "===================================" -ForegroundColor Yellow

    # Run scripts in order
    $scripts = @(
        "$scriptDir\00_setup\01_create_database.sql",
        "$scriptDir\00_setup\02_create_users.sql",
        "$scriptDir\01_schema\01_create_tables.sql",
        "$scriptDir\01_schema\02_create_indexes.sql",
        "$scriptDir\02_data\01_reference_data.sql"
    )

    foreach ($script in $scripts) {
        if (Test-Path $script) {
            Run-MySQLScript -ScriptPath $script
        } else {
            Write-Host "WARNING: Script not found: $script" -ForegroundColor Yellow
        }
    }

    Write-Host "`n===================================" -ForegroundColor Green
    Write-Host "All scripts completed successfully!" -ForegroundColor Green
    Write-Host "Log file: $logFile" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green
}
catch {
    Write-Host "`nExecution failed: $_" -ForegroundColor Red
    "Execution failed: $_" | Out-File $logFile -Append
}
finally {
    # Clear password from memory
    $mysqlPasswordText = $null
}

Read-Host "`nPress Enter to exit"
```

---

## Running Multiple Scripts

### Sequential Execution

Create `run_all.sql`:

```sql
-- Master script to run all scripts in order

-- Setup
source C:/clinic_project/00_setup/01_create_database.sql;
source C:/clinic_project/00_setup/02_create_users.sql;
source C:/clinic_project/00_setup/03_privileges.sql;

-- Schema
source C:/clinic_project/01_schema/01_create_tables.sql;
source C:/clinic_project/01_schema/02_create_indexes.sql;
source C:/clinic_project/01_schema/03_create_constraints.sql;

-- Data
source C:/clinic_project/02_data/01_reference_data.sql;
source C:/clinic_project/02_data/02_sample_data.sql;

-- Procedures and Views
source C:/clinic_project/03_procedures/01_stored_procedures.sql;
source C:/clinic_project/04_views/01_create_views.sql;

-- Verify
SELECT 'Installation Complete' AS Status;
SHOW TABLES;
```

Execute:
```cmd
mysql -u clinic_admin -p clinic_db < run_all.sql
```

### Parallel Execution (Advanced)

For independent scripts, use parallel processing:

```powershell
# PowerShell parallel execution
$scripts = @(
    "02_data/01_patients_data.sql",
    "02_data/02_doctors_data.sql",
    "02_data/03_appointments_data.sql"
)

$scripts | ForEach-Object -Parallel {
    mysql -u clinic_admin -pPassword123! clinic_db < $_
} -ThrottleLimit 3
```

---

## Error Handling

### Transaction Management

```sql
-- Safe execution template
DELIMITER $$

DROP PROCEDURE IF EXISTS safe_execute$$
CREATE PROCEDURE safe_execute()
BEGIN
    DECLARE exit handler FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error occurred, rolling back changes' AS Error;
    END;

    START TRANSACTION;

    -- Your SQL statements here
    CREATE TABLE patients (
        patient_id INT PRIMARY KEY,
        name VARCHAR(100)
    );

    -- More statements...

    COMMIT;
    SELECT 'All changes committed successfully' AS Status;
END$$

DELIMITER ;

CALL safe_execute();
DROP PROCEDURE safe_execute;
```

### Error Logging

Create `error_handler.sql`:

```sql
-- Create error log table
CREATE TABLE IF NOT EXISTS script_errors (
    error_id INT AUTO_INCREMENT PRIMARY KEY,
    error_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    script_name VARCHAR(255),
    error_code INT,
    error_message TEXT,
    sql_state VARCHAR(5)
);

-- Procedure to log errors
DELIMITER $$

CREATE PROCEDURE log_error(
    IN p_script_name VARCHAR(255),
    IN p_error_code INT,
    IN p_error_message TEXT,
    IN p_sql_state VARCHAR(5)
)
BEGIN
    INSERT INTO script_errors (script_name, error_code, error_message, sql_state)
    VALUES (p_script_name, p_error_code, p_error_message, p_sql_state);
END$$

DELIMITER ;
```

---

## Best Practices

### Script Design

1. **Idempotent Scripts**
   ```sql
   -- Drop if exists
   DROP TABLE IF EXISTS patients;

   -- Create if not exists
   CREATE TABLE IF NOT EXISTS patients (...);

   -- Insert ignore duplicates
   INSERT IGNORE INTO reference_data (...);

   -- Or use REPLACE
   REPLACE INTO configuration (...);
   ```

2. **Use Transactions**
   ```sql
   START TRANSACTION;

   -- Multiple related changes
   ALTER TABLE patients ADD COLUMN email VARCHAR(100);
   UPDATE patients SET email = 'pending@update.com' WHERE email IS NULL;
   ALTER TABLE patients MODIFY COLUMN email VARCHAR(100) NOT NULL;

   COMMIT;
   ```

3. **Include Verification**
   ```sql
   -- After creating table
   SELECT 'Patients table created' AS Status
   WHERE EXISTS (
       SELECT 1 FROM information_schema.tables
       WHERE table_schema = 'clinic_db'
       AND table_name = 'patients'
   );
   ```

### Performance Optimization

1. **Bulk Inserts**
   ```sql
   -- Disable keys for speed
   ALTER TABLE large_table DISABLE KEYS;

   -- Insert data
   INSERT INTO large_table VALUES
   (1, 'data1'),
   (2, 'data2'),
   -- ... many rows
   (10000, 'data10000');

   -- Re-enable keys
   ALTER TABLE large_table ENABLE KEYS;
   ```

2. **Session Optimization**
   ```sql
   -- For bulk operations
   SET unique_checks = 0;
   SET foreign_key_checks = 0;
   SET sql_log_bin = 0;

   -- Your bulk operations here

   -- Reset
   SET unique_checks = 1;
   SET foreign_key_checks = 1;
   SET sql_log_bin = 1;
   ```

---

## Troubleshooting

### Common Issues

#### Issue: Access Denied

**Error**: "ERROR 1044 (42000): Access denied for user"

**Solution**:
```sql
-- Check privileges
SHOW GRANTS FOR CURRENT_USER();

-- Grant necessary privileges (as root)
GRANT ALL PRIVILEGES ON clinic_db.* TO 'clinic_admin'@'localhost';
FLUSH PRIVILEGES;
```

#### Issue: Syntax Error

**Error**: "ERROR 1064 (42000): You have an error in your SQL syntax"

**Solutions**:
1. Check MySQL version compatibility
2. Verify delimiter usage
3. Check for reserved keywords
4. Validate quotes and backticks

#### Issue: File Not Found

**Error**: "ERROR: Failed to open file"

**Solutions**:
1. Use forward slashes in paths: `C:/path/file.sql`
2. Check file permissions
3. Use absolute paths
4. Ensure no spaces in path or quote it

#### Issue: Character Set Issues

**Error**: "Incorrect string value" or garbled characters

**Solution**:
```sql
-- Set character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- In connection string
mysql -u user -p --default-character-set=utf8mb4
```

#### Issue: Out of Memory

**Error**: "Out of memory" on large scripts

**Solutions**:
1. Split into smaller files
2. Increase memory:
   ```ini
   # my.ini
   [mysqld]
   max_allowed_packet = 64M
   ```
3. Use streaming:
   ```cmd
   mysql -u user -p --quick clinic_db < large_file.sql
   ```

### Debug Mode

Enable verbose logging:

```sql
-- Enable general log
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = 'C:/mysql_query.log';

-- Run your scripts

-- Disable when done
SET GLOBAL general_log = 'OFF';
```

---

## Script Examples

### Complete Setup Script

```sql
-- complete_setup.sql
-- Full clinic database setup

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS clinic_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE clinic_db;

-- 2. Create Tables
SOURCE C:/clinic_project/01_schema/01_create_tables.sql;

-- 3. Create Indexes
SOURCE C:/clinic_project/01_schema/02_create_indexes.sql;

-- 4. Load Data
SOURCE C:/clinic_project/02_data/01_reference_data.sql;

-- 5. Create Procedures
SOURCE C:/clinic_project/03_procedures/01_stored_procedures.sql;

-- 6. Create Views
SOURCE C:/clinic_project/04_views/01_create_views.sql;

-- 7. Verify Installation
SELECT
    (SELECT COUNT(*) FROM information_schema.tables
     WHERE table_schema = 'clinic_db') AS tables_count,
    (SELECT COUNT(*) FROM information_schema.routines
     WHERE routine_schema = 'clinic_db') AS procedures_count,
    (SELECT COUNT(*) FROM information_schema.views
     WHERE table_schema = 'clinic_db') AS views_count;

-- 8. Show Summary
SELECT 'Setup Complete!' AS Status;
```

---

## Quick Reference

### Command Line Options

| Option | Description |
|--------|-------------|
| `-u username` | Specify user |
| `-p` | Prompt for password |
| `-pPassword` | Inline password (insecure) |
| `-h hostname` | Server host |
| `-P port` | Server port |
| `-D database` | Default database |
| `--force` | Continue on errors |
| `--verbose` | Show executed statements |
| `--quick` | Don't cache results |
| `--default-character-set=utf8mb4` | Set character encoding |

### Workbench Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open script file |
| Ctrl+Shift+Enter | Execute all |
| Ctrl+Enter | Execute selection |
| Ctrl+S | Save script |
| F5 | Refresh schema |

---

**Document Version**: 1.0
**Last Updated**: January 2024
**MySQL Version**: 8.0.x
**Tested on**: Windows 10/11