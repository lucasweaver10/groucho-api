from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentOutline(SQLModel, table=True):
    __tablename__ = "content_outlines"
    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: Optional[int] = Field(foreign_key="contents.id", nullable=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    description: Optional[str] = None    
    custom_data: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    content_brief_id: int = Field(foreign_key="content_briefs.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    content_brief: "ContentBrief" = Relationship(back_populates="outline")
    content_outline_sections: List["ContentOutlineSection"] = Relationship(back_populates="content_outline")
    content: Optional["Content"] = Relationship(back_populates="content_outline")
    user: "User" = Relationship(back_populates="content_outlines")