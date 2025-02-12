import sqlite3

conn = sqlite3.connect("chat_responses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character TEXT NOT NULL,
    user_message TEXT NOT NULL,
    response_to_user_message TEXT NOT NULL
);
""")

conn.commit()
conn.close()
print("Database setup complete")
