import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate():
    conn_str = os.getenv('DATABASE_URL')
    if not conn_str:
        print("DATABASE_URL not found")
        return

    try:
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        
        print("Checking for missing columns in 'leads' table...")
        
        # Add renewal_date
        try:
            cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS renewal_date DATE")
            print("✓ Added renewal_date column")
        except Exception as e:
            print(f"Error adding renewal_date: {e}")
            conn.rollback()
            
        # Add premium
        try:
            cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS premium NUMERIC(10,2)")
            print("✓ Added premium column")
        except Exception as e:
            print(f"Error adding premium: {e}")
            conn.rollback()

        # Add signal
        try:
            cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS signal VARCHAR(100)")
            print("✓ Added signal column")
        except Exception as e:
            print(f"Error adding signal: {e}")
            conn.rollback()

        conn.commit()
        print("Migration complete!")
        
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
