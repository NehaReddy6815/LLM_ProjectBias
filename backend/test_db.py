import sqlite3

DB_PATH = "records.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Count records
c.execute("SELECT COUNT(*) FROM records")
count = c.fetchone()[0]
print(f"\n{'='*60}")
print(f"Total records in database: {count}")
print(f"{'='*60}\n")

# Show all records with full details
c.execute("SELECT * FROM records")
records = c.fetchall()

if records:
    print("📋 All Records in Database:\n")
    for i, record in enumerate(records, 1):
        print(f"Record #{i}")
        print(f"{'─'*60}")
        print(f"  🔑 Hash: {record[0]}")
        print(f"  📝 Prompt: {record[1]}")
        print(f"  📄 Output: {record[2][:100]}..." if len(record[2]) > 100 else f"  📄 Output: {record[2]}")
        print(f"  🎯 Bias Category: {record[3]}")
        print(f"  📊 Bias Score Before: {record[4]}")
        print(f"  📊 Bias Score After: {record[5]}")
        print(f"  ⛓️  Stored on Chain: {'Yes' if record[6] else 'No'}")
        print(f"{'─'*60}\n")
else:
    print("\n❌ No records found in database")

# Show table schema
print("\n📐 Database Schema:")
print(f"{'─'*60}")
c.execute("PRAGMA table_info(records)")
schema = c.fetchall()
for column in schema:
    print(f"  {column[1]} ({column[2]}) - Primary Key: {column[5]}")

conn.close()