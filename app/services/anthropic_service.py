from fastapi import HTTPException
from ..clients.anthropic import AnthropicClient
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class AnthropicTools:
    """Collection of tool definitions for different purposes."""
    
    @staticmethod
    def email_tools() -> List[Dict[str, Any]]:
        return [{
            "name": "generate_email",
            "description": "Generate an email object for a real estate property.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "preheader": {"type": "string", "description": "Email preheader"},
                    "greeting": {"type": "string", "description": "Email greeting"},
                    "first_sentence_hook": {"type": "string", "description": "First sentence hook"},
                    "first_value_paragraph": {"type": "string", "description": "First value paragraph"},
                    "second_value_paragraph": {"type": "string", "description": "Second value paragraph"},
                    "third_value_paragraph": {"type": "string", "description": "Third value paragraph"},
                    "call_to_action": {"type": "string", "description": "Call to action"},
                },
                "required": [
                    "name", "subject", "preheader", "greeting", "first_sentence_hook",
                    "first_value_paragraph", "second_value_paragraph", 
                    "third_value_paragraph", "call_to_action"
                ]
            }
        }]

    @staticmethod
    def summary_tools() -> List[Dict[str, Any]]:
        return [{
            "name": "generate_summary",
            "description": "Generate a concise summary of the provided content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Summary title"},
                    "main_points": {"type": "array", "items": {"type": "string"}, "description": "Key points"},
                    "conclusion": {"type": "string", "description": "Summary conclusion"}
                },
                "required": ["title", "main_points", "conclusion"]
            }
        }]

    @staticmethod
    def analysis_tools() -> List[Dict[str, Any]]:
        return [{
            "name": "analyze_content",
            "description": "Perform detailed analysis of the provided content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "key_findings": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                    "insights": {"type": "object"}
                },
                "required": ["key_findings", "recommendations", "insights"]
            }
        }]

class AnthropicService:
    def __init__(self):
        self.client = AnthropicClient()
        self.tools = AnthropicTools()

    async def _process_response(self, message: Any, tool_name: str) -> Any:
        """Process the response from Claude."""
        if not message:
            logger.error("No content received in Claude's response")
            raise HTTPException(
                status_code=500,
                detail="No content received from Claude"
            )

        try:
            response_data = message.content[0].input
            logger.debug(f"Extracted {tool_name} data: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Error extracting {tool_name} data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract {tool_name} data from response"
            )

    async def generate_email(self, prompt: str) -> Dict[str, Any]:
        """Generate an email using Claude."""
        try:
            message = self.client.create_message(
                prompt=prompt,
                system_prompt="""You are an expert email generator for a real estate company. 
                Generate an email object based on the provided data.""",
                tools=self.tools.email_tools(),
                tool_choice={"type": "tool", "name": "generate_email"}
            )
            return await self._process_response(message, "email")
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate email: {str(e)}"
            )

    async def generate_summary(self, prompt: str) -> Dict[str, Any]:
        """Generate a summary using Claude."""
        try:
            message = self.client.create_message(
                prompt=prompt,
                system_prompt="You are an expert at creating concise, informative summaries.",
                tools=self.tools.summary_tools(),
                tool_choice={"type": "tool", "name": "generate_summary"}
            )
            return await self._process_response(message, "summary")
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate summary: {str(e)}"
            )

    async def analyze_content(self, prompt: str) -> Dict[str, Any]:
        """Analyze content using Claude."""
        try:
            message = self.client.create_message(
                prompt=prompt,
                system_prompt="You are an expert content analyzer.",
                tools=self.tools.analysis_tools(),
                tool_choice={"type": "tool", "name": "analyze_content"}
            )
            return await self._process_response(message, "analysis")
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze content: {str(e)}"
            )
