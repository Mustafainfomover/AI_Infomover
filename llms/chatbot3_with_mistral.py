# import os
# import aiohttp
# import asyncio
# import json
# from dotenv import load_dotenv
#
# load_dotenv()
#
# async def stream_response(user_input):
#     api_key = os.getenv('MISTRAL_API_KEY')
#     model = "mistral-large-latest"
#     url = "https://api.mistral.ai/v1/chat/completions"
#
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }
#
#     data = {
#         "model": model,
#         "messages": [
#             {
#                 "role": "user", "content": user_input
#             }
#         ],
#         "stream": True
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=headers, json=data) as response:
#             async for line in response.content:
#                 if line.startswith(b'data:'):
#                     chunk = line[len(b'data:'):].strip()
#                     if chunk == b'[DONE]':
#                         continue
#                     if chunk:
#                         try:
#                             chunk_data = json.loads(chunk.decode('utf-8'))
#                             if 'choices' in chunk_data and chunk_data['choices']:
#                                 content = chunk_data['choices'][0]['delta'].get('content', '')
#                                 print(content, end='', flush=True)
#                         except json.JSONDecodeError as e:
#                             print(f"Failed to decode chunk: {chunk}. Error: {e}")
#
#     print("\nStreaming complete.")
#
# def stream_chat_response():
#     print("talk to the ai chatbot. Type exit to end the conversation.")
#     while True:
#         user_input=input("YOU:")
#         if user_input.lower()=="exit":
#             print('thank you for talking.')
#             break
#         else:
#             asyncio.run(stream_response(user_input))
#
# if __name__ == '__main__':
#     stream_chat_response()

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def stream_response(user_input):
    api_key = os.getenv('MISTRAL_API_KEY')
    model = "mistral-large-latest"
    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": user_input}],
        "stream": True
    }

    with requests.post(url, headers=headers, json=data, stream=True) as response:
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    chunk = line[len("data: "):]
                    try:
                        chunk_data = json.loads(chunk)
                        if 'choices' in chunk_data and chunk_data['choices']:
                            content = chunk_data['choices'][0]['delta'].get('content', '')
                            print(content, end='', flush=True)
                    except json.JSONDecodeError as e:
                        print(f"\nFailed to decode chunk: {chunk}. Error: {e}")

    print("\nStreaming complete.")

def stream_chat_response():
    print("Talk to the AI chatbot. Type 'exit' to end the conversation.")
    while True:
        user_input = input("YOU: ")
        if user_input.lower() == "exit":
            print("Thank you for talking.")
            break
        else:
            stream_response(user_input)

if __name__ == '__main__':
    stream_chat_response()
