# YOUR REAL META CREDENTIALS

## ⚠️ IMPORTANT: These are YOUR actual credentials from your code

```
META_APP_ID=1374336741109403
META_APP_SECRET=ca57447d436108c0452657bb084f8632
META_PAGE_ID=775140625692611
META_PAGE_ACCESS_TOKEN=EAATh87VBbpsBQbZC0Iztaz5GLopTmbACAsTYjoek436ZATcFl7OoETYfZBFhGZCDpSuSPJOi7AWOmGaYzjGFOSBhgmZC09X7TMXfA4nmHAxwxZCof4fJHqdKaEgB6ri6uDTad9zcTLf5wP7ImZAZAITGD4ZB7KWOClOxsQDdLjK190cw4ZBgdgyQPjcKvIEAyrZBpgqbw9P
META_LEAD_FORM_ID=1395244698621351
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
FLASK_PORT=3001
FLASK_DEBUG=False
```

---

## FOR RENDER DEPLOYMENT - Copy These Exactly:

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
META_APP_ID=1374336741109403
```

### Variable 4:
```
META_APP_SECRET=ca57447d436108c0452657bb084f8632
```

### Variable 5:
```
META_PAGE_ID=775140625692611
```

### Variable 6:
```
META_PAGE_ACCESS_TOKEN=EAATh87VBbpsBQbZC0Iztaz5GLopTmbACAsTYjoek436ZATcFl7OoETYfZBFhGZCDpSuSPJOi7AWOmGaYzjGFOSBhgmZC09X7TMXfA4nmHAxwxZCof4fJHqdKaEgB6ri6uDTad9zcTLf5wP7ImZAZAITGD4ZB7KWOClOxsQDdLjK190cw4ZBgdgyQPjcKvIEAyrZBpgqbw9P
```

### Variable 7:
```
META_LEAD_FORM_ID=1395244698621351
```

### Variable 8:
```
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
```

---

## ⚠️ SECURITY NOTE

**DO NOT commit this file to GitHub!**

These are sensitive credentials. Make sure:
- ✅ Keep them private
- ✅ Use in Render (private environment variables)
- ✅ Never share publicly
- ✅ Regenerate if accidentally exposed

---

## RENDER DEPLOYMENT STEPS

1. Go to https://dashboard.render.com
2. Create new Web Service
3. Select repository: `dashparserleads`
4. Fill all fields (root dir empty, build: `pip install -r requirements.txt`, start: `python app.py`)
5. Add all 8 environment variables above
6. Click Deploy
7. Wait 2-3 minutes ✅

Your app will auto-receive Facebook leads!
