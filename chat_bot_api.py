import logging
import sqlite3
import threading
import chromadb
import aioredis
import google.generativeai as genai
import os
import asyncio  
import time
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from concurrent.futures import ThreadPoolExecutor
from traitlets import FuzzyEnum
from typing import Optional, Dict, Any
from datetime import datetime
from prometheus_client import REGISTRY, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, start_http_server
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import Response

load_dotenv()


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')


chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="chroma_scripts")


executor = ThreadPoolExecutor()



# From ARNAV(author) - Monitoring tools initiazition

REQUESTS_TOTAL = Counter(
    "app_requests_total",
    "Total number of requests by source",
    ["source"]
)

RESPONSE_TIME = Histogram(
    "app_response_time_seconds",
    "Response time in seconds",
    ["source"]
)

ERROR_COUNTER = Counter(
    "app_errors_total",
    "Total number of errors",
    ["type"]
)

ACTIVE_CONNECTIONS = Counter(
    "app_active_connections",
    "Number of active WebSocket connections"
)

DATABASE_PATH = "chat_history.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis
    metrics_thread = threading.Thread(
        target=start_metrics_server,
        args=(9090,),
        daemon=True
    )
    metrics_thread.start()
    redis = await aioredis.from_url("redis://localhost", decode_responses=True)
    create_chat_history_db()
    yield
    await redis.close()
    executor.shutdown(wait=True)

app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


def start_metrics_server(port=9090):
    start_http_server(port)
    logging.info(f"Metrics server started on port {port}")


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


class DatabaseConnection:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

def create_chat_history_db():
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                character_name TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                UNIQUE(user_id, character_name, user_message)
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_character 
            ON chatHistory(user_id, character_name)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON chatHistory(timestamp)
        ''')
        
        conn.commit()

def save_chat_history(
    user_id: str,
    character_name: str,
    user_message: str,
    ai_response: str,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chatHistory (
                    user_id, character_name, user_message, ai_response, metadata
                )
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, character_name, user_message, ai_response, 
                  str(metadata) if metadata else None))
            conn.commit()
            return True
    except sqlite3.Error as e:
        return False



def find_similar_response(user_id: str, character_name: str, user_message: str, 
                         similarity_threshold: float = 0.8) -> Optional[str]:
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chatHistory 
            WHERE user_id = ? AND LOWER(character_name) = LOWER(?)
            ORDER BY timestamp DESC LIMIT 100
        """, (user_id, character_name))
        
        messages = cursor.fetchall()
        
        highest_similarity = 0
        best_response = None
        
        for row in messages:
            stored_message = row["user_message"]
            similarity = FuzzyEnum.ratio(user_message.lower(), stored_message.lower())
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_response = row["ai_response"]
        
        if highest_similarity >= similarity_threshold:
            return best_response
        
        return None

async def query_chroma(character_name: str, user_message: str):
    loop = asyncio.get_running_loop()
    where_condition = {"character": {"$eq": character_name}} if character_name else {} 
    try:
        return await loop.run_in_executor(
            None,
            lambda: collection.query(
                query_texts=[user_message],
                n_results=1,
                where=where_condition
            )
        )
    except Exception as e:
        return {"documents": []}

async def generate_ai_response(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(
            executor,
            lambda: model.generate_content(prompt).text.strip()
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate AI response")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ACTIVE_CONNECTIONS.inc()
    
    try:
        while True:
            try:
                data = await websocket.receive_json()
                
                user_id = data.get("user_id")
                character_name = data.get("movie_character_name")
                user_message = data.get("user_message")
                
                if not all([user_id, character_name, user_message]):
                    ERROR_COUNTER.labels(type="missing_fields").inc()
                    await websocket.send_json({
                        "error": "Missing required fields"
                    })
                    continue
                
                start_time = time.time()
                similar_response = find_similar_response(user_id, character_name, user_message)
                if similar_response:
                    total_time = time.time() - start_time
                    REQUESTS_TOTAL.labels(source="chat_history").inc()
                    RESPONSE_TIME.labels(source="chat_history").observe(total_time)
                    
                    await websocket.send_json({
                        "user_id": user_id,
                        "character": character_name,
                        "response": similar_response,
                        "source": "Chat History",
                        "time_taken": f"{total_time:.4f} seconds"
                    })
                    continue
                cache_key = f"{user_id}:{character_name}:{user_message}"
                cached_response = await redis.get(cache_key)
                
                if cached_response:
                    total_time = time.time() - start_time
                    REQUESTS_TOTAL.labels(source="cache").inc()
                    RESPONSE_TIME.labels(source="cache").observe(total_time)
                    
                    await websocket.send_json({
                        "user_id": user_id,
                        "character": character_name,
                        "response": cached_response,
                        "source": "Cache",
                        "time_taken": f"{total_time:.4f} seconds"
                    })
                    continue
                try:
                    chroma_task = query_chroma(character_name, user_message)
                    prompt = f"""You are {character_name} from a movie. 
                    Respond exactly how {character_name} would talk, maintaining 
                    the character's personality and if possible, refer to the movie(s) 
                    the character is from.
                    User message: {user_message}"""
                    
                    ai_task = generate_ai_response(prompt)
                    results, response = await asyncio.gather(chroma_task, ai_task)
                    
                    context = results["documents"][0] if results["documents"] else "No context found"
                    await redis.setex(cache_key, 3600, response)
                    
                    total_time = time.time() - start_time
                    REQUESTS_TOTAL.labels(source="generative_ai").inc()
                    RESPONSE_TIME.labels(source="generative_ai").observe(total_time)
                    
                    metadata = {
                        "context": context,
                        "source": "Generative AI",
                        "timestamp": datetime.now().isoformat()
                    }
                    save_chat_history(user_id, character_name, user_message, response, metadata)
                    
                    await websocket.send_json({
                        "user_id": user_id,
                        "character": character_name,
                        "response": response,
                        "source": "Generative AI",
                        "context": context,
                        "time_taken": f"{total_time:.4f} seconds"
                    })
                    
                except Exception as e:
                    ERROR_COUNTER.labels(type="ai_generation").inc()
                    raise
                    
            except Exception as e:
                ERROR_COUNTER.labels(type="websocket_communication").inc()
                await websocket.send_json({
                    "error": f"Error processing request: {str(e)}"
                })
                
    except WebSocketDisconnect:
        ACTIVE_CONNECTIONS.dec()
        return "Web Socket disconnected"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)