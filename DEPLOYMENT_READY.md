# 🚀 Render Deployment - Complete Setup Summary

## ✅ Project Status: READY FOR DEPLOYMENT

Your entire project is now deployed on GitHub and configured for Render production deployment.

---

## 📁 Root Directory Configuration

### What's in the Root Directory:

**Core Application Files:**
- `app.py` - Flask backend with all endpoints
- `dash_parser.py` - DASH PDF extraction
- `mvr_parser_strict.py` - MVR PDF extraction  
- `license_history_integration.py` - G/G1/G2 calculation
- `g1g2_calculator.py` - License date calculator
- `meta_leads_fetcher.py` - Meta API integration
- `save_quote_endpoint.py` - Database saving
- `Untitled-2.html` - Frontend UI (single file)

**Deployment Configuration:**
- `requirements.txt` - Python dependencies
- `Procfile` - Render start command: `python app.py`
- `runtime.txt` - Python version: `python-3.13.6`
- `render.yaml` - Infrastructure as code
- `build.sh` - Build script
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules

**Documentation:**
- `README.md` - Project overview
- `RENDER_SETUP.md` - Step-by-step Render setup
- `RENDER_DEPLOYMENT.md` - Deployment instructions
- `RENDER_DEPLOYMENT_CHECKLIST.md` - Pre/post deployment checklist
- `ROOT_DIRECTORY_SETUP.md` - Root directory configuration
- `quotes_schema.sql` - Database schema
- `init_render_db.py` - Database initialization script

---

## 🔐 Environment Variables

### Local Development
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root@123
MYSQL_DATABASE=insurance_leads
FLASK_PORT=3001
FLASK_DEBUG=True
```

### Render Production
```bash
MYSQL_HOST=<render-mysql-host.onrender.com>
MYSQL_PORT=3306
MYSQL_USER=<render-db-user>
MYSQL_PASSWORD=<secure-password>
MYSQL_DATABASE=insurance_leads
FLASK_DEBUG=False
```

**Key Point:** App reads from environment variables automatically!

```python
# Example from app.py
host = os.getenv('MYSQL_HOST', 'localhost')
user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', 'root@123')
```

---

## 📝 Deployment Steps

### 1️⃣ Create Render Account
- Visit https://render.com
- Sign up / Login
- Connect GitHub

### 2️⃣ Create MySQL Database
1. **Dashboard** → **New +** → **MySQL**
2. **Name:** `insurance-leads-db`
3. **Copy connection details:**
   - Host: `_____________________`
   - User: `_____________________`
   - Password: `_____________________`

### 3️⃣ Create Web Service
1. **Dashboard** → **New +** → **Web Service**
2. **Repository:** Select `dashparserleads`
3. **Name:** `insurance-dashboard`
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `python app.py`

### 4️⃣ Add Environment Variables
In Render Web Service → **Environment:**

```
MYSQL_HOST=<from-step-2>
MYSQL_PORT=3306
MYSQL_USER=<from-step-2>
MYSQL_PASSWORD=<from-step-2>
MYSQL_DATABASE=insurance_leads
FLASK_DEBUG=False
```

### 5️⃣ Deploy
- Click **Deploy**
- Watch build logs
- Wait for "Your service is live"

### 6️⃣ Initialize Database
```bash
# Via Render shell
python init_render_db.py
```

---

## 🎯 What Gets Deployed

**Source:** GitHub → `sayalileapforge-tech/dashparserleads`

**To:** Render → `insurance-dashboard-xxxxx.onrender.com`

**Includes:**
- ✅ Flask backend
- ✅ PDF parsing (DASH & MVR)
- ✅ Multi-driver support
- ✅ G/G1/G2 calculation
- ✅ MySQL database integration
- ✅ HTML frontend
- ✅ REST API endpoints
- ✅ Auto-fill functionality

**Excludes (by .gitignore):**
- ❌ PDFs
- ❌ Test files
- ❌ Upload folder
- ❌ Logs
- ❌ Python cache
- ❌ Environment variables

---

## 🔌 API Endpoints (After Deployment)

All endpoints served from production URL:

```
https://insurance-dashboard-xxxxx.onrender.com
```

**Example API Calls:**

```bash
# Get all leads
curl https://insurance-dashboard-xxxxx.onrender.com/api/leads

