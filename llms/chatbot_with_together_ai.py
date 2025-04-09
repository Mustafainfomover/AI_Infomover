import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class ChatBot:
    def __init__(self):
        self.api_key = os.getenv('TOGETHER_AI_API_KEY')  # Ensure API key is stored in .env
        self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"  # Adjust based on available models
        self.url = "https://api.together.xyz/v1/chat/completions"
        self.conversation_history = []  # Stores previous messages for memory

    def get_user_input(self):
        """Gets user input and updates conversation history."""
        user_input = input("\nYOU: ")
        user_message = {"role": "user", "content": user_input}
        self.conversation_history.append(user_message)
        return user_input

    def send_request(self):
        """Sends request with full conversation history to Together AI."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": self.conversation_history,
            "stream": True
        }

        buffer = ""
        with requests.post(self.url, headers=headers, json=data, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8").strip()
                    # if line == "[DONE]":
                    #     break
                    if line.startswith("data: "):
                        chunk = line[len("data: "):]
                        if chunk == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(chunk)
                            if 'choices' in chunk_data and chunk_data['choices']:
                                content = chunk_data['choices'][0]['delta'].get('content', '')
                                print(content, end='', flush=True)
                                buffer += content

                        except json.JSONDecodeError as e:
                            print(f"\nFailed to decode chunk: {chunk}. Error: {e}")

        if buffer.strip():
            assistant_message = {"role": "assistant", "content": buffer}
            self.conversation_history.append(assistant_message)

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
