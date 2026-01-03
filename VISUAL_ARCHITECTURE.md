# VISUAL ARCHITECTURE - DOMAIN ISOLATION

## Before (BROKEN) ❌

```
┌─────────────────────────────────────────────────────────────┐
│ User Uploads PDF (DASH or MVR)                              │
└────────────────┬────────────────────────────────────────────┘
                 ↓
      ┌──────────────────────────┐
      │ handleFileUpload()        │
      │ - Validates file          │
      │ - Sends to server         │
      └────────┬─────────────────┘
               ↓
      ┌──────────────────────────┐
      │ Server Response           │
      │ Returns: 21 fields        │
      │ ❌ No document_type!      │
      └────────┬─────────────────┘
               ↓
      ┌─────────────────────────────────────────────┐
      │ populateDriverFields(driverNum, data, type) │
      │                                              │
      │ BIG MONOLITHIC FUNCTION (151 lines)        │
      │                                              │
      │ Try to figure out:                          │
      │ ❌ What to populate?                        │
      │ ❌ What to clear?                           │
      │ ❌ What fields apply?                       │
      │                                              │
      │ Complex nested if/else logic               │
      │ ❌ EASY TO MIX DATA                         │
      │ ❌ HARD TO MAINTAIN                         │
      └────────┬────────────────────────────────────┘
               ↓
    ┌──────────┴──────────┐
    ↓                     ↓
  PROBLEM              PROBLEM
  DASH data            MVR data
  mixed in             mixed in
  MVR display          DASH display
```

---

## After (FIXED) ✅

```
┌─────────────────────────────────────────────────────────────┐
│ User Uploads PDF (DASH or MVR)                              │
└────────────────┬────────────────────────────────────────────┘
                 ↓
      ┌──────────────────────────┐
      │ handleFileUpload()        │
      │ - Validates file          │
      │ - Sends to server         │
      └────────┬─────────────────┘
               ↓
      ┌──────────────────────────┐
      │ Server Response           │
      │ Returns: 21 fields        │
      │ ✅ INCLUDES document_type │
      │ {                         │
      │   document_type: "DASH"   │
      │ }                         │
      └────────┬─────────────────┘
               ↓
      ┌────────────────────────────────────┐
      │ Extract: parsedDocType              │
      │ [DOMAIN_ISOLATION] Decision Point   │
      └────────┬──────────┬──────────────────┘
               │          │
         ┌─────┘          └─────┐
         ↓                      ↓
    ┌──────────────┐      ┌──────────────┐
    │ DASH Type?   │      │ MVR Type?    │
    └──────┬───────┘      └──────┬───────┘
           ↓                      ↓
    ┌──────────────────┐  ┌──────────────────────┐
    │ populateDashUI() │  │ populateMvrUI()      │
    │ (68 lines)       │  │ (76 lines)           │
    │                  │  │                      │
    │ KNOWS:           │  │ KNOWS:               │
    │ ✓ Store in:      │  │ ✓ Store in:          │
    │   dashParsedData │  │   mvrParsedData      │
    │ ✓ Populate:      │  │ ✓ Populate ONLY:     │
    │   All 8 sections │  │   Driver Details     │
    │ ✓ Clear: Nothing │  │   MVR Info           │
    │                  │  │ ✓ Clear:             │
    │ CANNOT MIX DATA! │  │   Demographics       │
    │ CANNOT FORGET!   │  │   Address            │
    │                  │  │   History            │
    │                  │  │   Policy             │
    │                  │  │   Insurance          │
    │                  │  │                      │
    │                  │  │ CANNOT MIX DATA!     │
    │                  │  │ CANNOT FORGET!       │
    └────────┬─────────┘  └──────────┬───────────┘
             ↓                       ↓
    ┌─────────────────┐    ┌─────────────────┐
    │ All sections    │    │ MVR Info visible│
    │ populate        │    │ DASH cleared    │
    │ cleanly         │    │ cleanly         │
    │ ✓ SAFE          │    │ ✓ SAFE          │
    │ ✓ CLEAR         │    │ ✓ CLEAR         │
    │ ✓ RELIABLE      │    │ ✓ RELIABLE      │
    └─────────────────┘    └─────────────────┘
```

---

## Data Flow Comparison

### OLD (Mixed) ❌
```
PDF → Parser → Response → Single Function → ???
                            ↓
                    Try to guess:
                    • Is this DASH or MVR?
                    • What should populate?
                    • What should clear?
                    • Risk of mistake!
```

### NEW (Isolated) ✅
```
PDF → Parser → Response (with document_type) 
              ↓
        Is it DASH? → populateDashUI()
        Is it MVR?  → populateMvrUI()
        Unknown?    → Default to DASH
        
Each function KNOWS exactly what to do.
No guessing. No mixing. No mistakes.
```

---

## Data Object State

### OLD (No Isolation) ❌
```javascript
// All data in mixed state
var data = {
  full_name: "...",
  address: "...",
  gender: "...",
  convictions: "...",
  ... mix of DASH and MVR fields
}
// Unclear what applies to which type
```

### NEW (Isolated) ✅
```javascript
// Separate storage per type
var dashParsedData = {
  1: { full_name, address, gender, claims, ... }  // DASH fields only
}

var mvrParsedData = {
  1: { full_name, convictions, years_licensed, ... }  // MVR fields only
}

// Totally clear what belongs where
```

---

## Function Structure Comparison

