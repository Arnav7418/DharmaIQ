# Level Wise Demonstration videos 
## Level 1: Basic Chat Bot API  
### Demonstration Video for level 1 (Click the thumbnail below to play YouTube video)
[![Basic Chat Bot API](https://img.youtube.com/vi/qwBli23dtbk/maxresdefault.jpg)](https://youtu.be/qwBli23dtbk)  

## Level 2: Store & Retrieve Movie Script Data  
### Demonstration Video for level 2 (Hosted on YouTube)
[![Store & Retrieve Movie Script Data](https://img.youtube.com/vi/jd_L0a9Ztho/maxresdefault.jpg)](https://youtu.be/jd_L0a9Ztho)  


## Level 3: Implement RAG with Vector Search
### Demonstration Video for level 3 (Hosted on YouTube)
[![Implement RAG with Vector Search](https://img.youtube.com/vi/_sWnGE9vdxs/maxresdefault.jpg)](https://youtu.be/_sWnGE9vdxs)  

## Level 4: Scale System to Handle High Traffic
### Demonstration Video for level 4 (Hosted on YouTube)
[![Scale System to Handle High Traffic](https://img.youtube.com/vi/8FzKVNJ1CjQ/maxresdefault.jpg)](https://youtu.be/8FzKVNJ1CjQ)  


## Level 5: Optimize for Latency & Deploy 
### Demonstration Video for level 5 (Hosted on YouTube)
[![Optimize for Latency & Deploy ](https://img.youtube.com/vi/8FzKVNJ1CjQ/maxresdefault.jpg)](https://youtu.be/5rqG21H6ieo)  


# How to run the project

## Step 1: Clone the repository using git or download the zip.

## Step 2: Run the command in the terminal.
```bash
pip install -r requirements.txt
```

## Step 3: Install the Redis for caching using Linux (WSL)

## Step 4: Run the command to start the project 
```bash
uvicorn chat_bot_api:app --host 0.0.0.0 --port 8000
```

## Step 5: Use any Websocket platform like Postman to test the code

### Step 5.1: Download the Postman desktop app 
### Step 5.2: Open the Postman app and click on "NEW"
### Step 5.3: Select WebSocket 
### Step 5.4: Enter the following URL
```bash
ws://localhost:8000/ws
```
### Step 5.5: Click Connect

# API Documentation 

## Send the request body in the following format 
```bash
{
    "user_id": "Enter your id",
    "movie_character_name": "Character name you want to talk to",
    "user_message": "Message to the movie_character_name"
}
```


