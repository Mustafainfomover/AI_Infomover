from pyexpat.errors import messages

from llms.chatbot3_with_mistral import stream_response
import os
import time
from dotenv import load_dotenv
from mistralai import Mistral
load_dotenv()
class ChatBot:
    def __init__(self, api_key, model):
        self.api_key= api_key
        self.model= model
        self.conversation_history=[]
        self.mistral_client = Mistral(api_key=api_key)

    def run(self):
        while True:
            self.get_user_input()
            self.send_request()

    def get_user_input(self):
        user_input=input("\n YOU: ")
        user_message={
            "role":"user",
            "content": user_input
        }
        self.conversation_history.append(user_message)
        return user_message

    def send_request(self):
        stream_response = self.mistral_client.chat.stream(
            model=self.model,
            messages=self.conversation_history
        )
        buffer = ""
        for chunk in stream_response:
            content = chunk.data.choices[0].delta.content
            print(content, end="")
            buffer += content

        if buffer.strip():
            assistant_message = {
                "role": "assistant",
                "content": buffer
            }
            self.conversation_history.append(assistant_message)
            # print(chunk.data.choices[0].delta.content,end="")


if __name__ == '__main__':
    api_key = os.getenv('MISTRAL_API_KEY')
    if api_key is None:
        print("better set your key")
        exit(1)

    chat_bot = ChatBot(api_key, model="mistral-large-latest")
    chat_bot.run()