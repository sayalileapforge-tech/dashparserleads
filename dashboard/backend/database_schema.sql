-- ============================================================================
-- INSURANCE LEADS DATABASE SCHEMA
-- Database: insurance_leads
-- Created: 2025-12-28
-- Purpose: Central repository for all leads from Meta Lead Ads
-- ============================================================================

-- ============================================================================
-- LEADS TABLE - Main table storing all lead information
-- ============================================================================
CREATE TABLE IF NOT EXISTS leads (
    -- Primary Key
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each lead',

    -- Facebook/Meta Fields
    meta_lead_id VARCHAR(255) NOT NULL UNIQUE INDEX COMMENT 'Unique identifier from Meta API',
    lead_form_id VARCHAR(255) COMMENT 'Form ID from Meta',
    source VARCHAR(50) DEFAULT 'facebook' INDEX COMMENT 'Lead source (always facebook)',

    -- Contact Information
    first_name VARCHAR(255) COMMENT 'Lead first name',
    last_name VARCHAR(255) COMMENT 'Lead last name',
    full_name VARCHAR(255) INDEX COMMENT 'Full name of the lead',
    email VARCHAR(255) INDEX COMMENT 'Email address',
    phone VARCHAR(20) INDEX COMMENT 'Phone number',

    -- Additional Information
    company_name VARCHAR(255) COMMENT 'Company name',
    job_title VARCHAR(255) COMMENT 'Job title',

    -- Location
    city VARCHAR(255) COMMENT 'City',
    state VARCHAR(2) COMMENT 'State code (2 letters)',
    country VARCHAR(255) COMMENT 'Country name',
    zip_code VARCHAR(20) COMMENT 'Postal code',

    -- Lead Processing & Status
    status ENUM(
        'new',
        'processing',
        'processed',
        'contacted',
        'quote_sent',
        'closed_won',
        'closed_lost',
        'no_answer'
    ) DEFAULT 'new' INDEX COMMENT 'Current processing status',
    notes LONGTEXT COMMENT 'Internal notes about the lead',

    -- Event Manager Signal (Conversions API)
    signal ENUM('green', 'red') DEFAULT 'red' INDEX COMMENT 'Signal for Meta Event Manager: green=qualified, red=not qualified',

    -- Insurance Premiums (in cents)
    auto_premium INT COMMENT 'Auto insurance premium (in cents)',
    home_premium INT COMMENT 'Home insurance premium (in cents)',
    tenant_premium INT COMMENT 'Tenant insurance premium (in cents)',

    -- Meta API Data
    custom_form_fields JSON COMMENT 'Custom fields from Meta form (JSON)',
    raw_payload LONGTEXT COMMENT 'Complete raw payload from Meta API',

    -- Timestamps
    meta_created_at DATETIME COMMENT 'Timestamp when lead was created in Meta system',
    synced_at DATETIME COMMENT 'Timestamp when lead was synced from Meta',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'When record was created in our system',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'When record was last updated'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Central repository for all leads from Meta Lead Ads';

-- ============================================================================
-- TABLE INDEXES for Performance
-- ============================================================================
CREATE INDEX idx_meta_lead_id ON leads(meta_lead_id);
CREATE INDEX idx_status ON leads(status);
CREATE INDEX idx_signal ON leads(signal);
CREATE INDEX idx_email ON leads(email);
CREATE INDEX idx_phone ON leads(phone);
CREATE INDEX idx_full_name ON leads(full_name);
CREATE INDEX idx_source ON leads(source);
CREATE INDEX idx_created_at ON leads(created_at);
CREATE INDEX idx_updated_at ON leads(updated_at);
CREATE INDEX idx_synced_at ON leads(synced_at);

-- ============================================================================
-- SAMPLE DATA (for demonstration)
-- ============================================================================
-- Insert sample leads to show database structure
INSERT INTO leads (
    meta_lead_id, lead_form_id, source, first_name, last_name, full_name, 
    email, phone, company_name, city, state, country, zip_code, status, signal,
    auto_premium, home_premium, notes, synced_at, created_at
) VALUES
(
    'META_12345', 'FORM_001', 'facebook', 'John', 'Doe', 'John Doe',
    'john@example.com', '+1-555-123-4567', 'ABC Corp', 'New York', 'NY', 'USA', '10001',
    'new', 'red', 50000, 35000, 'Sample lead - awaiting contact', NOW(), NOW()
),
(
    'META_12346', 'FORM_001', 'facebook', 'Jane', 'Smith', 'Jane Smith',
    'jane@example.com', '+1-555-987-6543', 'XYZ Inc', 'Los Angeles', 'CA', 'USA', '90001',
    'processing', 'green', 45000, NULL, 'Qualified lead for Event Manager', NOW(), NOW()
),
(
    'META_12347', 'FORM_001', 'facebook', 'Robert', 'Johnson', 'Robert Johnson',
    'robert@example.com', '+1-555-456-7890', 'Tech Solutions', 'Chicago', 'IL', 'USA', '60601',
    'processed', 'green', 55000, 42000, 'Successfully processed and sent to Event Manager', NOW(), NOW()
);

-- ============================================================================
-- DATABASE STATISTICS VIEWS
-- ============================================================================
SELECT '=== DATABASE SCHEMA SUMMARY ===' as info;
SELECT 'Table: leads' as table_name, COUNT(*) as total_records FROM leads;
SELECT signal, COUNT(*) as count FROM leads GROUP BY signal;
SELECT status, COUNT(*) as count FROM leads GROUP BY status;
SELECT 'Total Leads' as metric, COUNT(*) as value FROM leads;
SELECT 'Green Signal (Qualified)' as metric, COUNT(*) as value FROM leads WHERE signal = 'green';
SELECT 'Red Signal (Not Qualified)' as metric, COUNT(*) as value FROM leads WHERE signal = 'red';
