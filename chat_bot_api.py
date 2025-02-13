import chromadb
from fastapi import FastAPI, HTTPException
import google.generativeai as genai
import os
import sqlite3
import logging
from models.userMessage import ChatRequest
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer  


load_dotenv()

app = FastAPI()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="chroma_scripts")


def get_db_connection():
    conn = sqlite3.connect("chat_responses.db")
    conn.row_factory = sqlite3.Row
    return conn

def find_similar_response(character_name: str, user_message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scripts WHERE LOWER(character) = LOWER(?)", (character_name,))
    messages = cursor.fetchall()
    
    for row in messages:
        stored_message = row["user_message"]
        similarity = fuzz.ratio(user_message.lower(), stored_message.lower())
        
        logging.info(f"Checking similarity: User Message: {user_message} | Stored Message: {stored_message} | Similarity: {similarity}")
        
        if similarity > 50:
            logging.info("Match found in database. Returning stored response.")
            conn.close()
            return row["response_to_user_message"]
    
    conn.close()
    return None

@app.post("/chat")
async def chat_with_character(request: ChatRequest):
    try:
        # db_response = find_similar_response(request.movie_character_name, request.user_message)
        # if db_response:
        #     return {
        #         "character": request.movie_character_name,
        #         "response": db_response,
        #         "source": "Database"
        #     }
        


        results = collection.query(
            query_texts=[request.user_message], 
            n_results=1,
            where={"character": request.movie_character_name}
        )
        if results["documents"]:
            context = results["documents"][0]  
        else:
            context = "No context found" 

        prompt = f"""You are {request.movie_character_name} from a movie. 
        Respond exactly how {request.movie_character_name} would talk, maintaining 
        the character's personality and if possible, refer to the movie(s) the character is from.
        User message: {request.user_message}"""

        response = model.generate_content(prompt)
        return {
            "character": request.movie_character_name,
            "response": response.text.strip(),
            "source": "Generative AI",
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
