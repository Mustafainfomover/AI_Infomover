import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# MongoDB Connection
mongoClient = MongoClient(
    os.getenv('MONGODB_URI'),
    ssl=True,
    tlsCAFile=certifi.where(),
    maxPoolSize=5,
    minPoolSize=5,
)


class Profiles:
    def __init__(self):
        self.db = mongoClient.get_database()
        self.profile = self.db.get_collection("profiles")

    def all_profiles(self):
        """Fetch all profiles and format them."""
        profiles = self.profile.find(
            {},
            {
                "firstName": 1,
                "lastName": 1,
                "carrierSummary": 1,
                "highlightedSkills": 1,
                "additionalSkill": 1,
            }
        )

        profiles_list = []
        for profile in profiles:
            highlighted_skills = ', '.join([skill.get('name', '') for skill in profile.get('highlightedSkills', [])])
            additional_skills = ', '.join([skill.get('name', '') for skill in profile.get('additionalSkill', [])])

            profile_text = f"""
            Name: {profile.get('firstName', '')} {profile.get('lastName', '')}
            Summary: {profile.get('carrierSummary', '')}
            Highlighted Skills: {highlighted_skills}
            Additional Skills: {additional_skills}
            """
            profiles_list.append(profile_text)

        return "Profiles:\n" + "\n".join(profiles_list) if profiles_list else "No profiles found."


class ChatBot:
    def __init__(self, model_name):
        self.model = ChatMistralAI(model=model_name, mistral_api_key=os.getenv("MISTRAL_API_KEY"))
        self.profile_data = Profiles().all_profiles()  # Load profiles from MongoDB

        # Define system prompt template
        self.system_template = (
            "You are an expert recruiter. Use the following profiles to answer the user's question:\n\n{profile_data}"
        )

        # Define prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_template),
            ("user", "{chat_history}\n\nUser: {question}")
        ])

        # Store conversation history
        self.conversation_history = []

    def ask(self, question):
        """Process user input, generate a response, and print it."""
        self.conversation_history.append(HumanMessage(content=question))

        # Prepare conversation history text
        chat_history_text = "\n".join(msg.content for msg in self.conversation_history)

        # Prepare prompt for the model
        prompt = self.prompt_template.invoke({
            "profile_data": self.profile_data,
            "question": question,
            "chat_history": chat_history_text
        })

        print("\nAnswer:")

        # Directly invoke the model
        response = self.model.invoke(prompt)
        print(response.content)  # Print the model's response
        print("\n")


if __name__ == "__main__":
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key is None:
        print("Please set environment variable MISTRAL_API_KEY")
        exit(1)

    bot = ChatBot("mistral-large-latest")

    print("Ask your questions (type 'exit' to stop):\n")
    while True:
        user_question = input("You: ")
        if user_question.strip().lower() == "exit":
            print("Goodbye!")
            break
        bot.ask(user_question)
