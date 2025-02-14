from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session
from ..dependencies import get_db
from ..models.content_brief import ContentBrief
from ..services import content_brief_service
from ..services.content_brief_service import get_content_brief_by_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.post("/", response_model=ContentBrief)
async def create(
    content_brief: ContentBrief,
    db: Session = Depends(get_db)
):
    try:
        # Create a new content brief using the service
        content_brief = content_brief_service.create(db=db, content_brief=content_brief)
        return content_brief
    except Exception as e:
        logger.error(f"Failed to create content brief: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create content brief")

@router.get("/{content_brief_id}")
async def get(
    content_brief_id: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        content_brief = get_content_brief_by_id(db=db, content_brief_id=content_brief_id)
        return content_brief
    except Exception as e:
        logger.error(f"Failed to get content brief for ID {content_brief_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content brief for ID {content_brief_id}")