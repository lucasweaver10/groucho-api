from datetime import datetime
from sqlalchemy.orm import Session
from app.models.content_brief import ContentBrief
from fastapi import Depends, HTTPException, Path
from ..dependencies import get_db
from .content_service import create_empty_content

def create(db: Session, content_brief: ContentBrief) -> ContentBrief:
    """Create a new content brief"""
    try:
        content_id = get_or_create_content_id(db=db, content_brief=content_brief, user_id=content_brief.user_id)
        content_brief.content_id = content_id
        
        content_brief.created_at = datetime.utcnow()
        content_brief.updated_at = datetime.utcnow()

        db.add(content_brief)
        db.commit()
        db.refresh(content_brief)
        
        return content_brief
    except Exception as e:
        db.rollback()
        raise e

def get_content_brief_by_id(
    db: Session = Depends(get_db),
    content_brief_id: int = Path(...),
) -> ContentBrief:
    """Get a content brief by its ID"""
    content_brief = db.query(ContentBrief).filter(
        ContentBrief.id == content_brief_id
    ).first()
    
    if not content_brief:
        raise HTTPException(status_code=404, detail="Content brief not found")
    
    return content_brief

def get_or_create_content_id(db: Session, content_brief: ContentBrief, user_id: int) -> int:
    if not content_brief.content_id:
        content_id = create_empty_content(db=db, user_id=user_id)
        content_brief.content_id = content_id
    else:
        content_id = content_brief.content_id    
    return content_id
