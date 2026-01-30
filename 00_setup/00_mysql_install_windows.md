# Installing MySQL Community Server 8.0.x on Windows

This guide covers the installation of MySQL Community Server 8.0.x on Windows using the official MySQL Installer.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Download MySQL Installer](#download-mysql-installer)
3. [Installation Process](#installation-process)
4. [Configuration Steps](#configuration-steps)
5. [Create Database and User](#create-database-and-user)
6. [Verify Installation](#verify-installation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Windows 10/11** (64-bit recommended)
- **4 GB RAM minimum** (8 GB recommended)
- **200 MB free disk space** for MySQL Server
- **Administrator privileges** for installation
- **.NET Framework 4.5.2** or higher (installer will prompt if missing)

### Port Requirements

- **Port 3306** must be available (default MySQL port)
- Check port availability:
  ```cmd
  netstat -an | findstr :3306
  ```
  If output appears, port is in use - see [Troubleshooting](#troubleshooting)

---

## Download MySQL Installer

1. **Navigate to MySQL Downloads**
   - Go to: https://dev.mysql.com/downloads/installer/
   - Select "Windows (x86, 32-bit), MSI Installer"

2. **Choose Installer Version**
   - Select: **mysql-installer-community-8.0.x.msi** (latest 8.0.x version)
   - Size: ~450 MB (includes all products)
   - Click "Download"

3. **Skip Oracle Account** (optional)
   - Click "No thanks, just start my download"
   - Save to Downloads folder

---

## Installation Process

### Step 1: Launch MySQL Installer

1. **Run as Administrator**
   - Right-click `mysql-installer-community-8.0.x.msi`
   - Select "Run as administrator"
   - Accept UAC prompt

2. **Choose Setup Type**
   - Select: **"Custom"** (for precise control)
   - Click "Next"

### Step 2: Select Products

1. **MySQL Server 8.0.x**
   - Expand: MySQL Servers → MySQL Server → MySQL Server 8.0
   - Select: MySQL Server 8.0.x (latest) - X64
   - Click green arrow (→) to move to "Products To Be Installed"

2. **MySQL Workbench 8.0.x**
   - Expand: Applications → MySQL Workbench → MySQL Workbench 8.0
   - Select: MySQL Workbench 8.0.x - X64
   - Click green arrow (→)

3. **MySQL Shell** (optional but recommended)
   - Expand: Applications → MySQL Shell → MySQL Shell 8.0
   - Select: MySQL Shell 8.0.x - X64
   - Click green arrow (→)

4. **Proceed**
   - Click "Next"
   - Click "Execute" to download and install components
   - Wait for all products to show green checkmarks
   - Click "Next"

---

## Configuration Steps

### Step 3: Server Configuration Type

1. **Type and Networking**
   - Config Type: **Development Computer**
   - Connectivity:
     - ✅ TCP/IP: **Enabled**
     - Port: **3306** (keep default)
     - ✅ Open Windows Firewall port for network access
   - Click "Next"

### Step 4: Authentication Method

1. **Authentication**
   - Select: **Use Strong Password Encryption** (Recommended)
   - Click "Next"

### Step 5: Accounts and Roles

1. **Root Account Password**
   ```
   Root Password: [Choose a strong password]
   Repeat Password: [Confirm password]
   ```

   ⚠️ **IMPORTANT**: Save this password securely!

   Suggested strong password example:
   ```
   MyS3cur3P@ssw0rd!2024
   ```

2. **Add User Account** (optional at this stage)
   - Can be done after installation
   - Click "Next"

### Step 6: Windows Service

1. **Configure Windows Service**
   - ✅ **Configure MySQL Server as a Windows Service**
   - Service Name: **MySQL80** (default)
   - ✅ **Start the MySQL Server at System Startup**
   - Run Service as: **Standard System Account**
   - Click "Next"

### Step 7: Apply Configuration

1. **Execute Configuration**
   - Click "Execute"
   - Wait for all steps to complete with green checkmarks
   - Click "Finish"

### Step 8: Complete Installation

1. **Installation Complete**
   - Click "Next"
   - Click "Finish"
   - MySQL Installer will remain open

---

## Create Database and User

### Using Command Line

1. **Open Command Prompt as Administrator**
   ```cmd
   cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
   ```

2. **Connect as root**
   ```cmd
   mysql -u root -p
   ```
   Enter root password when prompted

3. **Create clinic_db database**
   ```sql
   CREATE DATABASE clinic_db
   CHARACTER SET utf8mb4
   COLLATE utf8mb4_unicode_ci;

   SHOW DATABASES;
   ```

4. **Create clinic_admin user**
   ```sql
   -- Create user with localhost access only
   CREATE USER 'clinic_admin'@'localhost'
   IDENTIFIED BY 'Cl1n1c@dm1n2024!';

   -- Grant all privileges on clinic_db
   GRANT ALL PRIVILEGES ON clinic_db.*
   TO 'clinic_admin'@'localhost';

   -- Apply privilege changes
   FLUSH PRIVILEGES;

   -- Verify user creation
   SELECT user, host FROM mysql.user
   WHERE user = 'clinic_admin';
   ```

5. **Test clinic_admin access**
   ```sql
   EXIT;
   ```

   ```cmd
   mysql -u clinic_admin -p clinic_db
   ```
   Enter clinic_admin password when prompted

   ```sql
   -- Verify connection
   SELECT DATABASE();
   SELECT USER();
   EXIT;
   ```

### Using MySQL Workbench (Alternative)

See [01_workbench_connection.md](01_workbench_connection.md) for GUI method.

---

## Verify Installation

### Check Windows Service

1. **Open Services**
   - Press `Win + R`, type `services.msc`, press Enter
   - Find "MySQL80" service
   - Status should be "Running"
   - Startup Type should be "Automatic"

2. **Command Line Verification**
   ```cmd
   sc query MySQL80
   ```

   Expected output:
   ```
   STATE : 4 RUNNING
   ```

### Check MySQL Version

```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" --version
```

Expected output:
```
mysql Ver 8.0.xx for Win64 on x86_64
```

### Test Connection

```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u clinic_admin -p -e "SELECT VERSION();"
```

---

## Troubleshooting

### Issue: Windows Service Not Starting

**Symptoms**: MySQL80 service shows "Stopped" or fails to start

**Solutions**:

1. **Check Error Log**
   ```cmd
   notepad "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini"
   ```
   Look for `log-error` path, then check that file

2. **Reset Service**
   ```cmd
   net stop MySQL80
   net start MySQL80
   ```

3. **Check Event Viewer**
   - Open Event Viewer
   - Windows Logs → Application
   - Look for MySQL errors

4. **Reinstall Service**
   ```cmd
   cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
   mysqld --remove MySQL80
   mysqld --install MySQL80
   net start MySQL80
   ```

### Issue: Port 3306 Already in Use

**Symptoms**: "Port 3306 is already in use" error

**Solutions**:

1. **Identify Process Using Port**
   ```cmd
   netstat -ano | findstr :3306
   ```
   Note the PID (last column)

2. **Check Process**
   ```cmd
   tasklist | findstr [PID]
   ```

3. **Options**:
   - Stop conflicting service
   - OR change MySQL port in my.ini:
     ```ini
     [mysqld]
     port=3307
     ```
   - Restart MySQL service after change

### Issue: Access Denied for Root

**Symptoms**: "Access denied for user 'root'@'localhost'"

**Solutions**:

1. **Reset Root Password**
   - Stop MySQL service:
     ```cmd
     net stop MySQL80
     ```

   - Start MySQL in safe mode:
     ```cmd
     cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
     mysqld --skip-grant-tables --console
     ```

   - Open new Command Prompt:
     ```cmd
     mysql -u root
     ```

     ```sql
     FLUSH PRIVILEGES;
     ALTER USER 'root'@'localhost'
     IDENTIFIED BY 'NewRootPassword123!';
     EXIT;
     ```

   - Stop safe mode MySQL (Ctrl+C)
   - Start normal service:
     ```cmd
     net start MySQL80
     ```

### Issue: Cannot Connect from Workbench

**Symptoms**: Connection failed in MySQL Workbench

**Solutions**:

1. **Check Service Status**
   ```cmd
   sc query MySQL80
   ```

2. **Test Command Line Connection**
   ```cmd
   mysql -u root -p -h 127.0.0.1 -P 3306
   ```

3. **Check Firewall**
   - Windows Defender Firewall
   - Allow app: MySQL Server
   - Or add inbound rule for port 3306

4. **Verify Authentication Plugin**
   ```sql
   SELECT user, host, plugin
   FROM mysql.user
   WHERE user = 'clinic_admin';
   ```

   Should show: `mysql_native_password` or `caching_sha2_password`

### Issue: Character Set Problems

**Symptoms**: Unicode/emoji characters not displaying correctly

**Solution**:
```sql
-- Check database character set
SHOW CREATE DATABASE clinic_db;

-- If not utf8mb4, alter it:
ALTER DATABASE clinic_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

---

## Environment Variables (Optional)

Add MySQL to system PATH for easier command line access:

1. **Open System Properties**
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"

2. **Edit PATH**
   - Under "System variables", select "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\Program Files\MySQL\MySQL Server 8.0\bin`
   - Click "OK" on all windows

3. **Verify**
   - Open new Command Prompt
   - Type: `mysql --version`

---

## Security Recommendations

1. **Strong Passwords**
   - Use mix of uppercase, lowercase, numbers, symbols
   - Minimum 12 characters
   - Different passwords for root and clinic_admin

2. **Regular Updates**
   - Check for MySQL updates monthly
   - Use MySQL Installer to update

3. **Backup Configuration**
   ```cmd
   mysqldump -u root -p --all-databases > backup.sql
   ```

4. **Restrict Network Access**
   - Keep `bind-address = 127.0.0.1` in my.ini
   - Use Windows Firewall rules

---

## Next Steps

1. **Connect with MySQL Workbench**
   - Continue to [01_workbench_connection.md](01_workbench_connection.md)

2. **Run SQL Scripts**
   - See [02_running_sql_scripts.md](02_running_sql_scripts.md)

3. **Create Tables**
   - Execute schema creation scripts
   - Insert sample data

---

## Quick Reference

### Connection Parameters

| Parameter | Value |
|-----------|-------|
| Host | localhost or 127.0.0.1 |
| Port | 3306 |
| Database | clinic_db |
| Admin User | clinic_admin |
| Admin Password | (as set during creation) |
| Root User | root |
| Root Password | (as set during installation) |

### Important Paths

| Item | Default Path |
|------|-------------|
| Installation | C:\Program Files\MySQL\MySQL Server 8.0\ |
| Data Directory | C:\ProgramData\MySQL\MySQL Server 8.0\Data\ |
| Config File | C:\ProgramData\MySQL\MySQL Server 8.0\my.ini |
| Error Log | C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err |

### Useful Commands

```cmd
# Service control
net start MySQL80
net stop MySQL80
net pause MySQL80
net continue MySQL80

# Quick connect
mysql -u clinic_admin -p clinic_db

# Show status
mysqladmin -u root -p status

# Show variables
mysqladmin -u root -p variables
```

---

**Document Version**: 1.0
**Last Updated**: January 2024
**MySQL Version**: 8.0.x
**Windows Versions**: Windows 10/11