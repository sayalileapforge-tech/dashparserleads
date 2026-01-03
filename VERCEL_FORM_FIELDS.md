# VERCEL DEPLOYMENT - ALL FIELD VALUES

## Copy-Paste These Values Into Vercel Form

---

## STEP 1: Import Repository

| Field | Value |
|-------|-------|
| **Git Repository URL** | https://github.com/sayalileapforge-tech/dashparserleads |

---

## STEP 2: Project Settings

| Field | Value |
|-------|-------|
| **Project Name** | insurance-dashboard-frontend |
| **Framework Preset** | Other |
| **Root Directory** | ./ |
| **Build Command** | (Leave Empty) |
| **Output Directory** | (Leave Empty) |
| **Install Command** | (Leave Empty) |
| **Development Command** | (Leave Empty) |

---

## STEP 3: Environment Variables

Add EXACTLY these 2 variables:

### Variable 1:
```
Name: REACT_APP_API_URL
Value: https://dashparserleads.onrender.com
```

### Variable 2:
```
Name: REACT_APP_WEBHOOK_URL
Value: https://dashparserleads.onrender.com/api/meta-webhook
```

---

## STEP 4: Deploy Settings

| Setting | Value |
|---------|-------|
| **Production Branch** | main |
| **Deploy on Push** | Yes (Enabled) |
| **Preview Deployments** | Yes (Enabled) |

---

## STEP 5: Click "Deploy"

Wait 1-2 minutes ✅

---

## YOU'LL GET:

```
✅ Frontend URL: https://insurance-dashboard-frontend-[random].vercel.app
✅ Backend URL: https://dashparserleads.onrender.com
✅ API Ready: All endpoints working
```

---

## COMPLETE SUMMARY TABLE

| Category | Field | Value |
|----------|-------|-------|
| **GitHub** | Repository URL | https://github.com/sayalileapforge-tech/dashparserleads |
| **Project** | Name | insurance-dashboard-frontend |
| **Project** | Framework | Other |
| **Project** | Root Directory | ./ |
| **Build** | Build Command | (empty) |
| **Build** | Output Directory | (empty) |
| **Environment** | REACT_APP_API_URL | https://dashparserleads.onrender.com |
| **Environment** | REACT_APP_WEBHOOK_URL | https://dashparserleads.onrender.com/api/meta-webhook |
| **Deploy** | Production Branch | main |
| **Deploy** | Deploy on Push | Yes |

---

## VERCEL FORM FIELDS IN ORDER

```
1. Git Repository URL
   → https://github.com/sayalileapforge-tech/dashparserleads

2. Project Name
   → insurance-dashboard-frontend

3. Framework Preset
   → Other

4. Root Directory
   → ./

5. Build Command
   → (Leave blank)

6. Output Directory
   → (Leave blank)

7. Environment Variables
   → REACT_APP_API_URL = https://dashparserleads.onrender.com
   → REACT_APP_WEBHOOK_URL = https://dashparserleads.onrender.com/api/meta-webhook

8. Production Branch
   → main

9. Click "Deploy"
   → Wait 1-2 minutes
```

---

## WHAT THESE MEAN

| Field | Why |
|-------|-----|
| **Project Name** | Name shown in Vercel dashboard |
| **Framework** | Other = Plain HTML (no React/Next.js) |
| **Root Directory** | Where to find files (./ = root) |
| **Build/Output** | Empty because HTML doesn't need building |
| **API_URL** | Frontend needs to know where backend is |
| **WEBHOOK_URL** | For Facebook lead webhooks |
| **Deploy on Push** | Auto-deploy when you push to GitHub |

---

## READY TO GO?

1. Open https://vercel.com
2. Sign in with GitHub
3. Click "New Project"
4. Follow form above
5. Deploy ✅

You'll be live in 2 minutes!
