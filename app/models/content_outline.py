from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentOutline(SQLModel, table=True):
    __tablename__ = "content_outlines"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    user_id: int = Field(index=True)
    content_brief_id: int = Field(foreign_key="content_briefs.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    content_brief: "ContentBrief" = Relationship(back_populates="outlines")
    content_outline_sections: List["ContentOutlineSection"] = Relationship(back_populates="outline")
    contents: List["Content"] = Relationship(back_populates="content_outline")