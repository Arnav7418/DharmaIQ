import sqlite3 as db
from tabulate import tabulate

conn = db.connect("chat_history.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(chatHistory)")
columns = [col[1] for col in cursor.fetchall()]
cursor.execute("SELECT * FROM chatHistory")
rows = cursor.fetchall()
if rows:
    print(tabulate(rows, headers=columns, tablefmt="grid"))
else:
    print("No chat history found.")

conn.close()
