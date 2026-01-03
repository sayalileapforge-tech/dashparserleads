# Project Root Directory Structure & Environment Setup

## Directory Structure

```
dashboard ui/
├── app.py                          # Flask backend (main app)
├── dash_parser.py                  # DASH PDF parser
├── mvr_parser_strict.py            # MVR PDF parser
├── license_history_integration.py  # G/G1/G2 calculation
├── g1g2_calculator.py              # License date calculator
├── meta_leads_fetcher.py           # Meta API integration
├── save_quote_endpoint.py          # Database save endpoint
├── Untitled-2.html                 # Frontend (single file)
├── quotes_schema.sql               # Database schema
├── requirements.txt                # Python dependencies
├── Procfile                        # Render start command
├── runtime.txt                     # Python version
├── render.yaml                     # Infrastructure as code
├── build.sh                        # Build script
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── RENDER_SETUP.md                 # Render setup guide
├── RENDER_DEPLOYMENT.md            # Deployment instructions
├── RENDER_DEPLOYMENT_CHECKLIST.md  # Pre/post deployment checks
├── init_render_db.py               # Database initialization
└── uploads/                        # PDF uploads folder
    └── (auto-created on first upload)
```

## Environment Variables by Context

### LOCAL DEVELOPMENT
```bash
# .env or terminal environment
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root@123
MYSQL_DATABASE=insurance_leads
FLASK_PORT=3001
FLASK_DEBUG=True
```

**Run:**
```bash
python app.py
# Listens on: http://localhost:3001
```

### RENDER PRODUCTION
```bash
# Set in Render dashboard → Environment Variables
MYSQL_HOST=your-db-host.onrender.com
MYSQL_PORT=3306
MYSQL_USER=render_db_user
MYSQL_PASSWORD=<secure-password>
MYSQL_DATABASE=insurance_leads
FLASK_DEBUG=False
# FLASK_PORT - Render auto-assigns via PORT env var
```

**Auto-deployed by Render:**
```bash
# Procfile specifies: python app.py
# Listens on: 0.0.0.0 (any interface)
# Render maps to: https://insurance-dashboard-xxxxx.onrender.com
```

## Root Directory Configuration

### 1. Python Entry Point
**File:** `app.py`

```python
# Imports from root directory
from dash_parser import parse_dash_report
from license_history_integration import DriverLicenseHistory
from meta_leads_fetcher import get_fetcher
from save_quote_endpoint import save_quote

# Upload folder
UPLOAD_FOLDER = 'uploads'  # Creates relative to root
```

**Key settings:**
- Host: `0.0.0.0` (listens on all interfaces)
- Port: From `FLASK_PORT` env var or default 3001
- Debug: From `FLASK_DEBUG` env var or False

### 2. Database Configuration

**File:** `quotes_schema.sql`

```sql
-- Creates 3 tables:
-- 1. quotes (main quote record)
-- 2. quote_drivers (per-driver DASH/MVR data)
-- 3. quote_properties (property/vehicle data)
```

**Load schema:**
```bash
# Local MySQL
mysql -u root -p insurance_leads < quotes_schema.sql

# Render MySQL (via dashboard or script)
python init_render_db.py
```

### 3. Dependencies
**File:** `requirements.txt`

```
Flask==2.3.3
Flask-CORS==4.0.0
mysql-connector-python==8.1.0
PyPDF2==3.0.1
python-dateutil==2.8.2
requests==2.31.0
pydantic==2.0.0
Werkzeug==3.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

### 4. File Upload Directory
**Path:** `uploads/`

- Auto-created in root directory
- Stores uploaded PDFs
- Preserves UUID filenames
- .gitignore excludes from repo

### 5. Startup Commands

**Render Procfile:**
```
web: python app.py
```

**Render render.yaml:**
```yaml
buildCommand: pip install -r requirements.txt
startCommand: python app.py
```

## API Endpoints (Root Level)

All endpoints served from root:

```
GET  /                           # Dashboard page
GET  /api/leads                  # List all leads
POST /api/parse-dash             # Parse DASH PDF
POST /api/parse-mvr              # Parse MVR PDF
POST /api/calculate-g-dates      # Calculate G/G1/G2 dates
POST /api/save-quote             # Save quote to database
GET  /uploads/<filename>         # Download uploaded file
```

## Static Files

**Frontend:** `Untitled-2.html`
- Served as root index
- All JS embedded
- CSS embedded
- No external dependencies
- Ready for production

## Environment Variable Priority

App checks in this order:

1. **Environment variable** (Render injects these)
2. **os.getenv() default** (fallback value)

```python
# Example from app.py
host = os.getenv('MYSQL_HOST', 'localhost')  # Uses 'localhost' if not set
port = int(os.getenv('MYSQL_PORT', 3306))    # Uses 3306 if not set
debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
```

## Render-Specific Configuration

### Port Handling
- **Render sets:** `PORT` environment variable
- **App uses:** `FLASK_PORT` env var or defaults to 3001
- **Binding:** `host='0.0.0.0'` accepts any interface

### Database Connection
- **Local:** `localhost:3306` (direct)
- **Render:** `hostname.onrender.com:3306` (internet)
- Both use standard MySQL protocol

### File Uploads
- **Local:** Stored in `./uploads/`
- **Render:** Stored in `/home/application/uploads/`
- App handles both transparently

## Deployment Process

```mermaid
Local Development
    ↓
git push origin main
    ↓
GitHub Repository
    ↓
Render Webhook (auto-trigger)
    ↓
Render Build
  - Pulls code
  - Runs build command: pip install -r requirements.txt
    ↓
Render Start
  - Runs start command: python app.py
  - Injects environment variables
  - Binds to 0.0.0.0:PORT
    ↓
Production App Live
  - https://insurance-dashboard-xxxxx.onrender.com
```

## Quick Setup Checklist

### Before Pushing to GitHub
- [ ] `app.py` uses `os.getenv()` for all config
- [ ] `requirements.txt` has all packages
- [ ] `.env.example` has template
- [ ] `Procfile` has start command
- [ ] `runtime.txt` has Python version
- [ ] `quotes_schema.sql` is in root

### For Render Deployment
- [ ] Render MySQL database created
- [ ] Render web service created
- [ ] Environment variables set in Render:
  - [ ] MYSQL_HOST
  - [ ] MYSQL_USER
  - [ ] MYSQL_PASSWORD
  - [ ] MYSQL_DATABASE
- [ ] GitHub repo connected
- [ ] Build/start commands configured

### Post-Deployment
- [ ] App is live on Render URL
- [ ] Database tables created
- [ ] API endpoints respond
- [ ] PDF uploads work
- [ ] Database saves work

## Troubleshooting Root Issues

### App won't start
```bash
# Check Python syntax
python -m py_compile app.py

# Check dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

### Database not found
```bash
# Check env vars
echo $MYSQL_HOST
echo $MYSQL_USER

# Test connection
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD
```

### Uploads folder missing
```bash
# App auto-creates, but check:
mkdir -p uploads
chmod 755 uploads
```

### Import errors
```bash
# All modules in root directory:
ls -la *.py
```

---

**Status:** Production Ready ✅
**Location:** Root directory `/`
**Git Repo:** https://github.com/sayalileapforge-tech/dashparserleads
**Render URL:** TBD (after deployment)
