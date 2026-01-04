-- Table for storing all MVR info and conviction data
CREATE TABLE IF NOT EXISTS mvr_info (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    mvr_issue_date DATE,
    mvr_licence_expiry_date DATE,
    mvr_birth_date DATE,
    mvr_convictions_count INTEGER,
    mvr_convictions JSONB,
    mvr_conviction_details TEXT,
    mvr_demerit_points INTEGER,
    mvr_status VARCHAR(100),
    mvr_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
