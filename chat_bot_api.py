import sqlite3
import chromadb
import aioredis
from fastapi import FastAPI, HTTPException, Request, Depends
import google.generativeai as genai
import os
import logging

from traitlets import FuzzyEnum
from models.userMessage import ChatRequest
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import time
import asyncio  
from concurrent.futures import ThreadPoolExecutor  

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="chroma_scripts")

RATE_LIMIT = 5
RATE_LIMIT_WINDOW = 2 

executor = ThreadPoolExecutor()  

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

    MAX_REQUESTS = 2  
    if request_count >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    await redis.zadd(key, {str(current_time): current_time})
    await redis.expire(key, RATE_LIMIT_WINDOW)

async def query_chroma(character_name: str, user_message: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: collection.query(
        query_texts=[user_message], 
        n_results=1,
        where={"character": character_name}
    ))

async def generate_ai_response(prompt: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: model.generate_content(prompt).text.strip())

@app.post("/chat")
async def chat_with_character(request: ChatRequest, _: None = Depends(rate_limiter)):
    start_time = time.time()

    cache_key = f"{request.movie_character_name}:{request.user_message}"
    cached_response = await redis.get(cache_key)

    if cached_response:
        total_time = time.time() - start_time
        return {
            "character": request.movie_character_name,
            "response": cached_response,
            "source": "Cache",
            "context": "Cached response",
            "time_taken": f"{total_time:.4f} seconds"
        }

    
    chroma_task = query_chroma(request.movie_character_name, request.user_message)
    
    prompt = f"""You are {request.movie_character_name} from a movie. 
    Respond exactly how {request.movie_character_name} would talk, maintaining 
    the character's personality and if possible, refer to the movie(s) the character is from.
    User message: {request.user_message}"""
    
    ai_task = generate_ai_response(prompt)

    results, response = await asyncio.gather(chroma_task, ai_task)

    context = results["documents"][0] if results["documents"] else "No context found"

   
    await redis.setex(cache_key, 3600, response)

    total_time = time.time() - start_time

    return {
        "character": request.movie_character_name,
        "response": response,
        "source": "Generative AI",
        "context": context,
        "time_taken": f"{total_time:.4f} seconds"
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
        similarity = FuzzyEnum.ratio(user_message.lower(), stored_message.lower())
           
        if similarity > 50:
            conn.close()
            return row["response_to_user_message"]
    
    conn.close()
    return None