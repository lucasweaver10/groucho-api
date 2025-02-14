from datetime import datetime
from sqlalchemy.orm import Session
from ..models.content import Content

def create(
    db: Session,
    user_id: int
) -> int:
    content = Content(                
        type="blog_post",
        user_id=user_id        
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content.id

def get(
    db: Session,
    content_id: int
) -> Content:
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

# create a new empty content object and return the id
def create_empty_content(
    db: Session,
    user_id: int
) -> int:
    content = Content(                
        type="blog_post",
        user_id=user_id        
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content.id