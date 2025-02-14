from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session
from ..dependencies import get_db
from ..models.content import Content
from ..services import content_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.post("/", response_model=Content)
async def create_content(
    content: Content,
    db: Session = Depends(get_db) 
):
    try:
        content = content_service.create(db=db, content=content)
        return content
    except Exception as e:
        logger.error(f"Failed to create content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create content")


@router.get("/{content_id}")
async def get(
    content_id: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        content = content_service.get(db=db, content_id=content_id)
        return content
    except Exception as e:
        logger.error(f"Failed to get content for ID {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content for ID {content_id}")