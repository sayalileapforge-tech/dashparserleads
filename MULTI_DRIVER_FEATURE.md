# Multi-Driver Support - Complete Guide

## ✅ Feature Overview

The dashboard now supports multiple drivers! Each driver can have their own DASH and MVR PDFs uploaded, and their data is displayed individually when viewing that driver's page.

## 🎯 How It Works

### 1. **Adding a New Driver**
- Click the **"Add Another Driver"** button in the left panel
- A new driver section will appear below Driver 1
- A new driver tab will automatically appear in the **Driver Pages Navigation** section (top right)

### 2. **Uploading Driver Documents**
Each driver has their own upload area with:
- **DASH** - Default document type (click to select and upload)
- **Auto+** - Alternative document type
- **MVR** - Motor Vehicle Record
- **Relationship** - Select relationship (Applicant, Spouse, Son, Daughter, Parent, Sibling, Other)

### 3. **Viewing Driver Data**
Click on any driver tab at the top (e.g., "Driver 1", "Driver 2", etc.) to see that driver's parsed information on the right preview panel:

#### **DASH Data Shown:**
- Driver name and DLN
- Demographics (Gender, Marital Status, Years Licensed, Claims-Free)
- Address
- History (Non-Pay, Claims, 1st Party, Gaps)
- Current Policy (Company, Expiry Date)
- Vehicles & Operators counts

#### **MVR Data Shown:**
- Birth Date
- License Expiry Date
- Years of Experience
- Convictions Count & Details

#### **Combination Data (G/G1/G2):**
- Calculated insurance dates when both DASH and MVR are uploaded
- Shows "Customer has less than 5 years of experience" if applicable

## 📋 Data Management

### Per-Driver Storage
- **`parsedDASHData`** - Stores DASH data for each driver (indexed by driver number)
- **`parsedMVRData`** - Stores MVR data for each driver (indexed by driver number)
- **`currentDisplayDriver`** - Tracks which driver's data is currently being displayed

### Selective Data Clearing
When you upload a new file:
- Only that document type for that driver is cleared
- Other drivers' data is preserved
- The same driver's other document type is preserved

**Example:**
- Upload DASH for Driver 2 → Only Driver 2's old DASH is cleared
- Driver 1's data remains unchanged
- Driver 2's MVR (if any) remains unchanged

## 🔄 Workflow Example

### Scenario: Processing 3 Drivers from a household

1. **Driver 1 (Applicant)**
   - Click "Driver 1" tab (selected by default)
   - Upload DASH PDF → Data displays on right
   - Upload MVR PDF → Combined G/G1/G2 dates calculated
   - View all info in preview panel

2. **Driver 2 (Spouse)**
   - Click "Add Another Driver"
   - New "Driver 2" tab appears
   - Select "Spouse" in relationship
   - Upload DASH PDF for Driver 2 → Their data displays
   - Upload MVR PDF for Driver 2 → Their combined data displays
   - Driver 1's data remains intact

3. **Driver 3 (Son)**
   - Click "Add Another Driver"
   - New "Driver 3" tab appears
   - Select "Son" in relationship
   - Upload documents → Data displays
   - Can switch between all 3 drivers' tabs anytime

## 🎨 Visual Indicators

### Driver Tabs
- **Active Tab**: Blue background with white text
- **Inactive Tabs**: Gray background, clickable
- **Hover State**: Subtle color change

### Document Pills
- **Active**: Dark/Selected document type is highlighted
- **Uploaded**: Green background when file is selected
- **Remove**: X button appears to delete uploaded file

## ⚙️ Technical Details

### Key Functions

**`addDriver()`**
- Increments driver count
- Creates new driver HTML section
- Adds new tab button to navigation
- Auto-switches to new driver view

**`switchDriverPage(driverNum)`**
- Updates button styles (active/inactive)
- Sets `currentDisplayDriver` tracking variable
- Calls `switchDriverView()` to display data

**`switchDriverView(driverNum)`**
- Clears all display fields
- Fetches DASH data from `parsedDASHData[driverNum]`
- Fetches MVR data from `parsedMVRData[driverNum]`
- Populates all preview panel fields
- Calculates and displays expiry dates, experience, etc.

**`clearDriverDisplay()`**
- Resets all preview fields to "—"
- Used before switching drivers to avoid leftover data

### Event Flow

1. User clicks Driver tab
   ↓
2. `switchDriverPage(driverNum)` called
   ↓
3. Button styles updated, `currentDisplayDriver` set
   ↓
4. `switchDriverView(driverNum)` called
   ↓
5. Display fields cleared
   ↓
6. Driver's stored data retrieved and displayed

When PDF is uploaded:
1. PDF parsed by backend
   ↓
2. Data stored in `parsedDASHData[driverNum]` or `parsedMVRData[driverNum]`
   ↓
3. If `currentDisplayDriver === driverNum`, display automatically updates
   ↓
4. Combination dates calculated if both documents available

## 🔍 Copy Mode Features

When in the "Copy Info" tab (second tab), you can copy parsed data fields:
- Click the copy icon next to any field
- Data is copied to clipboard
- Works for all drivers' data

## ✨ Features Working Across Multiple Drivers

✅ Independent DASH/MVR uploads per driver
✅ Separate data storage per driver
✅ Tab-based navigation between drivers
✅ Automatic data display on tab switch
✅ G/G1/G2 calculation per driver
✅ Birth date validation per driver
✅ Expired policy indication per driver
✅ Leads sorted by recency (not driver-specific)

## 💡 Tips

- **Switch drivers anytime**: Click any driver tab to view their data
- **Add drivers as needed**: No limit on driver count
- **Re-upload documents**: Upload new PDF replaces old for same driver
- **Keep data**: When removing drivers, their data clears only when form is "Clear All"
- **Automatic switching**: New drivers automatically display when created
- **Form submission**: Submit button saves all entered data for the quote

## 🐛 Troubleshooting

**Data not showing for a driver?**
- Check that PDF upload was successful (look for success message)
- Verify you're viewing the correct driver tab
- Try re-uploading the PDF

**Data from wrong driver showing?**
- Make sure you clicked the correct driver tab
- Clear browser cache if issues persist

**Added driver but no tab appeared?**
- Refresh the page
- Check browser console for errors

---

**Version**: 2.9+ (Multi-Driver Edition)
**Last Updated**: January 2, 2026