# Upload and parse DASH PDF
curl -X POST -F "pdf=@dashboard.pdf" \
  https://insurance-dashboard-xxxxx.onrender.com/api/parse-dash

# Parse MVR PDF
curl -X POST -F "pdf=@mvr.pdf" \
  https://insurance-dashboard-xxxxx.onrender.com/api/parse-mvr

# Calculate G-dates
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "driver": {...},
    "mvr_data": {...}
  }' \
  https://insurance-dashboard-xxxxx.onrender.com/api/calculate-g-dates

# Save quote to database
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "lead_name": "...",
    "email": "...",
    "drivers": [...],
    "properties": [...]
  }' \
  https://insurance-dashboard-xxxxx.onrender.com/api/save-quote
```

---

## 🗄️ Database Tables

**Three normalized tables created automatically:**

1. **quotes**
   - lead_name, lead_email, lead_phone
   - meta_id, meta_source, potential_status
   - premium, renewal_date, signal, status

2. **quote_drivers** (per-driver data)
   - DASH extraction: name, DLN, DOB, address, phone, email
   - MVR extraction: birth_date, licence_expiry, convictions
   - Calculated: g_date, g1_date, g2_date

3. **quote_properties** (property/vehicle data)
   - address, type, year_built, storeys
   - electrical, plumbing, roofing, heating
   - alarm systems, locks, sprinklers

---

## ✨ Auto-Deploy from GitHub

Every push to `main` automatically deploys:

```bash
git commit -m "Update feature"
git push origin main
```

Render will:
1. Detect push
2. Pull latest code
3. Run build: `pip install -r requirements.txt`
4. Run start: `python app.py`
5. Deploy live in ~2-3 minutes

---

## 🐛 Troubleshooting Quick Reference

| Issue | Cause | Solution |
|-------|-------|----------|
| Build Failed | Missing package | Check `requirements.txt` |
| Won't Start | Wrong port | Check `Procfile` |
| DB Connection Error | Wrong credentials | Verify env vars in Render |
| PDFs not uploading | No uploads dir | App auto-creates it |
| API returns 404 | Path incorrect | Check endpoint URLs |

---

## 📊 Monitoring

**Render Dashboard provides:**
- ✅ Real-time logs
- ✅ CPU/Memory usage
- ✅ Deployment history
- ✅ Error alerts
- ✅ Uptime monitoring

---

## 🔄 Updates & Maintenance

### Push Code Update
```bash
git commit -m "Fix bug"
git push origin main
```
→ Render auto-deploys in 2-3 minutes

### Update Environment Variables
1. Render Dashboard → Web Service
2. Update variable
3. Service auto-restarts

### Database Updates
Connect to MySQL and run queries:
```bash
mysql -h <host> -u <user> -p<password> insurance_leads
```

---

## 📦 What's Next?

1. ✅ Go to https://render.com
2. ✅ Follow the 6 deployment steps above
3. ✅ Wait for live notification
4. ✅ Test API endpoints
5. ✅ Monitor in dashboard

---

## 📞 Support Files

- **RENDER_SETUP.md** - Detailed setup instructions
- **RENDER_DEPLOYMENT.md** - Complete deployment guide
- **RENDER_DEPLOYMENT_CHECKLIST.md** - Checklist for deployment
- **ROOT_DIRECTORY_SETUP.md** - Root directory reference
- **README.md** - Project overview

---

## 🎉 Deployment Ready!

**Your project is 100% ready for production deployment on Render.**

- ✅ Code on GitHub
- ✅ Procfile configured
- ✅ Requirements.txt complete
- ✅ Environment variables defined
- ✅ Database schema included
- ✅ Init script provided
- ✅ Documentation complete

**Next Step:** Go to https://render.com and deploy! 🚀

---

**Project:** Insurance Dashboard with DASH/MVR PDF Parsing
**Repository:** https://github.com/sayalileapforge-tech/dashparserleads
**Status:** ✅ Ready for Production
**Target Platform:** Render.com
**Python Version:** 3.13.6
**Database:** MySQL
**Framework:** Flask
