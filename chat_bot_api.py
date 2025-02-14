import chromadb
import aioredis
from fastapi import FastAPI, HTTPException, Request, Depends
import google.generativeai as genai
import os
import logging
from models.userMessage import ChatRequest
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import time

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="chroma_scripts")

RATE_LIMIT = 2 
RATE_LIMIT_WINDOW = 2 


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis
    redis = await aioredis.from_url("redis://localhost", decode_responses=True)
    yield 
    await redis.close()

app = FastAPI(lifespan=lifespan)

async def rate_limiter(request: Request):
    user_id = request.client.host 
    current_time = time.time()
    key = f"rate_limit:{user_id}"
    await redis.zremrangebyscore(key, "-inf", current_time - RATE_LIMIT_WINDOW)
    request_count = await redis.zcount(key, "-inf", "+inf") 

    # print(f"User: {user_id} | Requests in window: {request_count}") // From ARNAV(author) - Is a debugging statement
    MAX_REQUESTS = 2  
    if request_count >= MAX_REQUESTS:
        print("Rate limit exceeded!")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    await redis.zadd(key, {str(current_time): current_time})
    
    await redis.expire(key, RATE_LIMIT_WINDOW)


@app.post("/chat")
async def chat_with_character(request: ChatRequest, _: None = Depends(rate_limiter)):
    cache_key = f"{request.movie_character_name}:{request.user_message}"
    cached_response = await redis.get(cache_key)

    if cached_response:
        return {
            "character": request.movie_character_name,
            "response": cached_response,
            "source": "Cache",
            "context": "Cached response"
        }

    results = collection.query(
        query_texts=[request.user_message], 
        n_results=1,
        where={"character": request.movie_character_name}
    )

    context = results["documents"][0] if results["documents"] else "No context found"

    prompt = f"""You are {request.movie_character_name} from a movie. 
    Respond exactly how {request.movie_character_name} would talk, maintaining 
    the character's personality and if possible, refer to the movie(s) the character is from.
    User message: {request.user_message}"""

    response = model.generate_content(prompt).text.strip()

    await redis.setex(cache_key, 3600, response)

    return {
        "character": request.movie_character_name,
        "response": response,
        "source": "Generative AI",
        "context": context
    }






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
           
        if similarity > 50:
            conn.close()
            return row["response_to_user_message"]
    
    conn.close()
    return None

