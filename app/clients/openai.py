from typing import Type, Any
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        logging.error("OpenAI API key not found in environment variables")
        raise ValueError("OpenAI API key not found")
    return OpenAI(api_key=api_key)

class OpenAIClient:
    def __init__(self):
        self.client = get_openai_client()

    async def get_structured_response(
        self,
        response_model: Type[BaseModel],
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7
    ) -> Any:
        try:
            logging.info(f"Requesting structured response with model: {model}")
            completion = self.client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=response_model,
                temperature=temperature
            )
            
            logging.info("Successfully received response from OpenAI API")
            return completion.choices[0].message.parsed
            
        except Exception as e:
            logging.error(f"Error in get_structured_response: {str(e)}", exc_info=True)
            raise
