# Insurance Leads Management System

A clean, minimal backend for managing insurance leads from Meta Lead Ads with a modern web dashboard.

## Project Structure

```
backend/
├── app/
│   ├── core/              # Configuration and database
│   │   ├── config.py      # Environment variables
│   │   └── database.py    # SQLAlchemy setup
│   ├── models/            # Database models
│   │   └── lead.py        # Lead model
│   ├── routes/            # API endpoints
│   │   ├── leads.py       # Lead CRUD endpoints
│   │   └── process.py     # Lead processing (placeholder)
│   ├── schemas/           # Pydantic request/response schemas
│   │   └── lead.py        # Lead schemas
│   ├── services/          # Business logic
│   │   ├── lead_service.py      # Lead operations
│   │   └── meta_service.py      # Meta API client
│   └── main.py            # FastAPI app initialization
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── run.py                 # Entry point
├── start.bat              # Windows startup script
└── start.sh               # macOS/Linux startup script
```

## Requirements

- Python 3.10+
- MySQL 5.7+ or MySQL 8.0
- FastAPI & Uvicorn
- SQLAlchemy ORM

## Quick Start

### 1. Setup Environment

```bash
# Windows
start.bat

# macOS/Linux
chmod +x start.sh
./start.sh
```

### 2. Configure Database

Edit `.env` with your MySQL credentials:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=insurance_leads
```

### 3. Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment file
cp .env.example .env

# Run the application
python run.py
```

## API Endpoints

### Leads Management

- **GET** `/api/leads` - Fetch all leads with pagination
  - Query params: `page=1`, `page_size=25`, `status=new`, `search=term`
  - Returns: List of leads

- **GET** `/api/leads/{id}` - Get specific lead
  - Returns: Single lead

- **PUT** `/api/leads/{id}` - Update lead information
  - Body: `{ "field": "value" }`
  - Returns: Updated lead

- **PUT** `/api/leads/{id}/status` - Update lead status
  - Body: `{ "status": "contacted" }`
  - Status values: `new`, `contacted`, `quote_sent`, `closed_won`, `closed_lost`, `no_answer`
  - Returns: Updated lead

### Lead Processing

- **POST** `/api/process/{id}` - Process a lead
  - *Placeholder endpoint for future implementation*
  - Returns: Processed lead

### Health Check

- **GET** `/health` - API health status
- **GET** `/docs` - Swagger API documentation

## Database Schema

### Leads Table

```sql
id                  INT PRIMARY KEY
meta_lead_id        VARCHAR(255) UNIQUE  -- Facebook Lead ID
first_name          VARCHAR(255)
last_name           VARCHAR(255)
full_name           VARCHAR(255)
email               VARCHAR(255)
phone               VARCHAR(20)
company_name        VARCHAR(255)
job_title           VARCHAR(255)
city                VARCHAR(255)
state               VARCHAR(2)
country             VARCHAR(255)
zip_code            VARCHAR(20)
status              ENUM(...)            -- Lead status
notes               TEXT
auto_premium        INT                  -- In cents
home_premium        INT                  -- In cents
tenant_premium      INT                  -- In cents
raw_payload         TEXT                 -- JSON from Meta API
created_at          DATETIME
updated_at          DATETIME
```

## Meta API Integration

Meta API integration code is prepared but **NOT YET ACTIVATED**.

### To Enable Meta Integration:

1. Get your Meta credentials:
   - Page ID from Meta Business Suite
   - Long-lived Page Access Token from Meta Developer App

2. Add to `.env`:
   ```env
   META_PAGE_ID=your_page_id
   META_PAGE_ACCESS_TOKEN=your_long_lived_token
   ```

3. The client is ready in `app/services/meta_service.py`

### Integration Points:

- **MetaGraphAPIClient**: Ready to fetch leads from Meta Lead Ads
- **TODO Markers**: Code has TODO comments where credentials are needed
- **No OAuth**: Long-lived tokens only, no login flows

## Frontend Integration

The dashboard (`../dashboard.html`) connects to the backend via fetch API:

```javascript
// Fetch leads from backend
fetch('http://localhost:8000/api/leads')
  .then(res => res.json())
  .then(data => renderTable(data.leads));

// Update lead status
fetch('http://localhost:8000/api/leads/1/status', {
  method: 'PUT',
  body: JSON.stringify({ status: 'contacted' })
});
```

**CORS is enabled** - your frontend can make requests from any origin.

## Development

### Check Backend Status

```bash
# Terminal
curl http://localhost:8000/health

# Browser
http://localhost:8000/health
http://localhost:8000/docs
```

### Database Management

The database tables are created automatically on first run via SQLAlchemy.

### Add Sample Data

Edit the Lead model or use API POST requests to add sample leads for testing.

## Production Deployment

For production deployment:

1. Set `API_DEBUG=False` in `.env`
2. Use a production WSGI server (Gunicorn, etc.)
3. Use environment variables for secrets
4. Configure proper CORS origins
5. Use HTTPS/SSL certificates
6. Set up database backups

## Troubleshooting

### Port Already in Use
```bash
API_PORT=8001 python run.py
```

### Database Connection Error
- Verify MySQL is running
- Check credentials in `.env`
- Ensure database exists

### Module Not Found
```bash
pip install -r requirements.txt
```

### CORS Issues
- Check `app/main.py` CORS middleware configuration
- Frontend and backend must be on same domain in production

## API Response Format

### Success Response (200)
```json
{
  "id": 1,
  "meta_lead_id": "123456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "(555) 123-4567",
  "status": "new",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Error Response (400/404/500)
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Next Steps

1. ✅ Backend is ready
2. ⏳ Waiting for Meta API credentials (Page ID + Token)
3. ⏳ Add sample leads via API or database
4. ⏳ Test dashboard integration
5. ⏳ Deploy to production

## Support

For issues or questions:
1. Check application logs
2. Verify `.env` configuration
3. Check browser console for frontend errors
4. Review API documentation at `/docs` endpoint

---

**Status**: Ready for testing with sample data | Awaiting Meta API credentials for live integration
