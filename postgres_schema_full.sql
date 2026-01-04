-- Comprehensive PostgreSQL schema for insurance dashboard

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    meta_lead_id VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    status VARCHAR(50),
    potential_status VARCHAR(100),
    premium NUMERIC(10,2),
    signal VARCHAR(100),
    renewal_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dash_reports (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    raw_pdf_data TEXT,
    parsed_data JSONB,
    extracted_fields JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mvr_reports (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    raw_pdf_data TEXT,
    parsed_data JSONB,
    g_date DATE,
    g1_date DATE,
    g2_date DATE,
    total_months INTEGER,
    experience_warning TEXT,
    calculation_performed BOOLEAN,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    quote_type VARCHAR(50),
    quote_status VARCHAR(50),
    entry_mode VARCHAR(20),
    premium NUMERIC(10,2),
    renewal_date DATE,
    signal VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS property_entries (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    property_type VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    year_built INTEGER,
    storeys INTEGER,
    units INTEGER,
    families INTEGER,
    year_purchased INTEGER,
    owner_occupied BOOLEAN,
    inlaw_suite BOOLEAN,
    basement_apartment BOOLEAN,
    living_area_sqft INTEGER,
    basement_area_sqft INTEGER,
    basement_finished_percent INTEGER,
    electrical VARCHAR(100),
    plumbing VARCHAR(100),
    roofing VARCHAR(100),
    heating VARCHAR(100),
    full_baths INTEGER,
    half_baths INTEGER,
    burglar_alarm BOOLEAN,
    fire_alarm BOOLEAN,
    sprinkler_system BOOLEAN,
    smoke_detectors INTEGER,
    fire_extinguishers INTEGER,
    block_watch BOOLEAN,
    walled BOOLEAN,
    deadbolts BOOLEAN,
    property_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Manual entry for quotes (auto/manual)
CREATE TABLE IF NOT EXISTS manual_entry_quotes (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
