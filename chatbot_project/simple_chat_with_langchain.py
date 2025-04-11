import getpass
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pyexpat.errors import messages

load_dotenv()

if __name__ == '__main__':
    if not os.environ.get("MISTRAL_API_KEY"):
        os.environ["MISTRAL_API_KEY"]=getpass.getpass("enter api key for mistral ai: ")

    model =init_chat_model()
    messages=[
        SystemMessage("Translate the following from English into Hindi"),
        HumanMessage("My name is Mustafa Ahmed I stay in Bhopal"),
    ]
    # response = model.invoke(messages)
    # print(response.content)

    for token in model.stream(messages):
        print(token.content, end="")