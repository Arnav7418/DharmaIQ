import requests
import threading

def send_request(i):
    url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    data = {"movie_character_name": "Iron Man", "user_message": f"Hello {i}"}
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Request {i}: {response.status_code}, {response.text}")

threads = []

for i in range(1, 21):  
    thread = threading.Thread(target=send_request, args=(i,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()  




