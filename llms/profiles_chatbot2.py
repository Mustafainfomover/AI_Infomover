import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from mistralai import Mistral

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
        """Fetch all profiles with specific fields."""
        return self.profile.find(
            {},
            {
                "firstName": 1,
                "lastName": 1,
                "carrierSummary": 1,
                "highlightedSkills": 1,
                "additionalSkill": 1,
            }
        )

class ChatBot:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.conversation_history = []
        self.mistral_client = Mistral(api_key=api_key)

        # Fetch all profiles as context
        self.profiles_context = self.get_profiles_context()
        if self.profiles_context:
            self.conversation_history.append({"role": "system", "content": self.profiles_context})

    def get_profiles_context(self):
        """Retrieve and format all profiles."""
        profiles_instance = Profiles()
        profiles = profiles_instance.all_profiles()
        profiles_list = []

        for profile in profiles:
            highlighted_skills = ', '.join([skill.get('name', '') for skill in profile.get('highlightedSkills', [])])
            additional_skills = ', '.join([skill.get('name', '') for skill in profile.get('additionalSkill', [])])
            profile_text = f"""
                    Name: {profile.get('firstName', '')} {profile.get('lastName', '')}
                    Summary: {profile.get('carrierSummary', '')}
                    Highlighted Skills: {highlighted_skills}
                    Additional Skills: {additional_skills}
                    Location: {profile.get('currentLocation', '')}
                    """
            profiles_list.append(profile_text)

        return "Profiles:\n" + "\n".join(profiles_list) if profiles_list else "No profiles found."

    def run(self):
        while True:
            self.get_user_input()
            self.send_request()

    def get_user_input(self):
        user_input = input("\n YOU: ")
        user_message = {"role": "user", "content": user_input}
        self.conversation_history.append(user_message)

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
            assistant_message = {"role": "assistant", "content": buffer}
            self.conversation_history.append(assistant_message)

if __name__ == '__main__':
    api_key = os.getenv('MISTRAL_API_KEY')

    if not api_key:
        print("Set your Mistral API key.")
        exit(1)

    chat_bot = ChatBot(api_key, model="mistral-large-latest")
    chat_bot.run()
