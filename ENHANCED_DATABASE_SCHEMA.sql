-- =====================================================
-- ENHANCED INSURANCE DASHBOARD - COMPLETE DATA PERSISTENCE
-- Stores Meta Leads + Parsed PDF Data (MVR/DASH) + Manual Entry
-- =====================================================

CREATE DATABASE IF NOT EXISTS insurance_dashboard;
USE insurance_dashboard;

-- Drop existing tables if upgrading (optional)
-- DROP TABLE IF EXISTS quote_documents;
-- DROP TABLE IF EXISTS quote_driver_data;
-- DROP TABLE IF EXISTS parsed_pdf_data;
-- DROP TABLE IF EXISTS lead_quotes;
-- DROP TABLE IF EXISTS meta_leads;

-- =====================================================
-- 1. META LEADS TABLE (Primary Lead Information)
-- =====================================================
CREATE TABLE IF NOT EXISTS meta_leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meta_lead_id VARCHAR(100) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('new', 'contacted', 'qualified', 'converted', 'lost') DEFAULT 'new',
    source VARCHAR(100) DEFAULT 'Meta Lead Ads',
    notes TEXT,
    
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Master Meta Leads table - stores all real leads from Facebook';

-- =====================================================
-- 2. PARSED PDF DATA TABLE (MVR + DASH Extraction Results)
-- =====================================================
CREATE TABLE IF NOT EXISTS parsed_pdf_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT,  -- Links to meta_leads
    
    -- Document Metadata
    pdf_upload_id VARCHAR(100) UNIQUE,
    document_type ENUM('MVR', 'DASH', 'AUTO+', 'OTHER') NOT NULL,
    original_filename VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ▶ PERSONAL INFORMATION (from PDF)
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender ENUM('M', 'F', 'Other'),
    marital_status VARCHAR(100),
    address VARCHAR(500),
    
    -- ▶ LICENSE/DRIVER INFORMATION (from PDF)
    license_number VARCHAR(50),
    license_class VARCHAR(10),
    license_issue_date DATE,
    license_expiry_date DATE,
    years_licensed INT,
    license_status VARCHAR(100),
    
    -- ▶ INSURANCE HISTORY (from PDF)
    first_insurance_date DATE,
    years_continuous_insurance INT,
    years_claims_free INT,
    current_insurance_company VARCHAR(255),
    current_policy_number VARCHAR(100),
    current_policy_expiry DATE,
    
    -- ▶ CLAIMS HISTORY (from PDF - Last 6 Years)
    total_claims_6y INT,
    at_fault_claims_6y INT,
    first_party_claims_6y INT,
    comprehensive_claims_6y INT,
    dcpd_claims_6y INT,
    
    -- ▶ POLICY DETAILS (from PDF)
    current_operators_count INT,
    current_vehicles_count INT,
    
    -- ▶ G/G1/G2 DATES (Calculated from issue & first_insurance dates)
    g_date DATE,
    g2_date DATE,
    g1_date DATE,
    g_calculation_status VARCHAR(50),
    g_calculation_error TEXT,
    
    -- ▶ ADDITIONAL FIELDS (from DASH)
    driver_training VARCHAR(255),
    
    -- Metadata
    parse_success BOOLEAN DEFAULT TRUE,
    parse_errors JSON,
    raw_extracted_data JSON,  -- Store complete JSON if needed for recovery
    
    FOREIGN KEY (lead_id) REFERENCES meta_leads(id) ON DELETE SET NULL,
    INDEX idx_lead_id (lead_id),
    INDEX idx_document_type (document_type),
    INDEX idx_uploaded_at (uploaded_at),
    INDEX idx_license_number (license_number),
    UNIQUE KEY unique_upload_per_lead (lead_id, pdf_upload_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Extracted data from parsed PDFs (MVR, DASH) - all driver fields stored systematically';

-- =====================================================
-- 3. MANUAL ENTRY DATA TABLE (Manually Entered Information)
-- =====================================================
CREATE TABLE IF NOT EXISTS manual_entry_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    parsed_pdf_id INT,  -- Optional: linked parsed data
    
    -- ▶ MANUAL DRIVER INFORMATION
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender ENUM('M', 'F', 'Other'),
    marital_status VARCHAR(100),
    address VARCHAR(500),
    
    -- ▶ MANUAL LICENSE INFORMATION
    license_number VARCHAR(50),
    license_class VARCHAR(10),
    license_issue_date DATE,
    license_expiry_date DATE,
    
    -- ▶ MANUAL INSURANCE HISTORY
    first_insurance_date DATE,
    years_continuous_insurance INT,
    years_claims_free INT,
    
    -- ▶ CLAIMS MANUALLY ENTERED
    total_claims_6y INT,
    at_fault_claims_6y INT,
    first_party_claims_6y INT,
    comprehensive_claims_6y INT,
    dcpd_claims_6y INT,
    
    -- ▶ CURRENT POLICY DETAILS
    current_company VARCHAR(255),
    current_policy_number VARCHAR(100),
    current_policy_expiry DATE,
    current_operators_count INT,
    current_vehicles_count INT,
    
    -- ▶ G/G1/G2 DATES (Calculated from manual dates)
    g_date DATE,
    g2_date DATE,
    g1_date DATE,
    g_calculation_status VARCHAR(50),
    
    -- Metadata
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entered_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lead_id) REFERENCES meta_leads(id) ON DELETE CASCADE,
    FOREIGN KEY (parsed_pdf_id) REFERENCES parsed_pdf_data(id) ON DELETE SET NULL,
    INDEX idx_lead_id (lead_id),
    INDEX idx_parsed_pdf_id (parsed_pdf_id),
    INDEX idx_entered_at (entered_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Manually entered driver/insurance information for leads without PDFs or additional data';

-- =====================================================
-- 4. PROPERTY DETAILS TABLE (Home/Property Information)
-- =====================================================
CREATE TABLE IF NOT EXISTS property_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    
    -- ▶ PROPERTY INFORMATION
    property_type VARCHAR(100),
    address VARCHAR(500),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    province VARCHAR(50),
    year_built INT,
    square_footage INT,
    number_of_storeys INT,
    number_of_units INT,
    
    -- ▶ OWNERSHIP DETAILS
    owner_occupied BOOLEAN DEFAULT TRUE,
    purchased_date DATE,
    first_insured_year INT,
    
    -- ▶ MORTGAGE INFORMATION
    has_mortgage BOOLEAN DEFAULT FALSE,
    lender_name VARCHAR(255),
    
    -- ▶ HOME FEATURES
    full_bathrooms INT,
    half_bathrooms INT,
    bedrooms INT,
    
    -- ▶ SECURITY FEATURES
    has_burglar_alarm BOOLEAN DEFAULT FALSE,
    has_fire_alarm BOOLEAN DEFAULT FALSE,
    has_sprinkler_system BOOLEAN DEFAULT FALSE,
    has_deadbolts BOOLEAN DEFAULT FALSE,
    
    -- ▶ HOME SYSTEMS
    electrical_status VARCHAR(100),
    plumbing_status VARCHAR(100),
    roofing_status VARCHAR(100),
    heating_status VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lead_id) REFERENCES meta_leads(id) ON DELETE CASCADE,
    INDEX idx_lead_id (lead_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Property/home information for property insurance quotes';

-- =====================================================
-- 5. VEHICLE DETAILS TABLE (Vehicle Information)
-- =====================================================
CREATE TABLE IF NOT EXISTS vehicle_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    vehicle_sequence INT DEFAULT 1,
    
    -- ▶ VEHICLE INFORMATION
    year INT,
    make VARCHAR(100),
    model VARCHAR(100),
    body_type VARCHAR(50),
    vin VARCHAR(50),
    license_plate VARCHAR(20),
    
    -- ▶ VEHICLE USAGE
    annual_km INT,
    vehicle_use ENUM('pleasure', 'commute', 'business') DEFAULT 'pleasure',
    ownership_type ENUM('owned', 'financed', 'leased') DEFAULT 'owned',
    
    -- ▶ VEHICLE PROTECTION
    winter_tires BOOLEAN DEFAULT FALSE,
    anti_theft_device BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lead_id) REFERENCES meta_leads(id) ON DELETE CASCADE,
    INDEX idx_lead_id (lead_id),
    UNIQUE KEY unique_vehicle_per_lead (lead_id, vehicle_sequence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Vehicle details for auto insurance quotes';

-- =====================================================
-- 6. COMPLETE QUOTE SUMMARY TABLE (Master Record)
-- =====================================================
CREATE TABLE IF NOT EXISTS complete_quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL UNIQUE,
    
    -- ▶ QUOTE METADATA
    quote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quote_type ENUM('auto', 'property', 'combined') DEFAULT 'auto',
    quote_status ENUM('draft', 'submitted', 'quoted', 'converted') DEFAULT 'draft',
    
    -- ▶ AUTO INSURANCE SECTION
    auto_premium_estimated DECIMAL(10, 2),
    auto_coverage_selected VARCHAR(255),
    auto_deductible INT,
    
    -- ▶ PROPERTY INSURANCE SECTION
    home_premium_estimated DECIMAL(10, 2),
    home_coverage_selected VARCHAR(255),
    home_deductible INT,
    
    -- ▶ DOCUMENT REFERENCES
    parsed_pdf_id INT,  -- Link to parsed_pdf_data
    manual_entry_id INT,  -- Link to manual_entry_data
    property_id INT,  -- Link to property_details
    
    -- ▶ ADDITIONAL DATA
    notes TEXT,
    follow_up_date DATE,
    assigned_agent VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lead_id) REFERENCES meta_leads(id) ON DELETE CASCADE,
    FOREIGN KEY (parsed_pdf_id) REFERENCES parsed_pdf_data(id) ON DELETE SET NULL,
    FOREIGN KEY (manual_entry_id) REFERENCES manual_entry_data(id) ON DELETE SET NULL,
    FOREIGN KEY (property_id) REFERENCES property_details(id) ON DELETE SET NULL,
    INDEX idx_lead_id (lead_id),
    INDEX idx_quote_date (quote_date),
    INDEX idx_quote_status (quote_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Master quote summary - links all data for a lead';

-- =====================================================
-- 7. AUDIT LOG TABLE (Track All Changes)
-- =====================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT,
    action_type VARCHAR(50),  -- 'created', 'updated', 'pdf_parsed', 'manual_entered', 'quote_generated'
    table_name VARCHAR(100),
    record_id INT,
    old_data JSON,
    new_data JSON,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lead_id) REFERENCES meta_leads(id) ON DELETE SET NULL,
    INDEX idx_lead_id (lead_id),
    INDEX idx_action_type (action_type),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Complete audit trail of all changes to lead and quote data';

