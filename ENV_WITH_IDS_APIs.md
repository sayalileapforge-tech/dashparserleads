# ENVIRONMENT VARIABLES - EXACT FORMAT FOR RENDER

## Copy and paste these into Render's Environment Variables section

```
FLASK_PORT=3001
FLASK_DEBUG=False
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_PAGE_ID=your_page_id
META_PAGE_ACCESS_TOKEN=your_access_token
META_LEAD_FORM_ID=your_form_id
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
```

---

## EACH VARIABLE SEPARATELY

### Variable 1:
```
FLASK_PORT=3001
```

### Variable 2:
```
FLASK_DEBUG=False
```

### Variable 3:
```
META_APP_ID=your_app_id
```

### Variable 4:
```
META_APP_SECRET=your_app_secret
```

### Variable 5:
```
META_PAGE_ID=your_page_id
```

### Variable 6:
```
META_PAGE_ACCESS_TOKEN=your_access_token
```

### Variable 7:
```
META_LEAD_FORM_ID=your_form_id
```

### Variable 8:
```
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
```

---

## WHERE TO GET YOUR IDs AND APIs

| Variable | Where to Get |
|----------|-------------|
| **META_APP_ID** | Meta App Dashboard → Settings → Basic |
| **META_APP_SECRET** | Meta App Dashboard → Settings → Basic |
| **META_PAGE_ID** | Meta Business Suite → Pages → Page ID |
| **META_PAGE_ACCESS_TOKEN** | Meta Business Suite → Integrations → Page Access Token |
| **META_LEAD_FORM_ID** | Meta Business Suite → Lead Form → Form ID |
| **META_WEBHOOK_VERIFY_TOKEN** | Any random string (we use: `insurance_dashboard_webhook`) |

---

## HOW TO USE IN RENDER

1. On Render Web Service form
2. Scroll to "Environment"
3. Click "Add Environment Variable" for each one above
4. Paste Key=Value
5. Click "Deploy"

---

## EXAMPLE FILLED VALUES

```
FLASK_PORT=3001
FLASK_DEBUG=False
META_APP_ID=1234567890123456
META_APP_SECRET=abc123def456ghi789jkl012mno345pq
META_PAGE_ID=9876543210987654
META_PAGE_ACCESS_TOKEN=EAAPn5ZCxyz...actual_token_here...
META_LEAD_FORM_ID=4567890123456789
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
```

(Replace with YOUR actual values)
