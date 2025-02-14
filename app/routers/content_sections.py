from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from ..dependencies import get_db
from ..config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.post("/new")
async def generate_content_section():
    try:
        from app.services.content_section_service import generate_content_section
        response = await generate_content_section()
        return {"content_block": response.data}
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))