# Quick Start Guide - Facebook Lead Ads Integration

## 3-Minute Setup

### 1. Add Your Meta Credentials (2 minutes)

Edit `backend/.env`:

```dotenv
META_APP_ID=824389240430169
META_APP_SECRET=5ddcbd165cf003632e8aa85c84cade43
META_PAGE_ID=894819586548747
META_PAGE_ACCESS_TOKEN=EAALtxxPVHlkBQeoGRCbadQx...
META_LEAD_FORM_ID=1395244698621351
```

**Don't have these values?** See "Getting Your Credentials" below.

### 2. Start the Backend (1 minute)

**Windows:**
```bash
cd backend
start.bat
```

**Mac/Linux:**
```bash
cd backend
./start.sh
```

You should see: `INFO: Uvicorn running on http://0.0.0.0:3000`

### 3. Open Dashboard

Open in browser:
```
file:///C:\Users\sayal\Desktop\dashboard\dashboard.html
```

✅ **Done!** You should see your real Facebook leads.

---

## Getting Your Credentials

### META_APP_ID & META_APP_SECRET
1. Go to https://developers.facebook.com/apps
2. Click your app
3. Copy **App ID** and **App Secret**

### META_PAGE_ID
1. Go to your Facebook business page
2. Right-click → Inspect
3. Look in Network tab for "page_id"
4. Or use Graph API Explorer: https://developers.facebook.com/tools/explorer/

### META_PAGE_ACCESS_TOKEN
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app and page from dropdowns
3. Click **Get Token → Generate Access Token**
4. Make sure it has `leads_retrieval` permission
5. Copy the long token

### META_LEAD_FORM_ID
1. Go to https://business.facebook.com/leads
2. Click your Lead Form
3. The URL will show: `?asset_id=1395244698621351`
4. Copy the number

---

## Testing It Works

### Quick Check
```bash
python test_integration.py
```

### Manual Checks

1. **API Running?**
   - Open: http://localhost:3000/health
   - Should show: `{"status":"healthy"}`

2. **Meta Connected?**
   - Open: http://localhost:3000/api/sync/meta/status
   - Should show: `"meta_api_enabled":true`

3. **Credentials Valid?**
   - Open: http://localhost:3000/api/sync/meta/test
   - Should show: `"success":true`

4. **Sync Leads?**
   - Open: http://localhost:3000/api/sync/meta
   - Should show how many leads were synced

5. **Dashboard Working?**
   - Open dashboard.html
   - Should show your real leads

---

## Common Issues

### "Meta API is DISABLED"
→ Check all 5 fields are in `.env` (not `<I_WILL_EDIT>`)

### "API not running"
→ Make sure you ran `start.bat` or `./start.sh`

### "Dashboard shows 'Failed to fetch'"
→ Backend must be running on http://localhost:3000

### "No leads showing"
→ Open http://localhost:3000/api/sync/meta to fetch them first

### "Invalid token error"
→ Get a new token from https://developers.facebook.com/tools/explorer/

---

## Full Documentation

- **Setup Details:** See `FACEBOOK_LEAD_ADS_SETUP.md`
- **Architecture:** See `INTEGRATION_SUMMARY.md`
- **Checklist:** See `PRODUCTION_CHECKLIST.md`

---

## API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API running |
| `/api/sync/meta` | POST | Sync leads from Facebook |
| `/api/sync/meta/status` | GET | Check if Meta API enabled |
| `/api/sync/meta/test` | GET | Test credentials work |
| `/api/leads` | GET | Get all leads (paginated) |
| `/api/leads/{id}` | GET | Get single lead |
| `/api/leads/{id}/status` | PUT | Update lead status |
| `/api/process/{id}` | POST | Process a lead |

---

## That's It!

You now have a production-ready Facebook Lead Ads integration.

**Next steps:**
- ✅ Leads sync from Facebook automatically
- ✅ Dashboard shows real data
- ✅ Update lead statuses & track premiums
- ✅ Export or process as needed

**Questions?** Check the full setup guide: `FACEBOOK_LEAD_ADS_SETUP.md`

---

**Status:** ✅ Ready to use. Add your credentials and go live! 🚀
