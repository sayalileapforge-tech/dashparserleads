# 📘 Facebook Meta Leads Integration Setup Guide

Your application is now ready to fetch leads from Facebook! Here's how to configure it:

## Step 1: Get Your Meta Business Account
- Go to https://business.facebook.com
- Sign in with your Facebook account
- Create a Business Account if you don't have one

## Step 2: Create a Meta App
1. Go to https://developers.facebook.com/apps
2. Click "Create App" → Choose "Business" type
3. Fill in app details (Name, Purpose, etc.)
4. Add "Lead Ads" to your app

## Step 3: Get Your Lead Form ID
1. In Meta Business Suite, go to **Ads Manager**
2. Navigate to **Leads** section
3. Select your Lead Form
4. Copy the **Form ID** from the URL or settings

## Step 4: Generate Access Token
1. In Developer Dashboard, go to **Tools** → **Access Token Debug**
2. Create a new access token with these permissions:
   - `leads_retrieval` (to fetch leads)
   - `pages_read_engagement`
   - `page_read_user_profiles`
3. Copy the **Access Token**

## Step 5: Find Your Page ID
1. In Facebook Business Manager, go to **Pages**
2. Select your page
3. Copy the **Page ID** from page settings

## Step 6: Get App ID & Secret
1. In Developer Dashboard, go to **Settings** → **Basic**
2. Copy your **App ID**
3. Copy your **App Secret** (keep this confidential!)

## Step 7: Configure .env File

Edit `.env` file in your project and replace placeholders:

```
META_APP_ID=1234567890123456
META_APP_SECRET=abc123def456ghi789jkl012mno345pqr
META_PAGE_ID=9876543210123456
META_PAGE_ACCESS_TOKEN=EAA... (long token string)
META_LEAD_FORM_ID=1234567890
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
```

## Step 8: Verify Setup

Test your configuration:
```bash
python -c "
from meta_leads_fetcher import get_fetcher
fetcher = get_fetcher()
leads = fetcher.fetch_leads()
print(f'Successfully fetched {len(leads)} leads!')
"
```

## Step 9: Enable Webhook (Optional)

If you want automatic lead syncing:
1. Go to your app settings
2. Set Webhook URL to: `https://yourdomain.com/api/meta-webhook`
3. Verify Token: `insurance_dashboard_webhook`
4. Subscribe to `lead` event

## Troubleshooting

| Error | Solution |
|-------|----------|
| `HTTP 400 - Invalid request` | Check Form ID format and credentials |
| `HTTP 401 - Unauthorized` | Access token expired or invalid |
| `HTTP 403 - Forbidden` | Token lacks required permissions |
| `No leads returned` | Check your lead form has submissions |

## Current Status

✅ Your application is running at: http://localhost:3001
✅ Meta API integration is live and attempting to fetch leads
✅ Fallback to sample data if credentials are not configured

Once you add your credentials to `.env`, new leads will appear automatically!

---
**Note:** Keep your APP_SECRET and ACCESS_TOKEN confidential. Never commit them to GitHub!
