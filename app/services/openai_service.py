from fastapi import HTTPException
from typing import List
from pydantic import BaseModel
from ..clients.openai import OpenAIClient

# Model definitions
class ExampleModel(BaseModel):
    scenario: str
    explanation: str

class QuestionModel(BaseModel):
    question: str
    answer: str

class ExampleData(BaseModel):
    examples: List[ExampleModel]
    questions: List[QuestionModel]

class OpenAIService:
    def __init__(self):
        self.client = OpenAIClient()

    def _create_topic_messages(self, topic: str) -> list[dict]:
        """Create the messages for topic generation."""
        return [
            {
                "role": "system",
                "content": """You're an expert in doing things. Your task is to generate data for the given prompt."""
            },
            {
                "role": "user",
                "content": f"""Generate data from the prompt.
                
                More prompt info:
                - here
                - here
                - here
                """
            }
        ]

    async def generate_example_data(self, topic: str) -> ExampleData:
        """Generate structured topic data using OpenAI."""
        try:
            messages = self._create_topic_messages(topic)
            return self.client.get_completion(
                response_model=ExampleData,
                messages=messages,
                model="gpt-4o-mini",
                temperature=0.7
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate topic data: {str(e)}"
            )
