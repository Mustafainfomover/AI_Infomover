import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class ChatBot:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_GEMINI_API_KEY')  # Ensure API key is stored in .env
        self.model = "gemini-2.0-flash"  # Choose the appropriate Gemini model
        self.url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
        self.conversation_history = []  # Stores previous messages for memory

    def get_user_input(self):
        """Gets user input and updates conversation history."""
        user_input = input("\nYOU: ")
        user_message = {"role": "user", "parts": [{"text": user_input}]}
        self.conversation_history.append(user_message)
        return user_input

    def send_request(self):
        """Sends request with full conversation history to Google Gemini."""
        headers = {"Content-Type": "application/json"}
        data = {"contents": self.conversation_history}

        response = requests.post(self.url, headers=headers, json=data)

        if response.status_code == 200:
            try:
                response_data = response.json()
                message = response_data["candidates"][0]["content"]["parts"][0]["text"]

                words = message.split()  # Process word by word
                for word in words:
                    print(word, end=' ', flush=True)  # Print words immediately
                print()  # New line after response

                assistant_message = {"role": "assistant", "parts": [{"text": message}]}
                self.conversation_history.append(assistant_message)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"Error parsing response: {e}")
        else:
            print(f"Request failed: {response.status_code} - {response.text}")

    def run(self):
        """Runs the chatbot in a loop."""
        print("Talk to the AI chatbot. Type 'exit' to end the conversation.")
        while True:
            user_input = self.get_user_input()
            if user_input.lower() == "exit":
                print("\nThank you for chatting!")
                break
            self.send_request()

if __name__ == '__main__':
    chatbot = ChatBot()
    chatbot.run()
