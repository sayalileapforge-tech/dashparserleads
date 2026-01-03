# 🚀 Multi-Driver Dashboard - Quick Start

## Go Live Now! 

Open your browser and go to: **`http://localhost:3001`**

---

## ⚡ 5-Second Overview

**Before**: One driver per session
**After**: Unlimited drivers per session!

- 👤 **Driver 1** uploaded? Tab shows "Driver 1"
- ➕ **Click "Add Another Driver"** → New section + new tab
- 👥 **Driver 2** uploads? Tab shows "Driver 2"  
- 🔄 **Click tabs to switch** → Each driver's data displays
- 📋 **One form submission** → Saves all drivers' data

---

## 📖 How to Use (3 Simple Steps)

### Step 1️⃣: Upload Driver 1's Documents
```
1. Refresh page: http://localhost:3001
2. Look for "Driver 1" section on the LEFT
3. Click DASH button
4. Select your PDF file
5. → Right panel shows Driver 1's data
```

### Step 2️⃣: Add Driver 2 (Optional)
```
1. Scroll down in the left panel
2. Click "Add Another Driver"
3. New "Driver 2" section appears
4. Click DASH button
5. Select PDF file for Driver 2
6. → Right panel now shows Driver 2's data
```

### Step 3️⃣: Switch Between Drivers
```
1. Look at TOP RIGHT (below "Auto Preview" title)
2. You'll see tabs: "Driver 1" "Driver 2" (if added)
3. Click "Driver 1" tab
   → See Driver 1's name, address, policy info
4. Click "Driver 2" tab
   → See Driver 2's name, address, policy info
5. Click back and forth as many times as you want!
```

---

## 🎯 What's Displayed for Each Driver

### When DASH PDF is uploaded:
- ✓ Full Name
- ✓ Driver's License Number  
- ✓ Demographics (Gender, Marital Status, Years Licensed)
- ✓ Address
- ✓ Insurance History (Claims, Convictions, Gaps)
- ✓ Current Policy Company & Expiry Date
- ✓ Number of Vehicles & Operators

### When MVR PDF is uploaded:
- ✓ Birth Date
- ✓ License Expiry Date
- ✓ Years of Experience
- ✓ Convictions Details
- ✓ **Auto-calculated**: G / G1 / G2 dates

---

## 🎨 Visual Guide

```
┌─────────────────────────┬──────────────────────────────┐
│  LEFT PANEL             │  RIGHT PANEL (PREVIEW)      │
│  (Upload Area)          │  (Data Display)             │
├─────────────────────────┤                              │
│                         │  📋 Auto Preview             │
│  👤 Driver 1            │  [Driver 1] [Driver 2] ← Tabs
│  ├─ DASH / Auto+ / MVR  │                              │
│  ├─ Relationship: □     │  ┌──────────────────────┐   │
│  │  [Browse Files]      │  │ Driver Details       │   │
│  │                      │  │ ├─ Name: ______      │   │
│  ➕ Add Another Driver  │  │ ├─ DLN: ______       │   │
│  │                      │  │ ├─ Address: ______   │   │
│  👤 Driver 2            │  │ └─ etc...            │   │
│  ├─ DASH / Auto+ / MVR  │  └──────────────────────┘   │
│  ├─ Relationship: □     │                              │
│  │  [Browse Files]      │  ┌──────────────────────┐   │
│  │                      │  │ Current Policy       │   │
│  │                      │  │ ├─ Company: ______   │   │
│  │                      │  │ ├─ Expiry: ______    │   │
│  │                      │  │ └─ etc...            │   │
│  │                      │  └──────────────────────┘   │
└─────────────────────────┴──────────────────────────────┘
```

---

## ✅ Testing Checklist

Try this to test multi-driver:

- [ ] Open dashboard at http://localhost:3001
- [ ] Upload DASH PDF for Driver 1
  - [ ] Check: Name shows on right
  - [ ] Check: Policy info shows on right
- [ ] Add second driver
  - [ ] Check: "Driver 2" tab appears at top right
  - [ ] Check: New upload section appears on left
- [ ] Upload DASH for Driver 2
  - [ ] Check: Driver 2's data shows on right
- [ ] Click "Driver 1" tab
  - [ ] Check: Driver 1's data shows again (not Driver 2's)
