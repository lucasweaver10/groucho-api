from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException
from sqlmodel import Session
from ..dependencies import get_db
from ..config import settings
import json
import logging
from .content_outlines import ContentOutline
from app.services.content_outline_service import get_content_outline_by_id

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.get("/{content_outline_id}")
async def get_content_outline(
    content_outline_id: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        content_outline = get_content_outline_by_id(db=db, content_outline_id=content_outline_id)
        return content_outline
    except Exception as e:
        logger.error(f"Failed to get content outline for ID {content_outline_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content outline for ID {content_outline_id}")