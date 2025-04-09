import os
import time
from dotenv import load_dotenv
from mistralai import Mistral
import re

load_dotenv()



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

            print(chat_response.choices[0].message.content)



if __name__ == '__main__':
    main()
