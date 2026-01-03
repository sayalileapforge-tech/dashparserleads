# DASH Parser - Quick Reference

## How It Works

### 1. User Flow
```
User uploads DASH PDF 
    ↓
handleFileUpload() detects docType='dash'
    ↓
Calls parseDASHPDF(file, driverNum)
    ↓
Sends POST to /api/parse-dash with PDF file
    ↓
Backend parses PDF with regex patterns
    ↓
Returns JSON: {success: true, data: {...}, errors: []}
    ↓
UI populates form fields with extracted data
    ↓
User sees populated form, can edit/save
```

### 2. Backend Endpoint

**Endpoint**: `POST /api/parse-dash`
**Accepts**: multipart/form-data with 'file' field
**Returns**: 
```json
{
  "success": true,
  "data": {
    "name": "VALUE or -",
    "dln": "VALUE or -",
    "dob": "MM/DD/YYYY or -",
    "address": "VALUE or -",
    "gender": "M/F or -",
    "marital_status": "VALUE or -",
    "years_licensed": "NUMBER or -",
    "years_continuous_insurance": "NUMBER or -",
    "years_claims_free": "NUMBER or -",
    "claims_6y": "NUMBER or -",
    "first_party_6y": "NUMBER or -",
    "comprehensive_6y": "NUMBER or -",
    "dcpd_6y": "NUMBER or -",
    "current_company": "VALUE or -",
    "current_policy_expiry": "MM/DD/YYYY or -",
    "current_vehicles_count": "NUMBER or -",
    "current_operators_count": "NUMBER or -"
  },
  "errors": []
}
```

### 3. Parsing Rules

- **Name**: Extracted from "DRIVER REPORT" section header
- **DLN**: Pattern: `DLN: [A-Z0-9\-]+`
- **DOB**: Pattern: `Date of Birth: YYYY-MM-DD` → converted to MM/DD/YYYY
- **Address**: Pattern: `Address: [content]` until next field
- **Gender**: Pattern: `Gender: [M/F/Male/Female]` → M or F
- **History**: `Years Licensed`, `Years Claims Free`, etc. → extract number
- **Claims**: `Number of Claims in Last 6 Years` → extract number
- **Policy**: First policy block → extract company and expiry date

### 4. Dynamic Extraction

The parser uses **regex patterns**, not hardcoded positions:
- Adapts to PDF variations
- Works with any DASH PDF
- No coordinate-based extraction
- Case-insensitive matching where appropriate

### 5. Data Rules

- **Real value exists** → Show actual value
- **Data missing in PDF** → Show "-"
- **Empty strings** → Never used (show "-")
- **Dates** → Always MM/DD/YYYY format
- **Numbers** → String representation (not int)

### 6. UI Field Mapping

| Parser Field | HTML Element ID | Type |
|---|---|---|
| name | copy-name, prev-name | Input/Display |
| dob | copy-dob | Input |
| dln | copy-license, prev-dln | Input/Display |
| address | copy-address, prev-address | Input/Display |
| claims_6y | prev-claims | Display |
| first_party_6y | prev-firstparty | Display |
| current_company | prev-company, copy-company-insured | Display/Input |
| current_policy_expiry | prev-days-expiry | Display (calculated) |
| years_continuous_insurance | copy-cont-ins | Input |

### 7. Debugging

**Console Output**:
```javascript
[DASH] Parsing DASH PDF for driver N: filename.pdf
[DASH] Successfully parsed. Extracted fields: {...}
[DASH] ✓ Form fields populated successfully
```

**On Error**:
```javascript
[DASH] Parsing failed: [error messages]
[DASH] Error details: ...
```

Check browser DevTools → Console tab to debug parsing issues.

### 8. Testing

Run this to test the endpoint:
```bash
python test_dash_integration.py
```

Manual test:
```bash
curl -X POST http://localhost:3001/api/parse-dash \
  -F "file=@DASH_Report.pdf"
```

### 9. Implementation Files

| File | Purpose | Status |
|---|---|---|
| dash_parser.py | PDF parsing logic | ✓ Created |
| app.py | Backend endpoint | ✓ Modified |
| Untitled-2.html | UI with integration | ✓ Created |
| test_dash_integration.py | Integration tests | ✓ Created |

### 10. Protected (Not Modified)

- ✓ Meta Dashboard
- ✓ Leads API
- ✓ Search functionality
- ✓ Database schema
- ✓ Meta API integration

---

## Common Issues & Solutions

| Issue | Solution |
|---|---|
| "Network error" in console | Check if server is running: `python app.py` |
| "Parsing failed" in console | Check PDF format - must be DASH report |
| Form fields not populating | Check browser console [DASH] logs for errors |
| "-" showing for existing data | PDF text may be garbled - check regex patterns |
| Server won't start | Check for port 3001 conflict or Python errors |

---

## Next: MVR Parser

When implementing MVR parser:
1. Create `mvr_parser.py` with similar structure
2. Add `/api/parse-mvr` endpoint
3. Add `parseMVRPDF()` function in UI
4. Update `handleFileUpload()` to detect docType='mvr'
5. Test with MVR PDF samples

Same patterns apply - dynamic extraction, "-" for missing data, no hardcoding.
