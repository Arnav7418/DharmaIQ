import sqlite3 as db
conn = db.connect("chat_history.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = OFF;")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    cursor.execute(f"DELETE FROM {table_name};")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';") 
cursor.execute("PRAGMA foreign_keys = ON;")
conn.commit()
conn.close()

print("All data has been deleted from the database.")
