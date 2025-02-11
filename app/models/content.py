from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class Content(SQLModel, table=True):
    __tablename__ = "contents"
    id: int = Field(primary_key=True)
    title: str
    type: str = Field(default="blog_post")
    description: Optional[str] = None    
    text: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    content_brief_id: int = Field(foreign_key="content_briefs.id")
    content_outline_id: int = Field(foreign_key="content_outlines.id")
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    content_brief: "ContentBrief" = Relationship(back_populates="contents")
    content_outline: "ContentOutline" = Relationship(back_populates="contents")
    content_sections: List["ContentSection"] = Relationship(back_populates="content")
    user: "User" = Relationship(back_populates="contents")