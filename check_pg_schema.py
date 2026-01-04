import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cur.fetchall()
    print("Tables in your PostgreSQL database:")
    for table in tables:
        print(table[0])
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
