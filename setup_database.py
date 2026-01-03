#!/usr/bin/env python3
"""
Setup database tables for quotes management.
Run this once to create all required tables.
"""

import mysql.connector
from mysql.connector import Error
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'insurance_leads'
}

# Read schema from file
with open('quotes_schema.sql', 'r') as f:
    schema = f.read()

try:
    # Connect to database
    connection = mysql.connector.connect(**DB_CONFIG)
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print(f"✓ Connected to MySQL Server version {db_info}")
        
        cursor = connection.cursor()
        
        # Split and execute each statement
        statements = schema.split(';\n')
        
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    connection.commit()
                    print(f"✓ Statement {i+1} executed successfully")
                except Error as err:
                    if err.errno == 1050:  # Table already exists
                        print(f"✓ Table already exists (skipped)")
                    else:
                        print(f"✗ Error: {err}")
                        connection.rollback()
        
        cursor.close()
        
        # Verify tables created
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        print("\n" + "="*50)
        print("Database Tables Created:")
        print("="*50)
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        cursor.close()
        
except Error as err:
    print(f"✗ Database connection error: {err}")
    sys.exit(1)
    
finally:
    if connection.is_connected():
        connection.close()
        print("\n✓ Database connection closed")
