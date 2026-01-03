# Insurance Dashboard - Complete Data Persistence Implementation

## Overview

This is a **complete, production-ready data persistence solution** for the Insurance Dashboard (Auto + Property). It captures ALL manual user-entered data and stores it in a normalized MySQL database using a RESTful Node.js backend API.

**Key Principle**: Data persists from the moment user enters information until API submission. No calculations, validations, or business logic - just clean data storage.

---

## 📁 File Structure

```
dashboard ui/
├── Untitled-2.html                 # Main dashboard (HTML with integrated data collection)
├── 01_DATABASE_SCHEMA.sql          # MySQL database structure (10 tables)
├── 02_backend_server.js            # Express.js API server with endpoints
├── 03_form_data_collection.js      # Frontend data collection & submission module
├── README.md                        # This file
├── README_BACKEND.md                # Backend-specific setup guide
├── package.json                     # Node.js dependencies (create this)
└── .env                             # Environment configuration (create this)
```

---

## 🗄️ Database Schema Overview

### Core Tables (Reference)

```sql
customers                 -- Master customer records
├── auto_quotes          -- Auto insurance quotes (FK: customer_id)
│   ├── drivers          -- Multiple drivers per quote
│   │   └── driver_documents  -- Upload file references (dash, mvr, auto+)
│   ├── vehicles         -- Vehicle info (reserved for expansion)
│   └── auto_contact_info -- Contact details specific to auto
│
└── property_quotes      -- Property insurance quotes (FK: customer_id)
    └── properties       -- Multiple properties per quote
        ├── property_ownership      -- Ownership details
        ├── property_mortgage       -- Mortgage information
        ├── property_home_details   -- Construction & systems
        └── property_security       -- Safety features
```

### Data Flow Diagram

```
User Enters Data (Form)
         ↓
JavaScript collects all fields
         ↓
collectAutoVehicleData()
collectAutoDriversData()
collectPropertyData()
         ↓
Payload sent to Backend API
         ↓
POST /api/quotes/auto (or /property)
         ↓
Backend validates & uses transactions
         ↓
MySQL: Insert customer → quote → details → documents
         ↓
Return quoteId & customerId
         ↓
Frontend shows success notification
         ↓
✓ Data persisted reliably in database
```

---

## 🚀 Quick Start Guide

### Step 1: Setup Database

```bash
# Connect to MySQL
mysql -u root -p

# Import schema
mysql -u root -p insurance_dashboard < 01_DATABASE_SCHEMA.sql

# Verify tables created
USE insurance_dashboard;
SHOW TABLES;
```

Expected tables:
```
customers
auto_quotes
drivers
driver_documents
vehicles
auto_contact_info
property_quotes
properties
property_ownership
property_mortgage
property_home_details
property_security
```

### Step 2: Setup Backend

```bash
# Create package.json
cat > package.json << 'EOF'
{
  "name": "insurance-dashboard-api",
  "version": "1.0.0",
  "description": "Insurance Dashboard Backend API",
  "main": "02_backend_server.js",
  "scripts": {
    "start": "node 02_backend_server.js",
    "dev": "nodemon 02_backend_server.js"
  },
  "keywords": ["insurance", "api", "dashboard"],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "express": "^4.18.2",
    "mysql2": "^3.6.0",
    "cors": "^2.8.5",
    "body-parser": "^1.20.2",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
EOF

# Create .env file
cat > .env << 'EOF'
PORT=3001
NODE_ENV=development
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=insurance_dashboard
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
EOF

# Install dependencies
npm install

# Start backend (development)
npm run dev

# Or production
npm start
```

Expected output:
```
╔═══════════════════════════════════════════════════════════════╗
║         Insurance Dashboard API Server Started               ║
╠═══════════════════════════════════════════════════════════════╣
║ Server:        http://localhost:3001
║ Database:      insurance_dashboard
║ Environment:   development
╚═══════════════════════════════════════════════════════════════╝
```

### Step 3: Open Dashboard

```bash
# Simply open the updated HTML in your browser
# File → Open File → Untitled-2.html

# Or serve it with a local server
npx http-server

# Access at http://localhost:8080
```

