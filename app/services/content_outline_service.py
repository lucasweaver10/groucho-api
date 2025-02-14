from app.models.content_outline import ContentOutline 
from app.models.content_outline_section import ContentOutlineSection
from fastapi import Depends, HTTPException, Path
from ..dependencies import get_db

def create(
    db: Session,
    user_id: int
) -> int:
    content_outline = ContentOutline()
    db.add(content_outline)
    db.commit()
    db.refresh(content_outline)
    return content_outline.id

def get_content_outline_by_id(
    db: Session = Depends(get_db),
    content_outline_id: int = Path(...),
):
    content_outline = db.query(ContentOutline).filter(
        ContentOutline.id == content_outline_id
    ).first()
    
    if not content_outline:
        raise HTTPException(status_code=404, detail="Content outline not found")
    
    return content_outline

def get_content_outline_section_by_id(
    db: Session = Depends(get_db),
    content_outline_section_id: int = Path(...),
):
    content_outline_section = db.query(ContentOutlineSection).filter(
        ContentOutlineSection.id == content_outline_section_id
    ).first()
    
    if not content_outline_section:
        raise HTTPException(status_code=404, detail="Content outline section not found")
    
    return content_outline_section