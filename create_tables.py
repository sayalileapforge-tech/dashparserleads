"""Create all quotes database tables"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root@123', database='insurance_leads')
cursor = conn.cursor()

# Table 1: quotes
cursor.execute('''
CREATE TABLE IF NOT EXISTS quotes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    lead_id INT,
    lead_name VARCHAR(255) NOT NULL,
    lead_email VARCHAR(255),
    lead_phone VARCHAR(20),
    meta_id VARCHAR(255),
    meta_source VARCHAR(100),
    potential_status VARCHAR(100),
    premium DECIMAL(10, 2),
    renewal_date DATE,
    `signal` VARCHAR(20) DEFAULT 'red',
    `status` VARCHAR(50) DEFAULT 'draft',
    entry_mode VARCHAR(50),
    ownership VARCHAR(50),
    vehicle_use VARCHAR(50),
    annual_km INT,
    winter_tires BOOLEAN,
    anti_theft BOOLEAN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_lead_id (lead_id),
    INDEX idx_signal (`signal`),
    INDEX idx_status (`status`),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
''')
print("✓ Table: quotes")

# Table 2: quote_drivers  
cursor.execute('''
CREATE TABLE IF NOT EXISTS quote_drivers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quote_id INT NOT NULL,
    driver_number INT NOT NULL,
    relationship VARCHAR(50),
    dash_name VARCHAR(255),
    dash_dln VARCHAR(50),
    dash_dob DATE,
    dash_gender CHAR(1),
    dash_marital_status VARCHAR(50),
    dash_address TEXT,
    dash_years_licensed INT,
    dash_years_continuous_insurance INT,
    dash_years_claims_free INT,
    dash_nonpay_3y INT,
    dash_claims_6y INT,
    dash_first_party_6y INT,
    dash_dcpd_6y INT,
    dash_current_company VARCHAR(255),
    dash_current_policy_expiry DATE,
    dash_current_vehicles_count INT,
    dash_current_operators_count INT,
    dash_first_insurance_date DATE,
    mvr_birth_date DATE,
    mvr_licence_expiry_date DATE,
    mvr_convictions_count INT,
    mvr_convictions JSON,
    mvr_issue_date DATE,
    g_date DATE,
    g1_date DATE,
    g2_date DATE,
    insufficient_experience BOOLEAN,
    dash_json LONGTEXT,
    mvr_json LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
    INDEX idx_quote_id (quote_id),
    INDEX idx_driver_number (driver_number),
    INDEX idx_dash_dln (dash_dln),
    INDEX idx_mvr_birth_date (mvr_birth_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
''')
print("✓ Table: quote_drivers")

# Table 3: quote_properties
cursor.execute('''
CREATE TABLE IF NOT EXISTS quote_properties (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quote_id INT NOT NULL,
    property_number INT,
    property_address VARCHAR(255),
    property_city VARCHAR(255),
    property_postal VARCHAR(20),
    property_type VARCHAR(100),
    year_built INT,
    storeys INT,
    units INT,
    families INT,
    year_purchased INT,
    owner_occupied BOOLEAN,
    inlaw_suite BOOLEAN,
    basement_apartment BOOLEAN,
    living_area_sqft INT,
    basement_area_sqft INT,
    basement_finished_percent INT,
    electrical VARCHAR(100),
    plumbing VARCHAR(100),
    roofing VARCHAR(100),
    heating VARCHAR(100),
    full_baths INT,
    half_baths INT,
    burglar_alarm BOOLEAN,
    fire_alarm BOOLEAN,
    sprinkler_system BOOLEAN,
    smoke_detectors INT,
    fire_extinguishers INT,
    block_watch BOOLEAN,
    walled BOOLEAN,
    deadbolts BOOLEAN,
    property_json LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
    INDEX idx_quote_id (quote_id),
    INDEX idx_property_type (property_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
''')
print("✓ Table: quote_properties")

conn.commit()

# Verify
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"\n{'='*50}")
print(f"✓ Database initialized with {len(tables)} tables:")
print(f"{'='*50}")
for t in tables:
    print(f"  ✓ {t[0]}")

cursor.close()
conn.close()
