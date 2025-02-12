from pydantic import BaseModel

class ChatRequest(BaseModel):
    movie_character_name: str
    user_message: str