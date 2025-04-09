import os
import time
from dotenv import load_dotenv
from mistralai import Mistral
import re

load_dotenv()

def replying(answer):
    lines = re.split(r'[.:]', answer) #answer.split("." or ":")
    for line in lines:
        words=line.split()
        for word in words:
            print(word, end=" ")
            time.sleep(0.15)
        print()

def main():
    api_key = os.getenv('MISTRAL_API_KEY')
    if api_key is None:
        print("better set your key")
        exit(1)

    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)
    print("chat with bot type exit to exit the chat.")
    while True:
        user_input=input("YOU:")
        if user_input.lower()=="exit":
            print('thank you for visiting.')
            break
        else:
            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": user_input,
                    },

                ]

            )

            answer = chat_response.choices[0].message.content
            # print(type(answer))
            replying(answer)

if __name__ == '__main__':
    main()