### Step 4: Test Data Persistence

1. Open dashboard in browser
2. Search for customer (mock: "John" or "416")
3. Fill out Auto Quote form
4. Click "Save Quote" button
5. Watch browser console for success message
6. Check database:

```sql
SELECT * FROM auto_quotes;
SELECT * FROM drivers WHERE auto_quote_id = 1;
SELECT * FROM driver_documents WHERE driver_id = 1;
```

---

## 📊 Data Collection Map

### AUTO QUOTE - All Fields Captured

```javascript
{
  customer: {
    firstName: "John",
    lastName: "Doe",
    phone: "(416) 555-0123",
    email: "john@example.com"
  },
  vehicle: {
    ownership: "owned",           // Radio: owned | financed | leased
    use: "pleasure",              // Radio: pleasure | commute | business
    annualKm: 15000,              // Number input
    winterTires: true,            // Radio: yes | no
    antiTheft: false              // Radio: yes | no
  },
  drivers: [
    {
      driverNumber: 1,            // Sequential number
      relationship: "applicant",  // Dropdown: applicant | spouse | son | daughter | parent | sibling | other
      documents: {
        dash: {
          fileName: "driver1_dash.pdf",
          filePath: "/uploads/driver1_dash.pdf"
        },
        autoplus: { ... },
        mvr: { ... }
      }
    },
    {
      driverNumber: 2,
      relationship: "spouse",
      documents: { ... }
    }
  ],
  contact: {
    phone: "(416) 555-0123",      // Text input
    email: "john@example.com"     // Email input
  }
}
```

### PROPERTY QUOTE - All Fields Captured

```javascript
{
  customer: { ... },  // Same structure as auto
  properties: [
    {
      propertySequence: 1,
      type: "Primary Home",           // Dropdown: Primary Home | Secondary - Rented | Secondary - Non Rented | Vacation Home
      address: "456 Oak Avenue",
      city: "Toronto",
      postal: "M5V 3A8",
      purchased: "2015-06-20",
      firstInsured: "2015",
      ownerOccupied: true,            // Radio: Yes | No
      
      mortgage: {
        hasMortgage: true,            // Radio: Yes | No
        lender: "TD Bank",            // Text
        numberOfMortgages: 1          // Number
      },
      
      details: {
        yearBuilt: 1995,              // Number
        storeys: "2",                 // Text
        units: 1,                     // Number
        families: 1,                  // Number
        livingArea: 2800,             // Number (sq ft)
        basementArea: 1200,           // Number (sq ft)
        basementFinished: 70,         // Number (%)
        fullBaths: 3,                 // Number
        halfBaths: 1,                 // Number
        electrical: "Upgraded 2018",  // Text
        plumbing: "Updated 2010",     // Text
        roofing: "Asphalt 2016",      // Text
        heating: "Gas forced air",    // Text
        inlawSuite: false,            // Radio: Yes | No
        basementApartment: false      // Radio: Yes | No
      },
      
      security: {
        burglarAlarm: true,           // Checkbox
        fireAlarm: true,              // Checkbox
        sprinkler: true,              // Checkbox
        blockWatch: false,            // Checkbox
        walledCommunity: false,       // Checkbox
        deadbolts: true,              // Checkbox
        smokeDetectors: 5,            // Number
        fireExtinguishers: 3          // Number
      }
    },
    {
      propertySequence: 2,  // Multiple properties per quote
      ...
    }
  ]
}
```

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:3001
```

### 1. Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "message": "Insurance Dashboard API is running",
  "timestamp": "2024-12-25T10:30:00.000Z"
}
```

---

### 2. Save Auto Quote
```
POST /api/quotes/auto
Content-Type: application/json
```

