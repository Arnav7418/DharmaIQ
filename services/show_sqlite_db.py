import sqlite3 as db

conn=db.connect("chat_responses.db")
cursor=conn.cursor()
rows=cursor.execute("Select * from scripts")
for row in rows:
    print(row)