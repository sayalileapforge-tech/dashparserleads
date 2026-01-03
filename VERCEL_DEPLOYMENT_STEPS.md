# VERCEL DEPLOYMENT - STEP BY STEP

## Step 1: Create Vercel Account
```
Go to: https://vercel.com
Click: "Sign Up"
Choose: "Continue with GitHub"
Authorize Vercel to access your GitHub
```

---

## Step 2: Import Your GitHub Repository

```
1. After login, click "Add New..." → "Project"
2. Click "Import Git Repository"
3. Paste: https://github.com/sayalileapforge-tech/dashparserleads
4. Click "Continue"
```

---

## Step 3: Configure Project Settings

| Setting | Value |
|---------|-------|
| **Project Name** | insurance-dashboard-frontend |
| **Framework Preset** | Other |
| **Root Directory** | ./ (or leave empty) |
| **Build Command** | Leave empty (no build needed for HTML) |
| **Output Directory** | Leave empty |

---

## Step 4: Add Environment Variables (IMPORTANT!)

Click "Environment Variables" and add:

```
Name: REACT_APP_API_URL
Value: https://dashparserleads.onrender.com
```

(This connects your frontend to your Render backend)

---

## Step 5: Deploy

```
Click "Deploy" button
Wait 1-2 minutes ⏳
You'll get a live URL like: https://insurance-dashboard-frontend-xxxx.vercel.app
```

---

## Step 6: Update HTML Files to Use Render API

Once deployed, go back to your GitHub repo and update the HTML files:

**In `Untitled-2.html` (PDF Parser):**
Find lines with `fetch('http://localhost...` or `fetch('/api/parse-dash`

Replace with:
```javascript
fetch('https://dashparserleads.onrender.com/api/parse-dash', {
    method: 'POST',
    body: formData
})
```

**Same for other HTML files:**
- Replace all local API calls
- Use: `https://dashparserleads.onrender.com/api/...`

---

## Step 7: Push Updated Files

```bash
git add .
git commit -m "Update API URLs to Render backend"
git push origin main
```

Vercel will **auto-redeploy** when you push to GitHub ✅

---

## Step 8: Your Live URLs

**Frontend:** https://insurance-dashboard-frontend-xxxx.vercel.app
**Backend API:** https://dashparserleads.onrender.com
**Webhook:** https://dashparserleads.onrender.com/api/meta-webhook

---

## QUICK CHECKLIST

- [ ] Create Vercel account
- [ ] Connect GitHub repo
- [ ] Configure project settings
- [ ] Add environment variables
- [ ] Deploy to Vercel
- [ ] Update HTML files with API URLs
- [ ] Push changes to GitHub
- [ ] Vercel auto-redeploys
- [ ] Test frontend → backend connection
- [ ] Share frontend URL with client

---

## TEST YOUR DEPLOYMENT

1. Open your Vercel URL
2. Upload a PDF file
3. Should send to Render backend
4. Get response back
5. Display results ✅

---

## IF SOMETHING BREAKS

**Common Issues:**

**1. CORS Error (Cannot reach Render)**
- Solution: Check Render API URL is correct
- In app.py add:
  ```python
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  ```

**2. Files not found**
- Solution: Make sure all HTML, CSS, JS files are in GitHub repo
- Vercel needs to see them to deploy

**3. API calls returning 404**
- Solution: Update all API URLs to use Render domain
- Not localhost!

---

## NEXT STEPS

After Vercel deployment:
1. Share frontend URL with client
2. Client tests on browser
3. Upload PDF → parses
4. G-dates calculate
5. Multi-driver switching works
6. Facebook leads appear automatically
7. Demo successful! 🎉

---

**Need help?** Let me know if:
- You get stuck on any step
- You need help updating HTML files
- You get CORS errors
- API isn't responding
