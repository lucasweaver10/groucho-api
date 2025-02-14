from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException
from sqlmodel import Session
from ..dependencies import get_db
from ..config import settings
import json
import logging
from .content_outline_sections import ContentOutlineSection
from app.services.content_outline_section_service import get_content_outline_section_by_id

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.get("/{content_outline_section_id}")
async def get_content_outline_section(
    content_outline_section_id: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        content_outline_section = get_content_outline_section_by_id(db=db, content_outline_section_id=content_outline_section_id)
        return content_outline_section
    except Exception as e:
        logger.error(f"Failed to get content outline section for ID {content_outline_section_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content outline section for ID {content_outline_section_id}")