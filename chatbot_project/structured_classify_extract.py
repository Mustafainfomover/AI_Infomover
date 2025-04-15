import os
from enum import Enum
from random import sample
from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

load_dotenv()


# Enums for structured classification
class SentimentEnum(str, Enum):
    happy = "happy"
    sad = "sad"
    neutral = "neutral"



# Classification + Entity Extraction combined
class TextInsights(BaseModel):
    sentiment: SentimentEnum = Field(description="Sentiment of the text")
    aggressiveness: int = Field(description="Aggressiveness level (1 to 10)")
    language: str = Field(description="Language the text is written in")
    person: str = Field(description="Name of any person mentioned")
    date: str = Field(description="Any date mentioned in the text")
    location: str = Field(description="Any location mentioned")
    organization: str = Field(description="Any organization mentioned")


class TextInsightAnalyzer:
    def __init__(self, model_name: str = "mistral-large-latest", provider: str = "mistralai"):
        """Initialize the analyzer with structured output using Mistral."""
        self.llm = init_chat_model(model_name, model_provider=provider)
        self.llm_with_output = self.llm.with_structured_output(TextInsights)
        self.prompt_template = ChatPromptTemplate.from_template(
            """
Extract the following details from the passage that user has entrered:
- sentiment (happy, neutral, sad)
- aggressiveness (1 to 10)
- language (the language used)
- person
- date
- location
- organization

Respond only with the properties defined in the 'TextInsights' model.

Passage:
{input}
"""
        )

    def analyze_text(self, text: str) -> TextInsights:
        prompt = self.prompt_template.invoke({"input": text})
        response = self.llm_with_output.invoke(prompt)

        if not isinstance(response, TextInsights):
            raise TypeError(f"Expected 'TextInsights', got '{type(response).__name__}'")

        return response

    def analyze_to_dict(self, text: str) -> Dict[str, Any]:
        return self.analyze_text(text).model_dump()


def main():
    if not os.getenv("MISTRAL_API_KEY"):
        print("Please set the environment variable MISTRAL_API_KEY")
        return

    analyzer = TextInsightAnalyzer()

#     sample_text = """
# Apple held its Spring Event on April 10, 2024, in Cupertino. Tim Cook introduced the new iPad Pro.
# """
    sample_text=input("Enter the sentence here:")
    results = analyzer.analyze_to_dict(sample_text)
    print("\n Structured Analysis Result:")
    for key, value in results.items():
        print(f" {key}: {value}")


if __name__ == "__main__":
    main()
