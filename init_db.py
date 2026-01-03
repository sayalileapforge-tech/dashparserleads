import pymysql
import re

conn = pymysql.connect(host='localhost', user='root', password='root@123', database='insurance_leads')
cursor = conn.cursor()

# Read schema
with open('quotes_schema.sql', 'r') as f:
    content = f.read()

# Split on ; but keep them - better method
parts = content.split(';')
count = 0

for part in parts:
    statement = part.strip()
    # Skip empty and comments
    if not statement or statement.startswith('--') or statement.startswith('/*'):
        continue
    
    # Re-add semicolon
    statement = statement + ';'
    
    try:
        cursor.execute(statement)
        conn.commit()
        count += 1
        print(f"✓ Statement {count}")
    except Exception as e:
        err_str = str(e)
        # Ignore duplicate table errors
        if '1050' in err_str or 'already exists' in err_str:
            print(f"✓ Statement {count} (already exists)")
        else:
            print(f"✗ Error in statement {count}: {e}")
            # Print first 100 chars of statement for debugging
            print(f"  Statement preview: {statement[:100]}...")

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"\n{'='*50}")
print(f"✓ Database initialized with {len(tables)} tables")
print(f"{'='*50}")
for t in tables:
    print(f"  ✓ {t[0]}")

cursor.close()
conn.close()
print("\n✓ All done!")
