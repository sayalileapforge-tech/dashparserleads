# 📊 Database Documentation & Viewing Tools

This folder contains tools to view and export your insurance leads database so your client can see what data is being stored.

## 📁 Files Created

### 1. **database_schema.sql** (Backend)
The complete SQL schema definition file showing the structure of your leads table.

**What it contains:**
- Complete CREATE TABLE statement for the `leads` table
- All 25+ fields with descriptions
- Field types and constraints
- Indexes for performance
- Sample data for demonstration

**How to use:**
- View the schema in any text editor or MySQL client
- Import into MySQL: `mysql -u root -p insurance_leads < database_schema.sql`
- Share with your client to show database structure

---

### 2. **export_database.py** (Backend)
Python script that exports all leads from database to JSON and CSV files.

**What it does:**
- Exports all leads data to JSON format (structured, machine-readable)
- Exports all leads data to CSV format (spreadsheet, client-friendly)
- Shows database statistics (total leads, green/red signals, by status)
- Creates timestamped files so you have historical exports

**How to use:**
```bash
cd backend
python export_database.py
```

**Output:**
- Exports saved to `backend/exports/` folder
- Files: `leads_export_20251228_120000.json` and `.csv`
- Console shows statistics

**For your client:**
- Send them the CSV file to open in Excel
- Send them the JSON file for integration with their systems

---

### 3. **database_dashboard.html** (Root)
Beautiful web dashboard showing real-time database statistics.

**What it displays:**
- ✅ Total leads count
- 🟢 Green signal leads (qualified)
- 🔴 Red signal leads (not qualified)
- 📬 New leads
- 📋 Status breakdown (new, processing, processed, etc.)
- 📋 Recent 10 leads in table format
- 🗄️  Database connection info

**How to use:**
1. Start backend server: `python backend/run_backend.py`
2. Open in browser: `http://localhost:8000/database_dashboard.html`
   OR open file directly from explorer
3. Dashboard auto-refreshes every 10 seconds
4. Click "Refresh" button to update immediately

**For your client:**
- Show them this page to prove database is storing data
- They can check anytime to see latest statistics
- Green/Red signal breakdown shows qualification status

---

## 🚀 Quick Start for Client Demo

### Show Client 1: Real-time Dashboard
```
1. Run: python backend/run_backend.py
2. Open: browser → http://localhost:8000/database_dashboard.html
3. Show real-time stats and recent leads
```

### Show Client 2: Database Schema
```
1. Open: database_schema.sql
2. Show all fields and structure
3. Explain what each field stores
```

### Show Client 3: Exportable Data
```
1. Run: python backend/export_database.py
2. Open: backend/exports/leads_export_*.csv in Excel
3. Show complete data ready for import/analysis
```

---

## 📊 Database Structure Overview

| Field | Type | Description |
|-------|------|-------------|
| id | INT | Unique identifier |
| meta_lead_id | VARCHAR | ID from Meta API (unique) |
| first_name | VARCHAR | Lead's first name |
| last_name | VARCHAR | Lead's last name |
| email | VARCHAR | Email address (indexed) |
| phone | VARCHAR | Phone number (indexed) |
| company_name | VARCHAR | Company name |
| city | VARCHAR | City location |
| state | VARCHAR | State code |
| status | ENUM | new, processing, processed, contacted, etc. |
| signal | ENUM | **green** (qualified) or **red** (not qualified) |
| auto_premium | INT | Auto insurance premium (in cents) |
| home_premium | INT | Home insurance premium (in cents) |
| tenant_premium | INT | Tenant insurance premium (in cents) |
| created_at | DATETIME | When record was created |
| updated_at | DATETIME | Last update timestamp |

---

## 🔄 Data Flow

```
Meta Lead Ads
    ↓
Backend API (/api/leads)
    ↓
MySQL Database (insurance_leads.leads)
    ↓
Dashboard (view real-time)
    ↓
Export Tools (JSON/CSV)
    ↓
Client Reports
```

---

## 💡 Client Talking Points

1. **All Data Stored**: Every lead from Meta is stored in MySQL database with complete information
2. **Signal Tracking**: Each lead marked as green (qualified) or red (not qualified)
3. **Automated Processing**: Status tracks processing stage from new → processed
4. **Exportable**: Data can be exported to CSV/JSON for external analysis
5. **Real-time Dashboard**: Client can check stats anytime via dashboard
6. **Secure**: Data stored on server, indexed for performance

---

## 🛠️ Technical Details

**Database:** MySQL (insurance_leads database)
**Host:** localhost:3306
**User:** root
**Engine:** InnoDB
**Charset:** utf8mb4

**Indexes Created:**
- meta_lead_id (UNIQUE)
- status (for filtering)
- signal (for Event Manager)
- email, phone (for lookups)
- created_at, updated_at (for sorting)

---

## 📝 Notes for You

- Database persists data even after server restart
- New leads automatically added to database when synced
- Signal status saved and loaded from database
- Dashboard can be shared with client via URL
- Export files can be emailed as reports
- Schema can be modified in `app/models/lead.py` and code needs restart

---

**Last Updated:** 2025-12-28  
**Status:** ✅ Production Ready
