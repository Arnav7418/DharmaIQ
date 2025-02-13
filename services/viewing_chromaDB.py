import sqlite3
import pandas as pd

conn = sqlite3.connect("chat_responses.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM chroma_scripts2")
data = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
conn.close()
df = pd.DataFrame(data, columns=columns)
print(df)
