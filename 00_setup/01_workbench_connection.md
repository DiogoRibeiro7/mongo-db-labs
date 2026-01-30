# Connecting to MySQL with MySQL Workbench 8.0.x

This guide covers setting up and managing MySQL connections using MySQL Workbench on Windows.

## Table of Contents

1. [Launch MySQL Workbench](#launch-mysql-workbench)
2. [Create Connection for Root](#create-connection-for-root)
3. [Create Connection for clinic_admin](#create-connection-for-clinic_admin)
4. [Connection Management](#connection-management)
5. [Using Workbench Interface](#using-workbench-interface)
6. [Creating Database and User via GUI](#creating-database-and-user-via-gui)
7. [Troubleshooting Connection Issues](#troubleshooting-connection-issues)

---

## Launch MySQL Workbench

### First Launch

1. **Start MySQL Workbench**
   - From Start Menu: MySQL → MySQL Workbench 8.0
   - Or search: "MySQL Workbench"

2. **Welcome Screen**
   - You'll see "MySQL Connections" section
   - May have "Local instance MySQL80" if detected during installation

3. **Interface Overview**
   - **Home**: Connection management
   - **SQL Development**: Query editor and execution
   - **Server Administration**: User and permission management
   - **Data Modeling**: Visual database design

---

## Create Connection for Root

### Step 1: New Connection

1. **Click the + Icon**
   - Next to "MySQL Connections" label
   - Opens "Setup New Connection" dialog

2. **Configure Root Connection**
   ```
   Connection Name: Local MySQL Root
   Connection Method: Standard (TCP/IP)

   Parameters:
   - Hostname: 127.0.0.1
   - Port: 3306
   - Username: root
   ```

3. **Store Password (Optional)**
   - Click "Store in Vault..."
   - Enter root password
   - Click "OK"

4. **Test Connection**
   - Click "Test Connection" button
   - Should see: "Successfully made the MySQL connection"
   - If failed, see [Troubleshooting](#troubleshooting-connection-issues)

5. **Save Connection**
   - Click "OK"
   - Connection appears on home screen

### Step 2: Connect as Root

1. **Double-click** "Local MySQL Root" tile
2. Enter password if not stored
3. SQL Editor opens with root privileges

---

## Create Connection for clinic_admin

### Step 1: New Connection for clinic_admin

1. **Click + Icon** again

2. **Configure clinic_admin Connection**
   ```
   Connection Name: Clinic Database Admin
   Connection Method: Standard (TCP/IP)

   Parameters:
   - Hostname: localhost
   - Port: 3306
   - Username: clinic_admin
   - Default Schema: clinic_db
   ```

3. **Important**: Set Default Schema
   - Click "..." button next to Default Schema
   - If clinic_db exists, select it
   - If not, leave blank (will create later)

4. **Store Password**
   - Click "Store in Vault..."
   - Enter clinic_admin password
   - Click "OK"

5. **Test Connection**
   - Click "Test Connection"
   - Should succeed if user was created properly

6. **Save**
   - Click "OK"

### Step 2: Connection Tile Customization

1. **Right-click** on connection tile
2. Select "Edit Connection"
3. **Advanced Tab**:
   ```
   SQL_MODE: TRADITIONAL
   Others → OPT_CONNECT_TIMEOUT: 10
   ```

4. **SSL Tab**:
   - Use SSL: "No" (for local development)
   - For production, configure SSL

---

## Connection Management

### Organizing Connections

1. **Create Connection Groups**
   - Right-click in connections area
   - Select "Create Connection Group"
   - Name: "Development" or "Clinic Project"
   - Drag connections into group

2. **Connection Colors**
   - Right-click connection → "Set Color"
   - Suggestions:
     - Red: Root/Admin connections
     - Green: Application user connections
     - Blue: Read-only connections

### Connection Properties

1. **View Properties**
   - Right-click connection → "Properties"
   - Shows all connection parameters

2. **Export Connection**
   - File → Export → Export MySQL Connections
   - Save as .xml for backup

3. **Import Connection**
   - File → Import → Import MySQL Connections
   - Useful for team sharing

---

## Using Workbench Interface

### SQL Editor Layout

1. **Query Tab**
   - Write SQL statements
   - Syntax highlighting
   - Auto-completion (Ctrl+Space)

2. **Result Grid**
   - Shows query results
   - Editable for INSERT/UPDATE
   - Export options (CSV, JSON, XML)

3. **Action Output**
   - Shows executed statements
   - Error messages
   - Execution time

4. **Object Browser** (Left Panel)
   - SCHEMAS section
   - Tables, Views, Procedures
   - Right-click for context menu

### Essential Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Enter | Execute statement at cursor |
| Ctrl+Shift+Enter | Execute all statements |
| Ctrl+T | New query tab |
| Ctrl+W | Close current tab |
| Ctrl+S | Save script |
| Ctrl+Space | Auto-complete |
| Ctrl+B | Beautify SQL |
| F5 | Refresh schema list |

### Executing Queries

1. **Single Statement**
   ```sql
   SELECT * FROM clinic_db.patients;
   ```
   - Place cursor on line
   - Press Ctrl+Enter

2. **Multiple Statements**
   ```sql
   USE clinic_db;

   SELECT COUNT(*) FROM patients;
   SELECT COUNT(*) FROM doctors;
   ```
   - Select all statements
   - Press Ctrl+Shift+Enter

3. **Execute from File**
   - File → Open SQL Script (Ctrl+O)
   - Navigate to .sql file
   - Click lightning bolt icon or Ctrl+Shift+Enter

---

## Creating Database and User via GUI

### Create Database

1. **Connect as Root**

2. **Right-click in SCHEMAS area**
   - Select "Create Schema..."

3. **Configure Schema**
   ```
   Schema Name: clinic_db
   Default Collation: utf8mb4_unicode_ci
   Default Encryption: No
   ```

4. **Review SQL**
   - Click "Apply"
   - Review generated SQL:
   ```sql
   CREATE SCHEMA `clinic_db`
   DEFAULT CHARACTER SET utf8mb4
   COLLATE utf8mb4_unicode_ci;
   ```

5. **Execute**
   - Click "Apply"
   - Click "Finish"

### Create User

1. **Open User Management**
   - From home: Server → Users and Privileges
   - Or: Management tab → Users and Privileges

2. **Add Account**
   - Click "Add Account" button

3. **Login Tab**
   ```
   Login Name: clinic_admin
   Authentication Type: Standard
   Limit to Hosts Matching: localhost
   Password: [Enter password]
   Confirm Password: [Re-enter]
   ```

4. **Account Limits Tab** (Optional)
   ```
   Max Queries: 0 (unlimited)
   Max Updates: 0 (unlimited)
   Max Connections: 100
   Max User Connections: 10
   ```

5. **Administrative Roles Tab**
   - Leave unchecked for application user
   - Check "DBA" only for admin users

6. **Schema Privileges Tab**
   - Click "Add Entry..."
   - Selected schema: `clinic_db`
   - Click "OK"
   - Select privileges:
     - ✅ SELECT, INSERT, UPDATE, DELETE
     - ✅ CREATE, DROP, ALTER
     - ✅ INDEX, REFERENCES
     - ✅ CREATE TEMPORARY TABLES
     - ✅ EXECUTE, TRIGGER, EVENT
   - Or click "Select ALL" for full access

7. **Apply**
   - Click "Apply"
   - User created with privileges

### Verify User Access

1. **Test in SQL Editor**
   ```sql
   -- Check user exists
   SELECT user, host
   FROM mysql.user
   WHERE user = 'clinic_admin';

   -- Check privileges
   SHOW GRANTS FOR 'clinic_admin'@'localhost';
   ```

2. **Test Connection**
   - Create new connection with clinic_admin
   - Verify can access clinic_db

---

## Troubleshooting Connection Issues

### Issue: Connection Failed - Can't connect to MySQL server

**Diagnosis Steps**:

1. **Check Service Status**
   - Open Services (services.msc)
   - Verify MySQL80 is Running

2. **Test Command Line**
   ```cmd
   mysql -u root -p -h 127.0.0.1
   ```

3. **Check Error Details**
   - In Workbench, click "Show Details"
   - Common error codes:
     - 2003: Can't connect (service not running)
     - 1045: Access denied (wrong password)
     - 1049: Unknown database

**Solutions**:

**Error 2003 - Can't connect**:
```cmd
# Start service
net start MySQL80

# Check if listening
netstat -an | findstr :3306
```

**Error 1045 - Access denied**:
- Verify username and password
- Check host (localhost vs 127.0.0.1 vs %)
- Try command line first

**Error 1049 - Unknown database**:
- Remove default schema
- Or create database first

### Issue: Connection Timeout

**Symptoms**: Connection takes long time then fails

**Solutions**:

1. **Increase Timeout**
   - Edit Connection → Advanced tab
   - OPT_CONNECT_TIMEOUT: 60
   - OPT_READ_TIMEOUT: 60
   - OPT_WRITE_TIMEOUT: 60

2. **Use IP Instead of Hostname**
   - Change "localhost" to "127.0.0.1"
   - Avoids DNS resolution

3. **Check Firewall**
   ```cmd
   # Add firewall exception
   netsh advfirewall firewall add rule name="MySQL Port 3306" protocol=TCP dir=in localport=3306 action=allow
   ```

### Issue: SSL/TLS Connection Required

**Symptoms**: "SSL connection error" or "require_secure_transport"

**Solutions**:

1. **Disable SSL Requirement** (Development only)
   ```sql
   -- Connect as root
   ALTER USER 'clinic_admin'@'localhost'
   REQUIRE NONE;

   FLUSH PRIVILEGES;
   ```

2. **Configure SSL in Connection**
   - Edit Connection → SSL tab
   - Use SSL: "Require"
   - SSL CA File: Point to ca.pem
   - SSL Cert File: Point to client-cert.pem
   - SSL Key File: Point to client-key.pem

### Issue: Authentication Plugin Error

**Symptoms**: "Authentication plugin 'caching_sha2_password' cannot be loaded"

**Solutions**:

1. **Update Workbench**
   - Ensure Workbench 8.0.x matches MySQL 8.0.x

2. **Change Authentication Plugin**
   ```sql
   ALTER USER 'clinic_admin'@'localhost'
   IDENTIFIED WITH mysql_native_password
   BY 'YourPassword123!';

   FLUSH PRIVILEGES;
   ```

### Issue: Lost Connection During Query

**Symptoms**: "Lost connection to MySQL server during query"

**Solutions**:

1. **Increase Timeouts**
   ```sql
   -- Check current values
   SHOW VARIABLES LIKE '%timeout%';

   -- Increase in my.ini
   [mysqld]
   interactive_timeout = 28800
   wait_timeout = 28800
   net_read_timeout = 90
   net_write_timeout = 90
   ```

2. **Restart MySQL Service**
   ```cmd
   net stop MySQL80
   net start MySQL80
   ```

---

## Best Practices

### Connection Security

1. **Don't Store Root Password**
   - Use vault only for development
   - Production: Enter manually

2. **Use Specific Default Schema**
   - Prevents accidental wrong database operations

3. **Connection Naming Convention**
   ```
   [Environment]_[Database]_[User]
   Examples:
   - DEV_Clinic_Admin
   - TEST_Clinic_ReadOnly
   - PROD_Clinic_App
   ```

### Query Editor Tips

1. **Use Transactions**
   ```sql
   START TRANSACTION;

   -- Your changes
   UPDATE patients SET status = 'Active';

   -- Review then:
   COMMIT;  -- or ROLLBACK;
   ```

2. **Always Specify Database**
   ```sql
   -- Good
   SELECT * FROM clinic_db.patients;

   -- Risky
   SELECT * FROM patients;
   ```

3. **Save Important Queries**
   - File → Save Script As...
   - Organize in folders

### Performance Monitoring

1. **Enable Query Stats**
   - Query → Show Query Statistics
   - Shows execution plan

2. **Visual Explain**
   - Query → Visual Explain
   - Graphical execution plan

3. **Profiling**
   ```sql
   SET profiling = 1;

   -- Run your query
   SELECT * FROM patients;

   SHOW PROFILES;
   SHOW PROFILE FOR QUERY 1;
   ```

---

## Advanced Features

### SQL Snippets

1. **Create Snippet**
   - View → Panels → Snippets
   - Right-click → Add Snippet
   - Example:
   ```sql
   -- Name: Count All Tables
   SELECT
       table_name,
       table_rows
   FROM information_schema.tables
   WHERE table_schema = DATABASE()
   ORDER BY table_rows DESC;
   ```

2. **Use Snippet**
   - Double-click snippet to insert

### Database Synchronization

1. **Compare Schemas**
   - Database → Compare Schemas
   - Select source and target
   - Review differences

2. **Migration Wizard**
   - Database → Migration Wizard
   - Migrate from other databases

### Backup and Restore

1. **Export Database**
   - Server → Data Export
   - Select clinic_db
   - Export to Self-Contained File

2. **Import Database**
   - Server → Data Import
   - Import from Self-Contained File

---

## Next Steps

1. **Run SQL Scripts**
   - Continue to [02_running_sql_scripts.md](02_running_sql_scripts.md)

2. **Create Tables**
   - Design schema visually
   - Or execute DDL scripts

3. **Explore Features**
   - Performance Dashboard
   - Server Status
   - Client Connections

---

## Quick Reference Card

### Connection Checklist

- [ ] MySQL Service running
- [ ] Port 3306 accessible
- [ ] Correct hostname (localhost vs 127.0.0.1)
- [ ] Correct username
- [ ] Correct password
- [ ] Database exists (if specified)
- [ ] User has privileges
- [ ] Firewall allows connection
- [ ] SSL/TLS configured (if required)

### Common Connection Strings

```
# Local root
mysql://root:password@localhost:3306/

# Local clinic_admin
mysql://clinic_admin:password@localhost:3306/clinic_db

# With SSL
mysql://user:password@localhost:3306/clinic_db?ssl-mode=REQUIRED
```

---

**Document Version**: 1.0
**Last Updated**: January 2024
**MySQL Workbench Version**: 8.0.x
**Tested on**: Windows 10/11