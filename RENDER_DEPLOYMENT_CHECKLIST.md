# Render Deployment Checklist

## Pre-Deployment (Local)

✅ **Code Verification**
- [ ] Flask app runs locally: `python app.py`
- [ ] Database connection works: MySQL on localhost
- [ ] All PDFs upload and parse correctly
- [ ] G-dates calculate properly
- [ ] Multi-driver switching works

✅ **Git Repository**
- [ ] Code pushed to GitHub: `https://github.com/sayalileapforge-tech/dashparserleads`
- [ ] `.gitignore` excludes unnecessary files
- [ ] `requirements.txt` includes all dependencies
- [ ] `README.md` has clear instructions

✅ **Environment Files**
- [ ] `.env.example` created with template
- [ ] `Procfile` configured: `web: python app.py`
- [ ] `runtime.txt` specifies Python version: `python-3.13.6`
- [ ] `render.yaml` has correct build/start commands

## Render Setup

### Step 1: Create MySQL Database

- [ ] Log in to Render dashboard
- [ ] Click **New +** → **MySQL**
- [ ] Name: `insurance-leads-db`
- [ ] Copy connection details:
  - Host: `_____________________`
  - Port: `3306`
  - User: `_____________________`
  - Password: `_____________________`
  - Database: `insurance_leads`

### Step 2: Create Web Service

- [ ] Click **New +** → **Web Service**
- [ ] Select GitHub repository: `dashparserleads`
- [ ] Name: `insurance-dashboard`
- [ ] Branch: `main`
- [ ] Root Directory: `/` (leave empty)
- [ ] Environment: `Python 3`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python app.py`
- [ ] Plan: Standard or higher

### Step 3: Add Environment Variables

In Render dashboard → Web Service → Environment:

```
MYSQL_HOST=<from-database-connection>
MYSQL_PORT=3306
MYSQL_USER=<from-database-connection>
MYSQL_PASSWORD=<from-database-connection>
MYSQL_DATABASE=insurance_leads
FLASK_DEBUG=False
```

Optional (if using Meta API):
```
META_APP_ID=<your-value>
META_APP_SECRET=<your-value>
META_PAGE_ID=<your-value>
META_PAGE_ACCESS_TOKEN=<your-value>
META_LEAD_FORM_ID=<your-value>
```

## Deployment

- [ ] Click **Deploy** button
- [ ] Watch build logs for errors
- [ ] Wait for "Your service is live"
- [ ] Note the service URL: `https://insurance-dashboard-xxxxx.onrender.com`

## Post-Deployment Verification

### Database Setup

Connect to Render MySQL and run schema:
```bash
mysql -h <host> -u <user> -p <database> < quotes_schema.sql
```

Or run Python init script:
```bash
# Via Render shell:
python init_render_db.py
```

### Test Endpoints

- [ ] Dashboard loads: `https://insurance-dashboard-xxxxx.onrender.com`
- [ ] Leads API: `GET /api/leads`
- [ ] DASH parsing: `POST /api/parse-dash`
- [ ] MVR parsing: `POST /api/parse-mvr`
- [ ] G-dates calculation: `POST /api/calculate-g-dates`
- [ ] Quote saving: `POST /api/save-quote`

### Database Tests

- [ ] Can connect to MySQL
- [ ] `quotes` table exists
- [ ] `quote_drivers` table exists
- [ ] `quote_properties` table exists
- [ ] Can insert sample data

## Troubleshooting

### Build Failed

**Check:**
- Python version in `runtime.txt`
- All packages in `requirements.txt` available
- No syntax errors in Python files
- See build logs in Render dashboard

**Fix:**
```bash
# Verify locally
pip install -r requirements.txt
python -m py_compile app.py
```

### Service Won't Start

**Check:**
- Start command in service settings
- Port configuration (should be 0.0.0.0:3001)
- Environment variables are set
- No hardcoded localhost addresses

**Verify:**
```bash
# Run locally with Render env vars
export MYSQL_HOST=...
export MYSQL_PORT=3306
python app.py
```

### Database Connection Failed

**Check:**
- MySQL host/credentials correct
- Port 3306 is accessible
- Database exists: `insurance_leads`
- Firewall allows outbound connections

**Verify:**
```bash
# Test connection
mysql -h <host> -u <user> -p<pass> -D insurance_leads
```

### PDFs Not Uploading

**Check:**
- `/uploads` directory exists (created in app.py)
- Disk space available
- File permissions correct
- PDF size within limits

**Fix:**
- Check Render logs: `tail -f /var/log/app.log`

## Monitoring

### Logs

Access via Render dashboard:
- **Live Logs**: Real-time output
- **Previous Logs**: Past deployments

```bash
# Render provides live tail functionality
# View in dashboard → Logs tab
```

### Performance

Monitor in Render dashboard:
- CPU usage
- Memory usage
- Disk usage
- Network bandwidth

### Uptime

- Set up Render alerts
- Monitor via external service
- Check status page regularly

## Maintenance

### Database Backups

**Automatic:**
- Render provides backup functionality
- Configure retention in database settings

**Manual:**
```bash
mysqldump -h <host> -u <user> -p database > backup.sql
```

### Code Updates

Push to GitHub → Render auto-deploys:
```bash
git commit -m "Your message"
git push origin main
```

Render will:
1. Detect push
2. Rebuild
3. Test
4. Deploy (or rollback on failure)

### Environment Updates

**To update environment variables:**
1. Dashboard → Web Service Settings
2. Update variable
3. Service will restart

**Never hardcode secrets** - always use environment variables!

## Production URLs

**Live Application:**
```
https://insurance-dashboard-xxxxx.onrender.com
```

**API Base URL:**
```
https://insurance-dashboard-xxxxx.onrender.com/api
```

**Example API Calls:**
```bash
# Get leads
curl https://insurance-dashboard-xxxxx.onrender.com/api/leads

# Upload DASH PDF
curl -X POST -F "pdf=@file.pdf" \
  https://insurance-dashboard-xxxxx.onrender.com/api/parse-dash

# Calculate G-dates
curl -X POST -H "Content-Type: application/json" \
  -d '{"driver":{...}, "mvr_data":{...}}' \
  https://insurance-dashboard-xxxxx.onrender.com/api/calculate-g-dates
```

## Rollback Plan

If deployment fails:

1. **Previous Render deployment**
   - Dashboard → Manual Deploy → Previous version
   - Or wait for auto-rollback

2. **Git rollback**
   ```bash
   git revert HEAD
   git push origin main
   ```

3. **Database restore**
   - Render dashboard → Database → Restore backup
   - Or use mysqldump backup

## Cost Optimization

- Use free tier for testing
- Standard tier for production ($7/month)
- MySQL starter tier ($15/month)
- Scale up as needed

## Support Resources

- Render Docs: https://render.com/docs
- MySQL Docs: https://dev.mysql.com/doc/
- Flask Docs: https://flask.palletsprojects.com/
- GitHub Issues: Create issue in repo

---

**Deployment Status:** ✅ Ready for production

**Last Updated:** 2026-01-03
**Environment:** Production (Render)
**Python Version:** 3.13.6
**Framework:** Flask
**Database:** MySQL
