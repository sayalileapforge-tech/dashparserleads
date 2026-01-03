-- ============================================================================
-- QUOTES MANAGEMENT SCHEMA
-- Stores all quote data: lead info, parsed PDFs, manual entries, properties
-- ============================================================================

-- ============================================================================
-- QUOTES TABLE - Main quote record
-- ============================================================================
CREATE TABLE IF NOT EXISTS quotes (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Quote unique identifier',
    lead_id INT COMMENT 'Link to lead from Meta',
    lead_name VARCHAR(255) NOT NULL COMMENT 'Lead full name',
    lead_email VARCHAR(255) INDEX COMMENT 'Lead email',
    lead_phone VARCHAR(20) INDEX COMMENT 'Lead phone',
    
    -- Meta Lead Information
    meta_id VARCHAR(255) COMMENT 'Meta CRM lead ID',
    meta_source VARCHAR(100) COMMENT 'Source from Meta (form, api, import)',
    potential_status VARCHAR(100) COMMENT 'Lead potential status (hot, warm, cold, unqualified)',
    premium DECIMAL(10, 2) COMMENT 'Quoted premium amount',
    renewal_date DATE COMMENT 'Policy renewal date',
    
    -- Signal & Status
    signal ENUM('green', 'red') DEFAULT 'red' COMMENT 'Green=qualified, Red=not qualified',
    status ENUM('draft', 'submitted', 'processed') DEFAULT 'draft' COMMENT 'Quote status',
    
    -- Entry Mode
    entry_mode ENUM('auto', 'property', 'manual') COMMENT 'Type of entry: auto/property/manual',
    
    -- Manual Vehicle Entry (if no PDF)
    ownership VARCHAR(50) COMMENT 'Owned/Financed/Leased',
    vehicle_use VARCHAR(50) COMMENT 'Pleasure/Commute/Business',
    annual_km INT COMMENT 'Annual kilometers',
    winter_tires BOOLEAN COMMENT 'Has winter tires',
    anti_theft BOOLEAN COMMENT 'Has anti-theft device',
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_lead_id (lead_id),
    INDEX idx_signal (signal),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Main quotes table';

-- ============================================================================
-- QUOTE_DRIVERS TABLE - Driver details per quote (supports multiple drivers)
-- ============================================================================
CREATE TABLE IF NOT EXISTS quote_drivers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quote_id INT NOT NULL COMMENT 'Reference to quotes table',
    driver_number INT NOT NULL COMMENT 'Driver number (1, 2, 3...)',
    relationship VARCHAR(50) COMMENT 'Applicant/Spouse/Son/Daughter/Parent/Sibling/Other',
    
    -- DASH Data (Insurance History)
    dash_name VARCHAR(255) COMMENT 'Driver name from DASH',
    dash_dln VARCHAR(50) COMMENT 'Driver License Number',
    dash_dob DATE COMMENT 'Date of birth',
    dash_gender CHAR(1) COMMENT 'M/F',
    dash_marital_status VARCHAR(50) COMMENT 'Marital status from DASH',
    dash_address TEXT COMMENT 'Address from DASH',
    dash_years_licensed INT COMMENT 'Years licensed',
    dash_years_continuous_insurance INT COMMENT 'Continuous insurance years',
    dash_years_claims_free INT COMMENT 'Claims-free years',
    
    -- DASH History (3y/6y)
    dash_nonpay_3y INT COMMENT 'Non-pay incidents (3 years)',
    dash_claims_6y INT COMMENT 'Claims (6 years)',
    dash_first_party_6y INT COMMENT 'First party claims (6 years)',
    dash_dcpd_6y INT COMMENT 'DCPD incidents (6 years)',
    
    -- DASH Current Policy
    dash_current_company VARCHAR(255) COMMENT 'Current insurance company',
    dash_current_policy_expiry DATE COMMENT 'Current policy expiry date',
    dash_current_vehicles_count INT COMMENT 'Number of vehicles on policy',
    dash_current_operators_count INT COMMENT 'Number of operators on policy',
    dash_first_insurance_date DATE COMMENT 'First insurance date (for G calculation)',
    
    -- MVR Data (Motor Vehicle Record)
    mvr_birth_date DATE COMMENT 'Birth date from MVR',
    mvr_licence_expiry_date DATE COMMENT 'License expiry from MVR',
    mvr_convictions_count INT COMMENT 'Number of convictions',
    mvr_convictions JSON COMMENT 'Convictions details (JSON)',
    mvr_issue_date DATE COMMENT 'License issue date',
    
    -- Calculated G Dates (from combination)
    g_date DATE COMMENT 'G rate date (calculated)',
    g1_date DATE COMMENT 'G1 rate date (calculated)',
    g2_date DATE COMMENT 'G2 rate date (calculated)',
    insufficient_experience BOOLEAN COMMENT 'Customer has <5 years experience',
    
    -- Full DASH/MVR JSON backup
    dash_json LONGTEXT COMMENT 'Complete DASH parsed data (JSON)',
    mvr_json LONGTEXT COMMENT 'Complete MVR parsed data (JSON)',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
    INDEX idx_quote_id (quote_id),
    INDEX idx_driver_number (driver_number),
    INDEX idx_dash_dln (dash_dln),
    INDEX idx_mvr_birth_date (mvr_birth_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Driver-specific data for each quote';

-- ============================================================================
-- QUOTE_PROPERTIES TABLE - Property data (for property mode quotes)
-- ============================================================================
CREATE TABLE IF NOT EXISTS quote_properties (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quote_id INT NOT NULL COMMENT 'Reference to quotes table',
    property_number INT COMMENT 'Property number (1, 2, 3...)',
    
    -- Location
    property_address VARCHAR(255),
    property_city VARCHAR(255),
    property_postal VARCHAR(20),
    
    -- Property Basics
    property_type VARCHAR(100) COMMENT 'Primary/Secondary-Rented/Vacation/etc',
    year_built INT,
    storeys INT,
    units INT,
    families INT,
    year_purchased INT,
    
    -- Occupancy
    owner_occupied BOOLEAN,
    inlaw_suite BOOLEAN,
    basement_apartment BOOLEAN,
    
    -- Area
    living_area_sqft INT,
    basement_area_sqft INT,
    basement_finished_percent INT,
    
    -- Systems
    electrical VARCHAR(100),
    plumbing VARCHAR(100),
    roofing VARCHAR(100),
    heating VARCHAR(100),
    full_baths INT,
    half_baths INT,
    
    -- Security
    burglar_alarm BOOLEAN,
    fire_alarm BOOLEAN,
    sprinkler_system BOOLEAN,
    smoke_detectors INT,
    fire_extinguishers INT,
    block_watch BOOLEAN,
    walled BOOLEAN,
    deadbolts BOOLEAN,
    
    -- Property JSON backup
    property_json LONGTEXT COMMENT 'Complete property data (JSON)',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
    INDEX idx_quote_id (quote_id),
    INDEX idx_property_type (property_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Property details for quotes';

-- ============================================================================
-- Indexes for Performance
-- ============================================================================
CREATE INDEX idx_quotes_lead_id ON quotes(lead_id);
CREATE INDEX idx_quotes_signal ON quotes(signal);
CREATE INDEX idx_quotes_status ON quotes(status);
CREATE INDEX idx_quotes_created_at ON quotes(created_at);
CREATE INDEX idx_quote_drivers_quote_id ON quote_drivers(quote_id);
CREATE INDEX idx_quote_properties_quote_id ON quote_properties(quote_id);
