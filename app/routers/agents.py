from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException
from sqlmodel import Session
from ..dependencies import get_db
from ..config import settings  # Import settings to check environment
import json
import logging

from pydantic import BaseModel
from app.agents.content_writer_agent import content_writer_agent

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

prompt = '''
Outline section:
[section]
    - IELTS Writing Tips for Success
    - Provide effective tips for approaching both tasks in the writing test.
    - Discuss the importance of understanding the task requirements and questions.
    - Emphasize the value of practice and feedback in improving writing skills.

Writing Sample:
What's the benefit for you? Objective Feedback The AI provides unbiased, consistent feedback on your pronunciation, helping you identify areas for improvement. Previously this was something only available if you paid for private lessons with a language tutor. But now, you can have your very own personalized AI speaking coach help you learn how to improve and correct your pronunciation in your target language. Improved Pronunciation By receiving detailed scores (extra details are only available in certain languages), you can pinpoint specific pronunciation issues and work on them, resulting in you having clearer and more accurate speech. Boosted Confidence Knowing that you're pronouncing words correctly can significantly boost your confidence when speaking a new language. While the AI scores may not always be perfect (although sometimes they're scary close!), they're certainly good enough to tell you if you're on the right track with pronouncing even the trickiest of words.

Next section's outline:
[section]
    - Understanding IELTS Writing Task 1
    - Outline the structure and requirements of Task 1.
    - Discuss common types of questions and how to approach them.
    - Highlight the importance of data interpretation and summarization skills.

Product description:
IELTS Writing Checker: Get your IELTS Writing Essays checked by AI or an expert IELTS teacher to get feedback on how you can improve to get the IELTS Writing score you need THE FIRST TIME. Featuring custom trained models and a free and premium version.

Negative words:
n/a
'''

@router.post("/content-writer-agent/generate-content-block")
async def generate_content_block():
    try:
        response = await content_writer_agent.run(prompt)
        return {"content": response.data}
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
