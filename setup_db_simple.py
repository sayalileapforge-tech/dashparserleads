#!/usr/bin/env python3
"""
Setup database tables using PyMySQL
"""
import pymysql
import sys

def setup_database():
    try:
        # Connect to MySQL
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root@123',
            database='insurance_leads'
        )
        
        cursor = conn.cursor()
        print("✓ Connected to MySQL database")
        
        # Read schema
        with open('quotes_schema.sql', 'r') as f:
            schema = f.read()
        
        # Split statements
        statements = schema.split(';\n')
        count = 0
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--') and not statement.startswith('/*'):
                try:
                    cursor.execute(statement)
                    conn.commit()
                    count += 1
                    print(f"✓ Statement {count} executed")
                except pymysql.Error as e:
                    if e.args[0] == 1050:  # Table exists
                        print(f"✓ Table already exists")
                    else:
                        print(f"✗ Error: {e}")
        
        # Show created tables
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        print("\n" + "="*50)
        print("Database Tables:")
        print("="*50)
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Database setup complete!")
        return True
        
    except pymysql.Error as e:
        print(f"✗ MySQL Error: {e}")
        print("\nTrying with password 'password'...")
        
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='password',
                database='insurance_leads'
            )
            
            cursor = conn.cursor()
            print("✓ Connected to MySQL database")
            
            # Read schema
            with open('quotes_schema.sql', 'r') as f:
                schema = f.read()
            
            # Split and execute
            statements = schema.split(';\n')
            count = 0
            
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--') and not statement.startswith('/*'):
                    try:
                        cursor.execute(statement)
                        conn.commit()
                        count += 1
                    except pymysql.Error as err:
                        if err.args[0] == 1050:
                            pass  # Table exists
                        else:
                            print(f"✗ Error: {err}")
            
            # Show tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            print("\n" + "="*50)
            print(f"Database Tables ({len(tables)}):")
            print("="*50)
            for table in tables:
                print(f"  ✓ {table[0]}")
            
            cursor.close()
            conn.close()
            
            print("\n✓ Database setup complete!")
            return True
            
        except pymysql.Error as e2:
            print(f"✗ MySQL Error with password: {e2}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)