- [ ] Click "Driver 2" tab  
  - [ ] Check: Driver 2's data shows again
- [ ] Upload MVR for Driver 1
  - [ ] Make sure "Driver 1" tab is active first
  - [ ] Check: MVR data (birth date, convictions) shows
  - [ ] Check: G/G1/G2 dates calculated
- [ ] Add a 3rd driver
  - [ ] Check: Can add unlimited drivers
  - [ ] Check: "Driver 3" tab appears
  - [ ] Check: All previous drivers' data preserved

---

## 💡 Pro Tips

1. **Switch drivers often**
   - Click any driver tab anytime
   - No need to re-upload or re-select

2. **Each driver is independent**
   - Driver 1's MVR upload doesn't affect Driver 2
   - Removing Driver 3's file doesn't remove Driver 1's file

3. **Add as many as you need**
   - No limit on number of drivers
   - Good for family households or multi-driver companies

4. **Copy mode works per driver**
   - Click "Copy Info" tab
   - Copy any field for the currently active driver

5. **One-click switching**
   - Tabs at top right
   - Click = instant switch to that driver's data

---

## ⚙️ Behind the Scenes

When you upload a PDF:
1. Backend parses it
2. Data stored separately per driver
3. If you're viewing that driver → display updates instantly
4. If you're viewing another driver → data saved for later

When you click a driver tab:
1. Preview side fades slightly
2. All display fields clear
3. That driver's data loads from memory
4. Preview side un-fades
5. You see their info!

---

## 🔄 Example Scenario: 3 Drivers

```
Timeline:
─────────
1. Page loads
   └─ "Driver 1" tab shown, empty preview

2. Upload DASH for Driver 1
   └─ Driver 1's info displays

3. Click "Add Another Driver"
   └─ "Driver 2" tab appears, preview cleared

4. Upload DASH for Driver 2  
   └─ Driver 2's info displays

5. Click "Add Another Driver"
   └─ "Driver 3" tab appears, preview cleared

6. Upload DASH for Driver 3
   └─ Driver 3's info displays

7. Click "Driver 1" tab
   └─ Driver 1's original data displays (still saved!)

8. Click "Driver 2" tab
   └─ Driver 2's data displays

9. Upload MVR for Driver 2
   └─ MVR data + G dates calculated for Driver 2

10. Click "Driver 1" tab, then upload MVR for Driver 1
    └─ MVR data + G dates calculated for Driver 1

✓ All 3 drivers processed in one session!
```

---

## 🎓 What's New vs Old

| Feature | Before | After |
|---------|--------|-------|
| Multiple Drivers | ❌ Have to refresh/clear form | ✅ Handle unlimited in one session |
| Switching Drivers | ❌ Not possible | ✅ Click tabs instantly |
| Data per Driver | ❌ Single driver only | ✅ Each has their own storage |
| G/G1/G2 per Driver | ❌ Just 1 driver | ✅ Each driver calculated |
| UI | ❌ Single driver layout | ✅ Multi-tab layout |

---

## 🆘 Troubleshooting

**Q: Added a driver but tab didn't appear?**
- A: Try uploading a PDF first. Tab appears when data is loaded.

**Q: Switched to Driver 2, but see Driver 1's data?**
- A: Page might be caching. Try F5 (refresh) or Ctrl+Shift+R (hard refresh)

**Q: Want to remove a driver?**
- A: Click "Clear All" to reset to just Driver 1 with no data

**Q: Data disappeared after refresh?**
- A: Data is stored in browser memory. Page refresh clears it. Re-upload PDFs.

**Q: Can I upload same PDF to 2 drivers?**
- A: Yes! Just upload it to each driver's section.

---

## 📞 Quick Commands

| Action | How |
|--------|-----|
| Add Driver | Click "Add Another Driver" button |
| View Driver | Click driver tab at top right |
| Remove Driver | Not available - use "Clear All" to reset |
| Clear All | Click "Clear All" button at bottom |
| Copy Field | Click copy icon next to any field |
| Submit Form | Click "Save Quote" button |

---

## ✨ Summary

🎯 **Single Dashboard**  
🚗 **Multiple Drivers**  
🔄 **Tab-Based Switching**  
💾 **Per-Driver Storage**  
⚡ **Instant Display Updates**  
✅ **Ready to Use!**

---

**Start now**: http://localhost:3001

Good luck! 🚀
