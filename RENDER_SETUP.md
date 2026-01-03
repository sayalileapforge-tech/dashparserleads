# Render Deployment Setup Guide

## Step 1: Create Render Account
1. Go to https://render.com
2. Sign up or login
3. Connect GitHub account

## Step 2: Create MySQL Database (Optional)

If using Render's database:

1. In Render dashboard, click **New +** → **MySQL**
2. Name: `insurance-dashboard-db`
3. Select a plan (start with free tier if available)
4. Note the connection details:
   - **Host**: Will be provided in credentials
   - **User**: Provided in credentials  
   - **Password**: Provided in credentials
   - **Port**: Usually 3306

## Step 3: Create Web Service

### From Render Dashboard:
1. Click **New +** → **Web Service**
2. Select your GitHub repository: `dashparserleads`
3. Configure:

#### Build Settings:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Docker**: None

#### Environment Variables:
Add each variable in Render's environment variables editor:

```
MYSQL_HOST=<mysql-host-from-step2>
MYSQL_PORT=3306
MYSQL_USER=<mysql-user-from-step2>
MYSQL_PASSWORD=<mysql-password-from-step2>
MYSQL_DATABASE=insurance_leads
FLASK_DEBUG=False
```

### Optional Meta Integration:
If using Meta Lead Forms, also add:
```
META_APP_ID=<your-meta-app-id>
META_APP_SECRET=<your-meta-app-secret>
META_PAGE_ID=<your-meta-page-id>
META_PAGE_ACCESS_TOKEN=<your-meta-page-token>
META_LEAD_FORM_ID=<your-form-id>
```

## Step 4: Configure Render YAML (Alternative)

Create `render.yaml` in repo (already included):

```yaml
services:
  - type: web
    name: insurance-dashboard
    env: python
    plan: standard
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: MYSQL_HOST
        value: <mysql-host>
      - key: MYSQL_USER
        value: <mysql-user>
      - key: MYSQL_PASSWORD
        value: <mysql-password>
      - key: MYSQL_DATABASE
        value: insurance_leads
      - key: FLASK_DEBUG
        value: 'False'
```

## Step 5: Setup Database Tables

Once deployed:

1. Get your Render MySQL connection details
2. Connect using MySQL client:
   ```bash
   mysql -h <host> -u <user> -p <database>
   ```
3. Run the schema:
   ```sql
   source quotes_schema.sql;
   ```

Or use the init script:
```bash
python create_tables.py
```

## Step 6: Monitor Deployment

1. Render builds automatically from git commits
2. Watch build logs in Render dashboard
3. Check "Events" tab for deployment status
4. Your app URL: `https://insurance-dashboard-xxxx.onrender.com`

## Step 7: Post-Deployment Checklist

✅ Verify endpoints are working:
- `GET /` - Dashboard loads
- `POST /api/parse-dash` - PDF parsing works
- `POST /api/parse-mvr` - MVR parsing works
- `GET /api/leads` - Database connection works

## Troubleshooting

### Database Connection Failed
- Check MySQL host/credentials in environment variables
- Ensure MySQL port (3306) is open
- Verify database name is correct

### Port Issues
- Render automatically assigns a PORT
- App should listen on `0.0.0.0:0.0.0.0` 
- Never hardcode port 3001 in production

### Build Failures
- Check Python version: `python-3.13.6`
- Verify `requirements.txt` has all dependencies
- Check build logs for missing packages

### PDF Upload Issues
- Ensure `/uploads` directory exists and is writable
- Check file permissions on server
- Verify PDF size isn't exceeding limits

## Environment Variables Reference

| Variable | Local | Render | Required |
|----------|-------|--------|----------|
| MYSQL_HOST | localhost | host.onrender.com | Yes |
| MYSQL_PORT | 3306 | 3306 | Yes |
| MYSQL_USER | root | admin | Yes |
| MYSQL_PASSWORD | root@123 | strong_password | Yes |
| MYSQL_DATABASE | insurance_leads | insurance_leads | Yes |
| FLASK_PORT | 3001 | auto | No |
| FLASK_DEBUG | False | False | No |

## Production URLs

After deployment, your application will be available at:
```
https://insurance-dashboard-xxxxx.onrender.com
```

All API endpoints will be:
```
https://insurance-dashboard-xxxxx.onrender.com/api/...
```

## Database Backup

To backup your Render MySQL database:

1. Use Render's backup feature in dashboard
2. Or use mysqldump:
   ```bash
   mysqldump -h <host> -u <user> -p database > backup.sql
   ```

## Auto-Deploy from GitHub

Render automatically deploys when you push to `main` branch:

```bash
git commit -m "Update app"
git push origin main
```

Render will:
1. Detect the push
2. Pull the latest code
3. Run build command
4. Start the service
5. Show status in dashboard

---

**Need help?** Check Render documentation: https://render.com/docs
