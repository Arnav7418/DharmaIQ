from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(1, 2) 

    @task
    def chat_with_character(self):
        payload = {
            "movie_character_name": "Iron Man",
            "user_message": "What's your best quote?"
        }
        headers = {"Content-Type": "application/json"}

        response = self.client.post("/chat", json=payload, headers=headers)
        
        
        print(f"Response Time: {response.elapsed.total_seconds()} seconds")

# Run using: locust -f locustfile.py --host http://127.0.0.1:8000