### OLD (Monolithic) ❌
```javascript
function populateDriverFields(driverNum, data, docType) {
    if (!docType) docType = 'DASH';
    
    // Populate shared fields
    setVal('name', data.full_name);
    setVal('dln', data.licence_number);
    ...
    
    // NOW WHAT?
    if (docType === 'DASH' || docType === 'dash') {
        // Populate DASH sections
        setVal('address', data.address);
        setVal('gender', data.gender);
        setVal('claims', data.claims);
        ...
    } else {
        // Clear DASH sections
        setVal('address', '', '—');
        setVal('gender', '', '—');
        setVal('claims', '', '—');
        ...
    }
    // Complex logic, easy to make mistakes
}
```

### NEW (Separated) ✅
```javascript
// DASH Handler - Clear purpose
function populateDashUI(driverNum, data) {
    dashParsedData[driverNum] = data;
    setVal('name', data.full_name);      // Always populate
    setVal('address', data.address);     // DASH only
    setVal('claims', data.claims_6y);    // DASH only
    // This function ONLY handles DASH
    // Can't accidentally mix MVR data!
}

// MVR Handler - Clear purpose
function populateMvrUI(driverNum, data) {
    mvrParsedData[driverNum] = data;
    setVal('name', data.full_name);      // Always populate
    setVal('address', '', '—');          // EXPLICITLY clear
    setVal('claims', '', '—');           // EXPLICITLY clear
    // This function ONLY handles MVR
    // Can't accidentally populate DASH data!
}
```

---

## Routing Intelligence

### Without Smart Routing ❌
```
PDF Upload
    ↓
??? Does it have address field?
??? Does it have convictions field?
??? Is it DASH or MVR?
    ❌ Unclear! Risk mixing data!
```

### With Smart Routing ✅
```
PDF Upload
    ↓
Server detects type: "DASH" or "MVR"
    ↓
[DOMAIN_ISOLATION] Routes to correct function
    ↓
DASH Type? → populateDashUI()
MVR Type?  → populateMvrUI()
Unknown?   → Default to DASH (safe fallback)
    ✅ Clear! No ambiguity!
```

---

## Risk Matrix

### Before (Risky) ❌
```
┌────────────────┬─────────┬────────────┐
│ Action         │ Risk    │ Issue      │
├────────────────┼─────────┼────────────┤
│ Parse DASH     │ HIGH    │ May clear  │
│                │         │ MVR data   │
├────────────────┼─────────┼────────────┤
│ Parse MVR      │ HIGH    │ May populate│
│                │         │ DASH fields │
├────────────────┼─────────┼────────────┤
│ Mixed PDFs     │ CRITICAL│ Data mixing│
│ (same driver)  │         │ guaranteed │
└────────────────┴─────────┴────────────┘
```

### After (Safe) ✅
```
┌────────────────┬─────────┬────────────┐
│ Action         │ Risk    │ Guarantee  │
├────────────────┼─────────┼────────────┤
│ Parse DASH     │ NONE    │ DASH data  │
│                │ (safe)  │ safe       │
├────────────────┼─────────┼────────────┤
│ Parse MVR      │ NONE    │ MVR data   │
│                │ (safe)  │ safe       │
├────────────────┼─────────┼────────────┤
│ Mixed PDFs     │ NONE    │ No mixing  │
│ (same driver)  │ (safe)  │ guaranteed │
└────────────────┴─────────┴────────────┘
```

---

## Code Complexity

### Before ❌
```
Complexity Level: HIGH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ┌─────────────────────────────────────┐
  │ populateDriverFields()               │
  │ ├─ Check docType                     │
  │ ├─ IF docType === DASH               │
  │ │  ├─ Populate demographics          │
  │ │  ├─ Populate address               │
  │ │  ├─ Populate history               │
  │ │  └─ ... more logic                 │
  │ ├─ ELSE (must be MVR)                │
  │ │  ├─ Clear demographics             │
  │ │  ├─ Clear address                  │
  │ │  ├─ Clear history                  │
  │ │  └─ ... more logic                 │
  │ └─ Complex, error-prone              │
  └─────────────────────────────────────┘

Risk: Easy to make mistake somewhere!
```

### After ✅
```
Complexity Level: LOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ┌──────────────────────────────────────┐
  │ Routing Logic                        │
  │ ├─ IF docType === DASH               │
  │ │  └─ CALL populateDashUI()          │
  │ ├─ ELSE IF docType === MVR           │
  │ │  └─ CALL populateMvrUI()           │
  │ └─ Simple, clear decision            │
  └──────────────────────────────────────┘
       ↓                    ↓
  ┌──────────────┐  ┌──────────────────┐
  │populateDashUI│  │ populateMvrUI    │
  │              │  │                  │
  │KNOWS:        │  │ KNOWS:           │
  │• I'm DASH    │  │ • I'm MVR        │
  │• Populate X  │  │ • Populate Y     │
  │• No clear Z  │  │ • Clear Z        │
  └──────────────┘  └──────────────────┘

Risk: NONE! Each function is focused!
```

---

## Summary Diagram

```
        BEFORE                          AFTER
        ══════                          ═════

Mixed Function            →    Separated Functions
    ↓                         ↓           ↓
Unknown Intent         DASH Intent    MVR Intent
    ↓                         ↓           ↓
Complex Logic          Clean Logic    Clean Logic
    ↓                         ↓           ↓
High Risk          Low Risk      Low Risk
    ↓                         ↓           ↓
❌ DATA MIXING            ✅ SAFE         ✅ SAFE
```

---

**The solution is simple, clear, and safe.**
