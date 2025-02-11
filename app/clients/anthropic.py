import anthropic
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class AnthropicClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY is not set")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def create_message(
        self,
        prompt: str,
        system_prompt: str,
        tools: list,
        tool_choice: dict,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 2024
    ):
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                tool_choice=tool_choice,
                system=system_prompt,
                tools=tools,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_message: {str(e)}", exc_info=True)
            raise
