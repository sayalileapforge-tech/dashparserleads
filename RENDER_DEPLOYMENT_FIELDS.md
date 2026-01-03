# RENDER DEPLOYMENT - COMPLETE FIELDS

## ALL FIELDS FOR RENDER FORM

### STEP 1: SELECT REPOSITORY
```
Repository: sayalileapforge-tech/dashparserleads
Branch: main
```

---

### STEP 2: SERVICE NAME & SETTINGS

| Field | Value |
|-------|-------|
| **Service Name** | insurance-dashboard |
| **Region** | Oregon (US West) |
| **Plan** | Free |

---

### STEP 3: ENVIRONMENT SETTINGS

| Field | Value |
|-------|-------|
| **Environment** | Python 3 |
| **Runtime** | Python 3.13.6 |
| **Root Directory** | (Leave EMPTY) |

---

### STEP 4: BUILD & START COMMANDS

| Field | Value |
|-------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |

---

## STEP 5: ENVIRONMENT VARIABLES

Copy-paste each one into Render's "Add Environment Variable" form:

### Variable 1:
```
Key: FLASK_PORT
Value: 3001
```

### Variable 2:
```
Key: FLASK_DEBUG
Value: False
```

### Variable 3:
```
Key: META_APP_ID
Value: your-meta-app-id
```

### Variable 4:
```
Key: META_APP_SECRET
Value: your-meta-app-secret
```

### Variable 5:
```
Key: META_PAGE_ID
Value: your-meta-page-id
```

### Variable 6:
```
Key: META_PAGE_ACCESS_TOKEN
Value: your-meta-page-token
```

### Variable 7:
```
Key: META_LEAD_FORM_ID
Value: your-form-id
```

### Variable 8:
```
Key: META_WEBHOOK_VERIFY_TOKEN
Value: insurance_dashboard_webhook
```

---

## SUMMARY TABLE - COPY THIS

| Setting | Value |
|---------|-------|
| Repository | sayalileapforge-tech/dashparserleads |
| Branch | main |
| Service Name | insurance-dashboard |
| Environment | Python 3 |
| Root Directory | (empty) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python app.py` |
| Region | Oregon |
| Plan | Free |

---

## ENVIRONMENT VARIABLES TABLE

| Key | Value |
|-----|-------|
| FLASK_PORT | 3001 |
| FLASK_DEBUG | False |
| META_APP_ID | your-meta-app-id |
| META_APP_SECRET | your-meta-app-secret |
| META_PAGE_ID | your-meta-page-id |
| META_PAGE_ACCESS_TOKEN | your-meta-page-token |
| META_LEAD_FORM_ID | your-form-id |
| META_WEBHOOK_VERIFY_TOKEN | insurance_dashboard_webhook |

---

## DEPLOYMENT WORKFLOW

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Authorize GitHub & select repo
4. Fill all fields above
5. Add all 8 environment variables
6. Click "Deploy"
7. Wait 2-3 minutes ⏳
8. Get live URL: https://insurance-dashboard-xxxxx.onrender.com

---

## YOUR WEBHOOK URL (After Deployment)

```
https://insurance-dashboard-xxxxx.onrender.com/api/meta-webhook
```

Use this in Meta Business Suite webhook setup.

---

## VERIFY WEBHOOK TOKEN (Copy This)

```
insurance_dashboard_webhook
```

Paste this as Verify Token in Meta webhook settings.

---

**Ready to deploy? Start here:** https://dashboard.render.com