**Request Body:**
```json
{
  "customer": {
    "firstName": "John",
    "lastName": "Doe",
    "phone": "(416) 555-0123",
    "email": "john@example.com"
  },
  "vehicle": {
    "ownership": "owned",
    "use": "pleasure",
    "annualKm": 15000,
    "winterTires": true,
    "antiTheft": false
  },
  "drivers": [
    {
      "driverNumber": 1,
      "relationship": "applicant",
      "documents": {
        "dash": {
          "fileName": "driver1_dash.pdf",
          "filePath": "/uploads/driver1_dash.pdf"
        }
      }
    }
  ],
  "contact": {
    "phone": "(416) 555-0123",
    "email": "john@example.com"
  }
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Auto quote saved successfully",
  "quoteId": 1,
  "customerId": 1,
  "driversCount": 1,
  "timestamp": "2024-12-25T10:30:00.000Z"
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "message": "Error saving auto quote",
  "error": "Missing required field: firstName"
}
```

---

### 3. Save Property Quote
```
POST /api/quotes/property
Content-Type: application/json
```

**Request Body:**
```json
{
  "customer": {
    "firstName": "Jane",
    "lastName": "Smith",
    "phone": "(416) 555-9999",
    "email": "jane@example.com"
  },
  "properties": [
    {
      "propertySequence": 1,
      "type": "Primary Home",
      "address": "456 Oak Ave",
      "city": "Toronto",
      "postal": "M5V 3A8",
      "purchased": "2015-06-20",
      "firstInsured": "2015",
      "ownerOccupied": true,
      "mortgage": {
        "hasMortgage": true,
        "lender": "TD Bank",
        "numberOfMortgages": 1
      },
      "details": {
        "yearBuilt": 1995,
        "storeys": "2",
        "units": 1,
        "families": 1,
        "livingArea": 2800,
        "basementArea": 1200,
        "basementFinished": 70,
        "fullBaths": 3,
        "halfBaths": 1,
        "electrical": "Upgraded 2018",
        "plumbing": "Updated 2010",
        "roofing": "Asphalt 2016",
        "heating": "Gas forced air",
        "inlawSuite": false,
        "basementApartment": false
      },
      "security": {
        "burglarAlarm": true,
        "fireAlarm": true,
        "sprinkler": true,
        "blockWatch": false,
        "walledCommunity": false,
        "deadbolts": true,
        "smokeDetectors": 5,
        "fireExtinguishers": 3
      }
    }
  ]
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Property quote saved successfully",
  "propertyQuoteId": 1,
  "customerId": 1,
  "propertiesCount": 1,
  "propertyIds": [1],
  "timestamp": "2024-12-25T10:30:00.000Z"
}
```

---

## 🔑 Key Features

✅ **All Data Captured**
- Every input, select, radio, checkbox, and dynamically added item
- Multiple drivers per auto quote
- Multiple properties per property quote
- File references (names/paths, not binaries)

✅ **Normalized Database Structure**
- 10 properly designed tables with foreign keys
- Auto-increment primary keys
- ENUM types for fixed options
- Boolean fields where appropriate
- Indexes for performance

✅ **Clean Data Flow**
- Frontend collects exactly what user enters
- No calculations or transformations
- Backend receives clean JSON
- Uses prepared statements (SQL injection safe)
- Transactional integrity for multi-step operations

✅ **API-Driven Architecture**
- RESTful endpoints
- JSON request/response
- CORS-enabled for frontend integration
- Error handling and validation
- Modular and extensible design

✅ **Production Ready**
- Connection pooling
- Transaction support
- Error logging
- Configuration management
- Stateless design for scalability

---

## 🧪 Testing

### Browser Console Testing

```javascript
// Test auto quote collection
const autoData = {
  customer: collectCustomerData(),
  vehicle: collectAutoVehicleData(),
  drivers: collectAutoDriversData(),
  contact: collectAutoContactInfo()
};
console.log('Auto Quote:', autoData);

// Test property quote collection
const propData = {
  customer: collectCustomerData(),
  properties: collectPropertyData()
};
console.log('Property Quote:', propData);

// Test backend connection
checkBackendConnection();

// Submit auto quote
submitAutoQuote();

// Submit property quote
submitPropertyQuote();
```

### cURL Testing

