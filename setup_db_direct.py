#!/usr/bin/env python3
"""
Direct database setup using mysql command line
"""
import subprocess
import os

# Read schema
with open('quotes_schema.sql', 'r') as f:
    schema_sql = f.read()

# Write to temp file
temp_file = 'temp_schema.sql'
with open(temp_file, 'w') as f:
    f.write(schema_sql)

# Run mysql command
try:
    cmd = [
        'mysql',
        '-h', 'localhost',
        '-u', 'root',
        '-ppassword',
        'insurance_leads'
    ]
    
    print("Running database setup...")
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=schema_sql)
    
    if process.returncode == 0:
        print("✓ Database tables created successfully")
        print(stdout)
    else:
        print("✗ Error creating tables:")
        print(stderr)
        
finally:
    # Clean up temp file
    if os.path.exists(temp_file):
        os.remove(temp_file)
