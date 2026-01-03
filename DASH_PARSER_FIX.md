# ROOT CAUSE FOUND & FIXED

## The Problem
Combination section showing WRONG dates:
- G: 08/08/2025 (should be ~03/21/2014)
- G2: 08/08/2023 (should be ~03/21/2012)
- G1: 08/08/2021 (should be ~03/21/2010)

## Root Cause Analysis
The DASH parser was extracting the **WRONG DATE** as `firstInsuranceDate`:

1. The DASH parser regex was looking for BOTH:
   - "End of Latest Term" (correct - when insurance term ended)
   - "Expiry Date" (wrong - when current policy EXPIRES)

2. When the PDF contained "Expiry Date: 08/08/2026", the parser would match this:
   - Extracted as: firstInsuranceDate = 2026-08-08
   - Calculation: 2026-08-08 - 1 year = 2025-08-08
   - Display: 08/08/2025 ✗ (WRONG!)

3. The correct value should be from "End of Latest Term", which is when the insurance coverage period ended (a date in the past).

##  THE FIX
File: `dash_parser.py` Lines 238 and 261

**BEFORE** (WRONG):
```python
r'(?:End of (?:the )?Latest Term|Expiry Date)\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})'
```
This pattern matched EITHER "End of Latest Term" OR "Expiry Date"

**AFTER** (CORRECT):
```python
r'End of (?:the )?Latest Term\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})'
```
This pattern matches ONLY "End of Latest Term"

## Why This Fixes It
- The pattern no longer matches "Expiry Date" (which is a future policy expiry)
- Now ONLY extracts "End of Latest Term" (which is the actual first insurance date from history)
- If the PDF has "End of Latest Term: 2015-03-21", it will extract that correctly
- Calculation: 2015-03-21 - 1 year = 2014-03-21
- Display: 03/21/2014 ✓ (CORRECT!)

## What to Do Now
1. **Reload the browser** to get the updated JavaScript
2. **Re-upload both DASH and MVR PDFs**
3. The combination section should now show the **CORRECT** dates

## If Dates Are Still Wrong
This could mean:
1. The DASH PDF doesn't have an "End of Latest Term" field
2. The PDF has "Expiry Date" but no "End of Latest Term"
3. The extraction is finding a different date

**Solution**: Check the DASH PDF for what date fields it contains. The PDF must have explicit "End of Latest Term" field for the parser to extract it.

## Files Changed
- `dash_parser.py` - Fixed regex pattern to exclude "Expiry Date"

## Status
✅ Fix applied
✅ Ready to test
✅ One change only (minimal risk)

Refresh the browser and upload the PDFs again to see if it works!
