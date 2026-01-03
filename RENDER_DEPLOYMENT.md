# Render Deployment Guide

## Prerequisites
- GitHub account (with repo pushed)
- Render account (render.com)
- MySQL database (or use Render's MySQL add-on)

## Step 1: Prepare for Deployment
✓ `requirements.txt` - All Python dependencies listed
✓ `Procfile` - How to start the app
✓ `runtime.txt` - Python version specified
✓ `build.sh` - Build instructions
✓ `.env.example` - Environment variables template

## Step 2: Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

## Step 3: Create Render Service

### Option A: Using Web UI (Recommended)
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: insurance-dashboard
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free or Starter

### Option B: Using render.yaml (Infrastructure as Code)
Already included in the repo!

## Step 4: Set Environment Variables
In Render dashboard → Environment:

```
FLASK_PORT=3001
FLASK_DEBUG=False
MYSQL_HOST=your-db-host.mysql.database.azure.com (or Render MySQL host)
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=insurance_leads
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_PAGE_ID=your_meta_page_id
META_PAGE_ACCESS_TOKEN=your_meta_token
META_LEAD_FORM_ID=your_form_id
```

## Step 5: Deploy Database
Either:
1. **Use Render's MySQL add-on** (easier)
2. **Use external MySQL** (Azure, AWS RDS, etc.)

### Initialize Database on Render
After deployment, SSH into the service or create a one-off job:
```bash
python create_tables.py
```

## Step 6: Monitor Deployment
- Check Render Logs for errors
- Test endpoints: `https://your-service.onrender.com/api/leads`
- Upload test PDFs and verify parsing works

## Troubleshooting

### Database Connection Fails
- Verify MySQL credentials in environment
- Check firewall/IP whitelist on database
- Ensure database service is running

### Static Files Not Found
- Verify all files are committed to git
- Check .gitignore doesn't exclude important files

### Slow First Request
- Normal - Render spins down free services
- Upgrade to paid plan for persistence

## Cost Estimation
- **Web Service**: Free (auto-sleep) or $7+/month
- **MySQL Database**: Free (limited) or $15+/month
- **Total**: $20+/month for production

## Production Checklist
- [ ] All environment variables set
- [ ] Database initialized with schema
- [ ] Meta API credentials valid
- [ ] HTTPS enabled (automatic on Render)
- [ ] Backup strategy for MySQL
- [ ] Error logging configured
- [ ] Rate limiting enabled

## Scaling Tips
- Switch from SQLite to MySQL ✓ (already done)
- Use CDN for static files
- Enable caching headers
- Monitor performance
- Set up alerts for errors