-- =====================================================
-- 8. CLAIMS HISTORY TABLE (Detailed Claims Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS claims_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    source_table ENUM('parsed_pdf_data', 'manual_entry_data') NOT NULL,
    source_id INT,  -- ID from parsed_pdf_data or manual_entry_data
    
    claim_date DATE,
    claim_type ENUM('at_fault', 'first_party', 'comprehensive', 'dcpd', 'other') NOT NULL,
    amount DECIMAL(10, 2),
    description TEXT,
    status VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lead_id) REFERENCES meta_leads(id) ON DELETE CASCADE,
    INDEX idx_lead_id (lead_id),
    INDEX idx_claim_date (claim_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Detailed claims history for each lead';

-- =====================================================
-- INDEXES FOR COMMON QUERIES
-- =====================================================
CREATE INDEX idx_lead_status_date ON meta_leads(status, created_at);
CREATE INDEX idx_pdf_type_date ON parsed_pdf_data(document_type, parsed_at);
CREATE INDEX idx_quote_lead_date ON complete_quotes(lead_id, quote_date);

-- =====================================================
-- VIEWS FOR EASY DATA ACCESS
-- =====================================================

-- View: Complete Lead Profile
CREATE OR REPLACE VIEW vw_lead_profile AS
SELECT 
    ml.id as lead_id,
    ml.full_name,
    ml.email,
    ml.phone,
    ml.status,
    ml.created_at,
    ppd.id as parsed_pdf_id,
    ppd.document_type,
    ppd.full_name as pdf_name,
    ppd.license_number,
    ppd.g_date,
    ppd.g2_date,
    ppd.g1_date,
    med.id as manual_entry_id,
    med.full_name as manual_name,
    cq.id as quote_id,
    cq.quote_status,
    cq.quote_date
FROM meta_leads ml
LEFT JOIN parsed_pdf_data ppd ON ml.id = ppd.lead_id
LEFT JOIN manual_entry_data med ON ml.id = med.lead_id
LEFT JOIN complete_quotes cq ON ml.id = cq.lead_id;

-- View: Auto Quote Summary
CREATE OR REPLACE VIEW vw_auto_quote_summary AS
SELECT 
    ml.full_name,
    ml.email,
    ml.phone,
    ml.status,
    ppd.license_number,
    ppd.g_date,
    ppd.g2_date,
    ppd.g1_date,
    ppd.years_continuous_insurance,
    ppd.years_claims_free,
    vd.year as vehicle_year,
    vd.make,
    vd.model,
    cq.auto_premium_estimated,
    cq.quote_status,
    cq.quote_date
FROM meta_leads ml
LEFT JOIN parsed_pdf_data ppd ON ml.id = ppd.lead_id
LEFT JOIN vehicle_details vd ON ml.id = vd.lead_id
LEFT JOIN complete_quotes cq ON ml.id = cq.lead_id;

-- View: All Lead Data (Consolidated)
CREATE OR REPLACE VIEW vw_all_lead_data AS
SELECT 
    ml.id,
    ml.full_name as lead_name,
    ml.email,
    ml.phone,
    ml.status,
    COALESCE(ppd.full_name, med.full_name) as driver_name,
    COALESCE(ppd.license_number, med.license_number) as license_number,
    COALESCE(ppd.g_date, med.g_date) as g_date,
    COALESCE(ppd.g2_date, med.g2_date) as g2_date,
    COALESCE(ppd.g1_date, med.g1_date) as g1_date,
    COALESCE(ppd.years_continuous_insurance, med.years_continuous_insurance) as continuous_insurance,
    COALESCE(ppd.current_insurance_company, med.current_company) as insurance_company,
    pd.property_type,
    pd.address as property_address,
    vd.make,
    vd.model,
    cq.quote_status,
    cq.quote_date,
    ml.created_at
FROM meta_leads ml
LEFT JOIN parsed_pdf_data ppd ON ml.id = ppd.lead_id
LEFT JOIN manual_entry_data med ON ml.id = med.lead_id
LEFT JOIN property_details pd ON ml.id = pd.lead_id
LEFT JOIN vehicle_details vd ON ml.id = vd.lead_id
LEFT JOIN complete_quotes cq ON ml.id = cq.lead_id;

-- =====================================================
-- INSERT SAMPLE DATA (For Testing)
-- =====================================================
INSERT INTO meta_leads (full_name, first_name, last_name, email, phone, status, source) 
VALUES 
('Anchit Parveen Gupta', 'Anchit', 'Gupta', 'gupta.anchit407@gmail.com', '(416) 555-0101', 'new', 'Meta Lead Ads'),
('Zahra Abuzar', 'Zahra', 'Abuzar', 'zebraabuzar788@gmail.com', '(647) 555-0202', 'contacted', 'Meta Lead Ads'),
('Nallely Prado Castro', 'Nallely', 'Castro', 'nallely@email.com', '(905) 555-0303', 'qualified', 'Meta Lead Ads');
