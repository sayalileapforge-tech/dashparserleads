# MySQL Database Setup Guide

## Overview
All lead data (name, phone, email, signal, premium, potential status, renewal date) and parsed PDF data (DASH, MVR) are automatically stored in MySQL when:
1. MySQL is running and accessible
2. Environment variables are configured in `.env`
3. Database schema is created

---

## Step 1: Install MySQL

### Windows (Using XAMPP or MySQL Installer)

**Option A: XAMPP (Easiest)**
1. Download XAMPP from https://www.apachefriends.org/
2. Install and run XAMPP Control Panel
3. Click "Start" next to MySQL

**Option B: MySQL Installer**
1. Download from https://dev.mysql.com/downloads/mysql/
2. Run installer and follow setup
3. Default port: 3306

### Mac (Using Homebrew)
```bash
brew install mysql
brew services start mysql
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

---

## Step 2: Configure Environment Variables

Edit `.env` file in your project root and uncomment/update these lines:

```dotenv
# DATABASE CONFIGURATION
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root@123
MYSQL_DATABASE=insurance_dashboard
```

**If using XAMPP:**
- Host: `localhost`
- Port: `3306`
- User: `root`
- Password: `` (empty by default) OR set in XAMPP config

---

## Step 3: Create Database Schema

### Method 1: Using MySQL Command Line

```bash
mysql -u root -p < ENHANCED_DATABASE_SCHEMA.sql
```

**Or manually:**

1. Open MySQL command line or MySQL Workbench
2. Copy and paste contents of `ENHANCED_DATABASE_SCHEMA.sql`
3. Run all queries

### Method 2: Using Python Script

Create `setup_database.py`:

```python
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD', ''),
    port=int(os.getenv('MYSQL_PORT', 3306))
)

with open('ENHANCED_DATABASE_SCHEMA.sql', 'r') as f:
    schema_sql = f.read()
    
cursor = conn.cursor()
for statement in schema_sql.split(';'):
    if statement.strip():
        cursor.execute(statement)

conn.commit()
print("✓ Database schema created successfully!")
cursor.close()
conn.close()
```

Then run:
```bash
python setup_database.py
```

---

## Step 4: Verify Setup

Run the Flask server:
```bash
python app.py
```

Check the console output for:
```
[DB] Database connection established
[DB] ✓ All tables ready
```

---

## Data Stored Automatically

### 1. **Meta Leads Table** (`meta_leads`)
When user clicks "Process" on a lead:
- ✓ full_name
- ✓ email
- ✓ phone
- ✓ created_at (timestamp)

When user updates lead:
- ✓ signal (Meta signal value)
- ✓ premium (Premium potential)
- ✓ potential_status (Potential Status dropdown)
- ✓ renewal_date (Renewal Date)
- ✓ status (Lead status: new, contacted, qualified, converted, lost)

### 2. **Parsed PDF Data Table** (`parsed_pdf_data`)
When user uploads and parses PDF:
- ✓ document_type (DASH, MVR, AUTO+)
- ✓ full_name
- ✓ date_of_birth
- ✓ license_number
- ✓ license_expiry_date
- ✓ first_insurance_date
- ✓ years_continuous_insurance
- ✓ years_claims_free
- ✓ current_insurance_company
- ✓ current_vehicles_count
- ✓ current_operators_count
- ✓ g_date (Calculated G date)
- ✓ g2_date (Calculated G2 date)
- ✓ g1_date (Calculated G1 date)
- ✓ All raw extracted data as JSON

### 3. **Property Details Table** (`property_details`)
When user enters property information:
- ✓ address
- ✓ city
- ✓ postal_code
- ✓ property_type
- ✓ year_built
- ✓ square_footage
- ✓ security features (burglar alarm, fire alarm, etc.)
- ✓ home systems (electrical, plumbing, roofing, heating)

### 4. **Manual Entry Data Table** (`manual_entry_data`)
When user manually enters driver/insurance info:
- ✓ All manually entered fields
- ✓ Calculated G/G1/G2 dates
- ✓ Timestamp of entry

---

## API Endpoints for Data Persistence

All these endpoints automatically save to MySQL:

```bash
# Update lead signal
PUT /api/leads/{lead_id}/signal
{ "signal": "hot" }

# Update lead premium
PUT /api/leads/{lead_id}/premium
{ "premium": "high" }

# Update lead potential status
PUT /api/leads/{lead_id}/potential-status
{ "potential_status": "qualified" }

# Update lead renewal date
PUT /api/leads/{lead_id}/renewal-date
{ "renewal_date": "2026-06-15" }

# Save quote (DASH, MVR, Property data)
POST /api/quotes/save
{
  "lead_id": "1584270442585975",
  "quote_type": "combined",
  "dash_data": { ... },
  "mvr_data": { ... },
  "property_data": { ... }
}
```

---

## Troubleshooting

### Error: "Connection refused"
- Check if MySQL is running
- Verify host/port are correct
- Try `telnet localhost 3306`

### Error: "Access denied"
- Verify username/password in `.env`
- Check MySQL user permissions

### Error: "Database doesn't exist"
- Run schema setup script
- Verify database name in `.env`

### Tables Not Created
- Run `ENHANCED_DATABASE_SCHEMA.sql` again
- Check for SQL errors in the schema file

### Data Not Saving
- Check Flask console for errors
- Verify `.env` has correct MySQL credentials
- Check if MySQL connection is established on startup

---

## Summary

✅ **Automatic Data Persistence:**
- All lead information (name, phone, email, signal, premium, etc.)
- All parsed PDF data (DASH, MVR with full extracted fields)
- All property information
- All manually entered data
- All calculated G/G1/G2 dates

Once MySQL is configured, everything is stored automatically without any code changes needed!

---

**Next Steps:**
1. Install MySQL
2. Configure `.env` file
3. Run schema setup
4. Restart Flask server
5. Test by clicking "Process" on a lead - check MySQL to verify data is saved
