# G/G1/G2 Calculation - Detailed Math Verification

## Test Case Data
```
From MVR Report:
  Issue Date (Licence Issue Date): 2001-11-16
  Expiry Date (Licence Expiry Date): 2030-03-02
  Birth Date: 1985-05-15

From DASH Report:
  First Insurance Date (End of Latest Term): 2015-03-21
```

## WHY THE DATES WERE WRONG (Before Fix)

### ❌ WRONG CALCULATION (Using Expiry Date)
```
Base: Licence Expiry Date = 2030-03-02

G = 2030-03-02 - 1 year = 2029-03-02 → Displayed as 02/03/2029 ✗
G2 = 2030-03-02 - 3 years = 2027-03-02 → Displayed as 02/03/2027 ✗
G1 = 2030-03-02 - 5 years = 2025-03-02 → Displayed as 02/03/2025 ✗

These are the WRONG dates the user was seeing!
```

**Why using Expiry Date is wrong**:
- Licence Expiry Date is "when does the driver's licence expire"
- NOT "when did insurance coverage first start"
- It's the wrong reference point entirely

---

## ✓ CORRECT CALCULATION (Using First Insurance Date)
```
Base: First Insurance Date = 2015-03-21

G = 2015-03-21 - 1 year = 2014-03-21 → Display as 03/21/2014 ✓
G2 = 2015-03-21 - 3 years = 2012-03-21 → Display as 03/21/2012 ✓
G1 = 2015-03-21 - 5 years = 2010-03-21 → Display as 03/21/2010 ✓

These are the CORRECT dates!
```

**Why using First Insurance Date is correct**:
- This is when insurance coverage FIRST started
- It's the anchor point for "continuous insurance" experience
- Subtracting 1/3/5 years gives the "good starting dates" for each tier

---

## Validation Check: Experience Validation

The system also checks if customer has enough experience:

```
MVR Licence Expiry Date: 2030-03-02 (day=02, month=03)
MVR Birth Date: 1985-05-15 (day=15, month=05)

Comparison (Day & Month only):
  Birth: day 15, month 05
  Expiry: day 02, month 03
  
Mismatch? YES (15 ≠ 02, or 05 ≠ 03)
  → Shows warning: "Customer has less than 5 years of experience"
  → But still calculates dates (doesn't block calculation)
```

---

## Code Implementation: Simple Calendar Year Subtraction

```python
from dateutil.relativedelta import relativedelta
from datetime import datetime

# Parse dates
first_ins = datetime.strptime("2015-03-21", "%Y-%m-%d")

# Calculate
g_date = first_ins - relativedelta(years=1)      # 2014-03-21
g2_date = first_ins - relativedelta(years=3)     # 2012-03-21
g1_date = first_ins - relativedelta(years=5)     # 2010-03-21

# Result
print(f"G:  {g_date.strftime('%Y-%m-%d')}")   # 2014-03-21 ✓
print(f"G2: {g2_date.strftime('%Y-%m-%d')}")  # 2012-03-21 ✓
print(f"G1: {g1_date.strftime('%Y-%m-%d')}")  # 2010-03-21 ✓
```

---

## Frontend Display Conversion

```javascript
// Backend returns: "2014-03-21" (ISO format)
// Frontend converts to: "03/21/2014" (mm/dd/yyyy)

function formatISOToDisplay(isoDate) {
    // "2014-03-21".split('-') = ["2014", "03", "21"]
    const parts = isoDate.split('-');
    // [month, day, year]
    return `${parts[1]}/${parts[2]}/${parts[0]}`;
    // "03/21/2014" ✓
}
```

---

## Complete Data Flow After Fix

```
1. User uploads DASH PDF
   └─ Parsed by dash_parser.py
   └─ Extracted: firstInsuranceDate = "2015-03-21"
   └─ Stored in: parsedDASHData[1] = { firstInsuranceDate, ... }
   └─ Called: calculateCombinationDates(1)
   └─ Waits: MVR data not ready yet

2. User uploads MVR PDF  
   └─ Parsed by mvr_parser_strict.py
   └─ Extracted: issue_date = "2001-11-16", licence_expiry_date = "2030-03-02"
   └─ Stored in: parsedMVRData[1] = { issue_date, licence_expiry_date, ... }
   └─ Called: calculateCombinationDates(1)
   └─ Ready: Both DASH and MVR available! ✓

3. calculateCombinationDates(1) executes
   └─ Combines: { driver: DASH, mvr_data: MVR }
   └─ Sends to: /api/calculate-g-dates with mode='pdf'

4. Backend calculates
   └─ Extracts: firstInsuranceDate from DASH
   └─ Extracts: issueDate, licence_expiry_date, birth_date from MVR
   └─ Calls: calculate_g_g1_g2(issueDate, firstInsuranceDate, birthDate, expiryDate)
   └─ Returns: {
        g_date: "2014-03-21",
        g2_date: "2012-03-21", 
        g1_date: "2010-03-21",
        success: true
      }

5. Frontend displays
   └─ G:  "03/21/2014" ✓
   └─ G2: "03/21/2012" ✓
   └─ G1: "03/21/2010" ✓
```

---

## Testing the Fix

To verify the fix works, the frontend will:

1. Automatically detect when both DASH and MVR are parsed
2. Call the calculation endpoint
3. Display the returned dates in the combination section
4. Show the CORRECT dates (03/21/2014, etc.) instead of WRONG dates (02/03/2029, etc.)

**No user action needed** - just upload both PDFs and the combination section auto-calculates with correct dates!

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Base Date Used | Licence Expiry (2030-03-02) ✗ | First Insurance (2015-03-21) ✓ |
| Calculated G | 2029-03-02 (02/03/2029) ✗ | 2014-03-21 (03/21/2014) ✓ |
| Calculated G2 | 2027-03-02 (02/03/2027) ✗ | 2012-03-21 (03/21/2012) ✓ |
| Calculated G1 | 2025-03-02 (02/03/2025) ✗ | 2010-03-21 (03/21/2010) ✓ |
| Root Cause | MVR using wrong base date | Fixed: Use correct base date |
| Location Fixed | mvr_parser_strict.py, app.py, HTML | 3 files updated |
| Impact | 100% fix for combination section | Should now show correct dates |