```bash
# Test backend health
curl http://localhost:3001/api/health

# Save auto quote
curl -X POST http://localhost:3001/api/quotes/auto \
  -H "Content-Type: application/json" \
  -d '{"customer":{"firstName":"John","lastName":"Doe"},"vehicle":{},"drivers":[],"contact":{}}'

# Save property quote
curl -X POST http://localhost:3001/api/quotes/property \
  -H "Content-Type: application/json" \
  -d '{"customer":{"firstName":"Jane","lastName":"Smith"},"properties":[]}'
```

---

## 🔍 Verify Data in Database

```sql
-- View all customers
SELECT * FROM customers;

-- View all auto quotes
SELECT * FROM auto_quotes;

-- View drivers for a quote
SELECT * FROM drivers WHERE auto_quote_id = 1;

-- View driver documents
SELECT * FROM driver_documents WHERE driver_id = 1;

-- View all properties
SELECT * FROM properties;

-- View property details
SELECT p.*, po.*, pm.* 
FROM properties p
LEFT JOIN property_ownership po ON p.id = po.property_id
LEFT JOIN property_mortgage pm ON p.id = pm.property_id;

-- View security info
SELECT * FROM property_security WHERE property_id = 1;

-- Full join to see relationships
SELECT 
  c.first_name, c.last_name,
  aq.id as auto_quote_id,
  d.driver_number, d.relationship,
  dd.doc_type, dd.file_name
FROM customers c
LEFT JOIN auto_quotes aq ON c.id = aq.customer_id
LEFT JOIN drivers d ON aq.id = d.auto_quote_id
LEFT JOIN driver_documents dd ON d.id = dd.driver_id;
```

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
- Ensure backend server is running: `npm run dev`
- Check API_BASE_URL in 03_form_data_collection.js
- Check CORS settings in .env

### "Unknown database"
- Run: `mysql -u root -p < 01_DATABASE_SCHEMA.sql`

### "Access Denied" error
- Update DB_USER and DB_PASSWORD in .env
- Verify MySQL credentials

### Data not saving
- Check browser console for errors
- Check backend console for SQL errors
- Verify customer is selected before submit
- Check network tab in DevTools for response

### File upload not working
- File references are stored as paths only, not actual files
- Ensure `/uploads` directory exists if needed
- Update file_path value in form collection

---

## 📈 Scaling & Future Enhancement

### File Upload Handling
Currently, file paths are stored as references only. To implement actual file uploads:

```javascript
// In 03_form_data_collection.js
async function uploadFile(file, driverNumber, docType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('driverNumber', driverNumber);
    formData.append('docType', docType);
    
    const response = await fetch(`${API_BASE_URL}/api/uploads`, {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

### Multiple Vehicles Support
The schema supports multiple vehicles per quote. To enable:

```javascript
// Create vehicle collection function
function collectAutoVehiclesData() {
    return [
        {
            vehicleSequence: 1,
            vin: "...",
            year: 2020,
            make: "Honda",
            model: "Civic"
        }
    ];
}
```

### Edit/Update Logic
Quotes are currently insert-only. To add updates:

```sql
-- Update auto quote
UPDATE auto_quotes 
SET annual_km = ?, winter_tires = ? 
WHERE id = ? AND customer_id = ?;

-- Update property
UPDATE properties 
SET address = ?, city = ? 
WHERE id = ? AND property_quote_id = ?;
```

---

## 📝 Summary

This implementation provides:

1. **Complete Data Capture** - Every field from the dashboard form
2. **Reliable Storage** - Normalized MySQL database with proper relationships
3. **Clean Architecture** - Separated concerns (frontend, API, database)
4. **Production Quality** - Error handling, transactions, security
5. **Easy Integration** - Just include one JavaScript file

The system is ready to be integrated into a larger Meta Dashboard flow with proper API authentication and additional business logic as needed.

---

## 📞 Support

For issues or questions:
1. Check browser console for client-side errors
2. Check backend console for server-side errors
3. Verify database connectivity
4. Review CORS settings if cross-origin issues occur
5. Check .env configuration

---

**Created**: December 25, 2024  
**Version**: 1.0.0  
**Status**: Production Ready
