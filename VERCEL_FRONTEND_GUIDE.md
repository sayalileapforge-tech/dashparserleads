# VERCEL FRONTEND DEPLOYMENT

## What to Deploy to Vercel

These HTML files should be deployed:

```
index.html                  ← Dashboard homepage (already configured)
Untitled-2.html             ← PDF Parser UI (needs API URL update)
test_search.html            ← Search interface (needs API URL update)
function_test.html          ← Function testing (needs API URL update)
```

---

## API URLs for Vercel

### Your Render Backend URL:
```
https://dashparserleads.onrender.com
```

### All API Endpoints Available:
```
✓ https://dashparserleads.onrender.com/api/health
✓ https://dashparserleads.onrender.com/api/parse-dash
✓ https://dashparserleads.onrender.com/api/parse-mvr
✓ https://dashparserleads.onrender.com/api/calculate-g-dates
✓ https://dashparserleads.onrender.com/api/meta-webhook
✓ https://dashparserleads.onrender.com/api/incoming-leads
```

---

## Quick Fix for HTML Files

In ANY HTML file that has:
```javascript
fetch('/api/parse-dash'  // ❌ Wrong (won't work)
```

Change to:
```javascript
fetch('https://dashparserleads.onrender.com/api/parse-dash'  // ✅ Correct
```

---

## Vercel Deployment Flow

```
1. Create account: vercel.com
   ↓
2. Connect GitHub repo
   ↓
3. Select project settings
   ↓
4. Click Deploy
   ↓
5. Get live URL (2 minutes)
   ↓
6. Update HTML API calls
   ↓
7. Push to GitHub
   ↓
8. Vercel auto-redeploys
   ↓
9. Live! ✅
```

---

## Your Final URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://insurance-dashboard-frontend-xxxx.vercel.app |
| **Backend** | https://dashparserleads.onrender.com |
| **API** | https://dashparserleads.onrender.com/api/... |

---

## I Can Help With

- ✅ Updating all HTML files with correct API URLs
- ✅ Creating a Vercel config file (vercel.json)
- ✅ Setting up auto-deployment
- ✅ Fixing CORS issues if they occur
- ✅ Testing frontend ↔ backend connection

**Just say:** "Update HTML files for Vercel" and I'll do it!
