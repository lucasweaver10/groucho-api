from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class Content(SQLModel, table=True):
    __tablename__ = "contents"
    id: int = Field(primary_key=True)
    content_series_id: Optional[int] = Field(foreign_key="content_series.id", nullable=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: Optional[str] = None
    type: str = Field(default="blog_post")
    description: Optional[str] = None    
    text: Optional[str] = None
    # Any additional metadata (status flags, etc.)
    custom_data: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    content_brief: Optional["ContentBrief"] = Relationship(back_populates="content")
    content_outline: Optional["ContentOutline"] = Relationship(back_populates="content")
    content_sections: List["ContentSection"] = Relationship(back_populates="content")
    user: "User" = Relationship(back_populates="contents")
    series: Optional["ContentSeries"] = Relationship(back_populates="contents")