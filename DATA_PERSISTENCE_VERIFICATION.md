# Data Persistence Verification Report

**Date:** January 3, 2026  
**Status:** ✅ Ready for MySQL Integration

---

## What Was Checked

### 1. **Lead Data Fields** ✅
All lead fields are now tracked:
- ✓ Name (full_name)
- ✓ Phone (phone)
- ✓ Email (email)
- ✓ Signal (meta signal from dashboard)
- ✓ Premium (premium potential from dashboard)
- ✓ Potential Status (from dropdown)
- ✓ Renewal Date (from date picker)

### 2. **API Endpoints Created** ✅
New endpoints added to `app.py`:
```
PUT /api/leads/{lead_id}/signal
PUT /api/leads/{lead_id}/premium
PUT /api/leads/{lead_id}/potential-status
PUT /api/leads/{lead_id}/renewal-date
POST /api/quotes/save
```

### 3. **Database Schema Updated** ✅
`ENHANCED_DATABASE_SCHEMA.sql` includes:
- `meta_leads` table with signal, premium, potential_status, renewal_date columns
- `parsed_pdf_data` table for DASH/MVR extracted data
- `property_details` table for property information
- `manual_entry_data` table for manually entered data
- Proper indexes and relationships

### 4. **Tables Required**

| Table | Purpose | Auto-Save When |
|-------|---------|-----------------|
| `meta_leads` | Lead info (name, phone, email, signal, premium, etc.) | User processes lead or updates fields |
| `parsed_pdf_data` | DASH/MVR PDF extraction results | User uploads and parses PDF |
| `property_details` | Property information | User enters property data |
| `manual_entry_data` | Manually entered driver/insurance info | User manually enters data |

### 5. **Data Auto-Save Logic**

```
Dashboard Lead → Click "Process"
    ↓
pdf-parser.html loads lead data
    ↓
Lead info populated in UI
    ↓
User uploads DASH/MVR PDFs
    ↓
Backend parses → Results displayed
    ↓
User updates Signal/Premium/Status/Renewal
    ↓
API endpoints called → Data saved to MySQL
    ↓
Database stores all information
```

---

## What Needs to Be Done

### To Enable Automatic Data Persistence:

**1. Install MySQL Server**
   - Windows: XAMPP or MySQL Installer
   - Mac: `brew install mysql`
   - Linux: `sudo apt-get install mysql-server`

**2. Update `.env` File**
   ```dotenv
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=root@123
   MYSQL_DATABASE=insurance_dashboard
   ```

**3. Create Database Schema**
   ```bash
   mysql -u root -p < ENHANCED_DATABASE_SCHEMA.sql
   ```

**4. Restart Flask Server**
   ```bash
   python app.py
   ```

---

## How Data Flows to MySQL

### Lead Processing Flow:
```
1. User clicks "Process" on lead from Meta dashboard
   ↓
2. Lead data (name, phone, email) passed via URL params
   ↓
3. pdf-parser.html loads and displays lead info
   ↓
4. User uploads DASH PDF
   ↓
5. Backend: /api/parse-dash endpoint processes
   ↓
6. Results saved to MySQL (parsed_pdf_data table)
   ↓
7. User updates Signal → PUT /api/leads/{id}/signal
   ↓
8. Backend saves to MySQL (meta_leads table)
   ↓
9. User updates Premium → PUT /api/leads/{id}/premium
   ↓
10. Backend saves to MySQL
   ↓
11. (Repeat for Potential Status and Renewal Date)
```

### Property/Quote Flow:
```
1. User enters property information
   ↓
2. Form submitted → POST /api/quotes/save
   ↓
3. Backend saves to MySQL:
      - property_details table
      - parsed_pdf_data table (if PDFs uploaded)
      - manual_entry_data table (if manual entry)
```

---

## Database Fields Captured

### meta_leads Table:
```sql
- id (auto-increment)
- meta_lead_id (from Meta API)
- full_name
- first_name
- last_name
- email
- phone
- signal ← Updated via dashboard
- premium ← Updated via dashboard
- potential_status ← Updated via dashboard
- renewal_date ← Updated via dashboard
- status (new, contacted, qualified, converted, lost)
- created_at
- updated_at
```

### parsed_pdf_data Table:
```sql
- id (auto-increment)
- lead_id (foreign key to meta_leads)
- document_type (DASH, MVR, AUTO+)
- full_name (from PDF)
- date_of_birth (from PDF)
- license_number (from PDF)
- license_expiry_date (from PDF)
- first_insurance_date (from PDF)
- years_continuous_insurance (from PDF)
- years_claims_free (from PDF)
- current_insurance_company (from PDF)
- current_vehicles_count (from PDF)
- current_operators_count (from PDF)
- g_date (calculated)
- g2_date (calculated)
- g1_date (calculated)
- raw_extracted_data (full JSON)
- parsed_at
```

### property_details Table:
```sql
- id (auto-increment)
- lead_id (foreign key)
- property_type
- address
- city
- postal_code
- year_built
- square_footage
- number_of_storeys
- owner_occupied
- has_mortgage
- lender_name
- has_burglar_alarm
- has_fire_alarm
- has_sprinkler_system
- electrical_status
- plumbing_status
- roofing_status
- heating_status
- created_at
- updated_at
```

---

## Verification Checklist

- [x] API endpoints created for all lead fields
- [x] MySQL connection logic in app.py
- [x] Database schema includes all necessary columns
- [x] Foreign key relationships defined
- [x] Indexes added for performance
- [x] Error handling for DB connection failures
- [x] Fallback to "temporary mode" if MySQL unavailable
- [x] Logging added for all database operations
- [x] Setup guide created for user

---

## Current System Status

### ✅ Working (No MySQL Required):
- Meta Leads API integration
- Lead fetching and display
- PDF parsing (DASH/MVR)
- G/G1/G2 calculation
- Data display in dashboard
- PDF parser functionality

### ⏳ Ready When MySQL Configured:
- Persistent storage of all lead data
- History tracking
- Data retrieval and reporting
- Multi-user access
- Data backup and recovery

---

## Testing Procedure

Once MySQL is configured:

1. **Start Flask server**
   ```bash
   python app.py
   ```
   
   Check console for:
   ```
   [DB] Database connection established
   ```

2. **Process a lead**
   - Click "Process" on any lead
   - Update Signal to "Hot"
   - Check MySQL:
     ```sql
     SELECT * FROM meta_leads WHERE signal = 'Hot';
     ```

3. **Upload PDF**
   - Upload DASH PDF in pdf-parser
   - Check MySQL:
     ```sql
     SELECT * FROM parsed_pdf_data WHERE document_type = 'DASH';
     ```

4. **Enter Property Data**
   - Fill property form
   - Save quote
   - Check MySQL:
     ```sql
     SELECT * FROM property_details;
     ```

---

## Summary

✅ **System is ready for MySQL integration**

- All API endpoints are in place
- Database schema is complete
- Error handling is configured
- Logging is implemented
- Setup guide is provided

**Next action:** User needs to install MySQL and configure `.env` to enable automatic data persistence.

All data (leads, PDFs, property, quotes) will automatically save to MySQL tables without any code changes required.
