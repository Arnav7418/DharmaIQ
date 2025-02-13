import sqlite3
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = chroma_client.get_or_create_collection(
    name="chroma_scripts",
    embedding_function=embedding_func
)

conn = sqlite3.connect("chat_responses.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS chroma_scripts2 (
        rowid INTEGER PRIMARY KEY,
        character TEXT,
        user_message TEXT,
        response TEXT,
        embedding TEXT  -- Store embeddings as a string
    )
""")

cursor.execute("SELECT rowid, character, user_message, response_to_user_message FROM scripts")
data = cursor.fetchall()
for row in data:
    rowid, character, user_message, response = row
    text = f"{character}: {user_message} -> {response}"
    embedding = embedding_func([text])[0]  
    collection.add(
        ids=[str(rowid)],  
        documents=[text],
        metadatas=[{"character": character, "user_message": user_message, "response": response}]
    )

    # From ARNAV(author) - This table is for viewing the database and has no logical use
    cursor.execute("""
        INSERT INTO chroma_scripts2 (rowid, character, user_message, response, embedding)
        VALUES (?, ?, ?, ?, ?)
    """, (rowid, character, user_message, response, str(embedding)))

conn.commit()
conn.close()

