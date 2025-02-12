import requests
from bs4 import BeautifulSoup
import sqlite3

BASE_URL = "https://www.imsdb.com"

def get_script_links():
    response = requests.get(f"{BASE_URL}/all-scripts.html")
    soup = BeautifulSoup(response.text, "html.parser")
    
    links = []
    for link in soup.select("p a"):  
        script_url = BASE_URL + link["href"]
        script_name = link.text.strip()
        links.append((script_name, script_url))
    
    return links

def get_script_text(script_url):
    response = requests.get(script_url)
    soup = BeautifulSoup(response.text, "html.parser")
    script_content = soup.find("td", class_="scrtext")
    return script_content.get_text(strip=True) if script_content else None

conn = sqlite3.connect("chat_responses.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_title TEXT NOT NULL,
    script_text TEXT NOT NULL
)
""")

script_links = get_script_links()
for title, url in script_links[:100]:  
    script_text = get_script_text(url)
    if script_text:
        cursor.execute("INSERT INTO scripts (movie_title, script_text) VALUES (?, ?)", (title, script_text))
        print(f"Added script: {title}")

conn.commit()
conn.close()



