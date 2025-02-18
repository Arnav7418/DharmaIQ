import sqlite3
from datetime import datetime
from tabulate import tabulate

def view_chat_history():
    try:
        # Connect to the database
        conn = sqlite3.connect('chat_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all records from chatHistory
        cursor.execute("""
            SELECT 
                id,
                user_id,
                character_name,
                user_message,
                ai_response,
                timestamp
            FROM chatHistory
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No chat history found.")
            return

        # Convert rows to list of dictionaries for better display
        formatted_rows = []
        for row in rows:
            formatted_rows.append({
                'ID': row['id'],
                'User ID': row['user_id'],
                'Character': row['character_name'],
                'User Message': row['user_message'][:50] + '...' if len(row['user_message']) > 50 else row['user_message'],
                'AI Response': row['ai_response'][:50] + '...' if len(row['ai_response']) > 50 else row['ai_response'],
                'Timestamp': row['timestamp']
            })

        # Print using tabulate for better formatting
        print("\n=== Chat History ===\n")
        print(tabulate(formatted_rows, headers='keys', tablefmt='grid'))
        
        # Print some statistics
        cursor.execute("SELECT COUNT(*) as total FROM chatHistory")
        total_chats = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) as users FROM chatHistory")
        unique_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT character_name) as characters FROM chatHistory")
        unique_characters = cursor.fetchone()[0]
        
        print(f"\nStatistics:")
        print(f"Total Chats: {total_chats}")
        print(f"Unique Users: {unique_users}")
        print(f"Unique Characters: {unique_characters}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def view_user_history(user_id):
    try:
        conn = sqlite3.connect('chat_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                id,
                character_name,
                user_message,
                ai_response,
                timestamp
            FROM chatHistory
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No chat history found for user {user_id}")
            return

        formatted_rows = []
        for row in rows:
            formatted_rows.append({
                'ID': row['id'],
                'Character': row['character_name'],
                'User Message': row['user_message'][:50] + '...' if len(row['user_message']) > 50 else row['user_message'],
                'AI Response': row['ai_response'][:50] + '...' if len(row['ai_response']) > 50 else row['ai_response'],
                'Timestamp': row['timestamp']
            })

        print(f"\n=== Chat History for User {user_id} ===\n")
        print(tabulate(formatted_rows, headers='keys', tablefmt='grid'))

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    while True:
        print("\nChat History Viewer")
        print("1. View all chat history")
        print("2. View specific user's history")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            view_chat_history()
        elif choice == "2":
            user_id = input("Enter user ID: ")
            view_user_history(user_id)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")