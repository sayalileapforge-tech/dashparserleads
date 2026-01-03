# G/G1/G2 Calculation Fix - Summary of Changes

## Root Cause Identified
The "1 MAX" (Combination) section was showing **WRONG DATES** (02/03/2029, 02/03/2027, 02/03/2025) because:

1. **MVR Parser Bug**: Was calculating G/G1/G2 using WRONG dates:
   - Using `licence_expiry_date` (2030-03-02) as the base for calculation
   - Instead of `firstInsuranceDate` (2015-03-21) from DASH
   
2. **DASH Parser Bug**: Was trying to calculate G/G1/G2 without MVR data:
   - DASH doesn't have `issueDate` (that comes from MVR)
   - Frontend showed wrong dates from incomplete calculation

## Solution Implemented

### 1. **mvr_parser_strict.py** - REMOVED Wrong Calculation
   - **File**: `mvr_parser_strict.py` Line 311
   - **Change**: Removed `_calculate_g_dates()` method that was using wrong dates
   - **Reason**: G/G1/G2 requires BOTH DASH (firstInsuranceDate) AND MVR (issueDate)
   - **Now**: MVR parser only extracts MVR fields, doesn't calculate G/G1/G2

### 2. **app.py** - REMOVED Wrong Calculation from DASH Endpoint
   - **File**: `app.py` Lines 907-938
   - **Change**: Removed G/G1/G2 calculation from `/api/parse-dash`
   - **Reason**: DASH alone doesn't have `issueDate` needed for calculation
   - **Now**: Defers calculation to combination endpoint

### 3. **Untitled-2.html** - ADDED Smart Combination Calculation
   - **File**: `Untitled-2.html` Lines 969-971, 1753-1755, 1861-1906
   - **Changes**:
     a) Added variables to store parsed data:
        - `parsedDASHData[driverNum]` - stores DASH extraction result
        - `parsedMVRData[driverNum]` - stores MVR extraction result
     
     b) Updated DASH parsing to store data and trigger combination:
        ```javascript
        parsedDASHData[driverNum] = data;
        calculateCombinationDates(driverNum);
        ```
     
     c) Updated MVR parsing to store data and trigger combination:
        ```javascript
        parsedMVRData[driverNum] = result.mvr_data;
        calculateCombinationDates(driverNum);
        ```
     
     d) Added NEW `calculateCombinationDates()` function:
        - Waits for BOTH DASH and MVR data
        - Combines them in format expected by backend
        - Calls `/api/calculate-g-dates` with PDF mode
        - Populates combination section with correct dates

### 4. **Flow Diagram - How It Works Now**

```
┌─────────────────┐         ┌─────────────────┐
│  Upload DASH    │         │  Upload MVR     │
└────────┬────────┘         └────────┬────────┘
         │                           │
         ▼                           ▼
   /api/parse-dash          /api/parse-mvr
         │                           │
         ▼                           ▼
  Store in parsedDASHData   Store in parsedMVRData
         │                           │
         └──────────┬────────────────┘
                    ▼
         Both documents available?
         (parsedDASHData[n] && parsedMVRData[n])
                    │
         ┌──────────▼──────────┐
         │ YES                 │ NO
         ▼                     ▼
  Combine DASH+MVR      Wait for other document
  Call /api/calculate-g-dates (PDF mode)
  Receive calculated G/G1/G2 dates
  Populate "1 MAX" section with dates
         │
         ▼
  Display: G: 03/21/2014, G2: 03/21/2012, G1: 03/21/2010
  ✓ CORRECT!
```

## Data Flow for Combination Calculation

```python
# Backend /api/calculate-g-dates (PDF mode)
# Receives:
{
    "mode": "pdf",
    "pdf_data": {
        "driver": {
            # DASH data - contains firstInsuranceDate
            "firstInsuranceDate": "2015-03-21",
            "name": "John Smith",
            ...
        },
        "mvr_data": {
            # MVR data - contains issueDate, licence_expiry_date, birth_date
            "issue_date": "2001-11-16",
            "licence_expiry_date": "2030-03-02",
            "birth_date": "1985-05-15",
            ...
        }
    }
}

# license_history_integration.py process_pdf_extraction():
# Extracts:
# - firstInsuranceDate from DASH
# - issueDate from MVR
# - licenseExpiryDate from MVR (for experience validation)
# - birthDate from MVR (for experience validation)

# Calculation (g1g2_calculator.py):
# G = 2015-03-21 - 1 year = 2014-03-21
# G2 = 2015-03-21 - 3 years = 2012-03-21
# G1 = 2015-03-21 - 5 years = 2010-03-21

# Frontend receives and displays:
# G: 03/21/2014, G2: 03/21/2012, G1: 03/21/2010 ✓
```

## What Changed vs. What Stayed the Same

### ✓ CORRECT (Not Changed)
- `g1g2_calculator.py` - CORRECT simple calendar year subtraction logic
- `license_history_integration.py` - CORRECT combination logic
- Manual entry calculation - Still working correctly

### ✗ BROKEN (FIXED)
- MVR parser calculating with wrong dates
- DASH parser trying to calculate without MVR data
- Frontend not combining both data sources before calculating

### ✓ ADDED
- Frontend now stores parsed DASH and MVR data
- Frontend now triggers combination calculation when both available
- Combination section now shows correct dates

## Expected Result
When user uploads BOTH DASH and MVR PDFs:
- Combination section automatically calculates
- Shows: G: 03/21/2014, G2: 03/21/2012, G1: 03/21/2010
- NOT: 02/03/2029, 02/03/2027, 02/03/2025 ✗

## Files Modified
1. `mvr_parser_strict.py` - Removed `_calculate_g_dates()` method
2. `app.py` - Removed G/G1/G2 calculation from DASH endpoint
3. `Untitled-2.html` - Added combination calculation logic and data storage
