#!/usr/bin/env python3
"""
Initialize database tables for Render deployment
Run this after database is connected to Render
"""

import os
import mysql.connector
from mysql.connector import Error

def create_tables():
    """Create all required database tables"""
    
    # Get connection details from environment
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', 'root@123')
    database = os.getenv('MYSQL_DATABASE', 'insurance_leads')
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = conn.cursor()
        
        print(f"[DB] Connected to {database} at {host}:{port}")
        
        # Read and execute schema
        with open('quotes_schema.sql', 'r') as f:
            schema = f.read()
        
        # Split by semicolon and execute each statement
        statements = schema.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                print(f"[DB] Executing: {statement[:80]}...")
                cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[SUCCESS] All tables created successfully!")
        
    except Error as e:
        print(f"[ERROR] Database error: {e}")
        return False
    except FileNotFoundError:
        print("[ERROR] quotes_schema.sql not found!")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("[INIT] Starting database initialization...")
    success = create_tables()
    exit(0 if success else 1)
