from fastapi import FastAPI, HTTPException
import openai
import os
import sqlite3
import logging
from models.userMessage import ChatRequest
from fuzzywuzzy import fuzz 
from dotenv import load_dotenv





app = FastAPI()

OPENAI_API_KEY="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"
client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
        db_response = find_similar_response(request.movie_character_name, request.user_message)
        if db_response:
            return {"character": request.movie_character_name, "response": db_response}
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are {request.movie_character_name} from a movie. Respond exactly how {request.movie_character_name} would talk maintaining the character's personality and if possible consider the reference to the movie(s) of the character."},
                {"role": "user", "content": request.user_message},
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        chat_response = response.choices[0].message.content.strip()        
        return {"character": request.movie_character_name, "response": chat_response}

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
