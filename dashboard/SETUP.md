# Quick Start Guide

## 5-Minute Setup

### Step 1: Start the Backend (Choose One)

**Windows:**
```cmd
cd backend
start.bat
```

**macOS/Linux:**
```bash
cd backend
chmod +x start.sh
./start.sh
```

### Step 2: Configure Environment

The startup script creates `.env` from `.env.example`. Edit it with your database credentials:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=insurance_leads
```

### Step 3: Verify Backend is Running

Open browser: **http://localhost:8000/health**

You should see:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Step 4: Open Dashboard

Open: **dashboard.html**

The dashboard will automatically connect to the backend and populate the lead table.

---

## Testing the API

### View API Documentation
```
http://localhost:8000/docs
```

### Get Leads
```bash
curl http://localhost:8000/api/leads
```

### Update Lead Status
```bash
curl -X PUT http://localhost:8000/api/leads/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "contacted"}'
```

---

## Adding Sample Leads

To test the dashboard with sample data:

```bash
# Using curl to add a lead
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "meta_lead_id": "test_123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "(555) 123-4567"
  }'
```

Or directly insert into MySQL:

```sql
INSERT INTO leads (
  meta_lead_id, first_name, last_name, email, phone, status, created_at, updated_at
) VALUES (
  'test_123', 'John', 'Doe', 'john@example.com', '(555) 123-4567', 'new', NOW(), NOW()
);
```

---

## Frontend Features Ready to Use

✅ **Fetch Leads** - Automatically loads from backend  
✅ **Update Status** - Status dropdown saves to backend  
✅ **Process Button** - Ready for lead processing  
✅ **Premium Calculator** - Auto-calculates totals  
✅ **Search & Filter** - Ready to implement  

---

## Project Structure

```
dashboard/
├── dashboard.html           ← Your UI (now connected!)
└── backend/
    ├── app/                 ← FastAPI application
    ├── .env                 ← Your credentials (create from .env.example)
    ├── requirements.txt     ← Python packages
    ├── run.py              ← Start server
    ├── start.bat/start.sh  ← Quick startup
    └── README.md           ← Full documentation
```

---

## Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/leads` | Fetch all leads |
| GET | `/api/leads/{id}` | Get single lead |
| PUT | `/api/leads/{id}` | Update lead info |
| PUT | `/api/leads/{id}/status` | Update status |
| POST | `/api/process/{id}` | Process lead (placeholder) |
| GET | `/health` | Health check |
| GET | `/docs` | API documentation |

---

## Troubleshooting

**Backend won't start?**
- Make sure MySQL is running
- Check `.env` database credentials
- Verify Python 3.10+ is installed

**Dashboard shows "No Leads"?**
- Add sample data using curl or MySQL
- Check browser console for errors (F12)
- Ensure backend is at http://localhost:8000

**Database connection error?**
- Check if MySQL is running
- Verify credentials in `.env`
- Ensure database `insurance_leads` exists

---

## Next: Meta API Integration

Once you have your Meta credentials:

1. Add to `.env`:
   ```env
   META_PAGE_ID=your_page_id
   META_PAGE_ACCESS_TOKEN=your_long_lived_token
   ```

2. The API client in `app/services/meta_service.py` is ready to use

3. Currently marked with TODO comments - remove them once credentials are added

---

## What's Next?

- ✅ Backend is running
- ✅ Dashboard is connected
- ✅ Database is ready
- ⏳ Add Meta API credentials when ready
- ⏳ Deploy to production

See `backend/README.md` for full documentation.
