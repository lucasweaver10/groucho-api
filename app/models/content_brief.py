from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentBrief(SQLModel, table=True):
    __tablename__ = "content_briefs"
    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: Optional[int] = Field(foreign_key="contents.id", nullable=True)
    content_brief_template_id: Optional[int] = Field(foreign_key="content_brief_templates.id")
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    description: Optional[str] = None    
    primary_keyword: Optional[str] = Field(default=None, max_length=200)
    secondary_keywords: Optional[str] = Field(default=None)
    author_instructions: Optional[str] = None
    writing_sample: Optional[str] = None
    negative_words: Optional[str] = Field(default=None, max_length=200)
    suggested_word_count: Optional[int] = None
    product_info: Optional[str] = Field(default=None)
    call_to_action: Optional[str] = Field(default=None)    
    custom_data: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="content_briefs")
    outline: "ContentOutline" = Relationship(back_populates="content_brief")
    content: "Content" = Relationship(back_populates="content_brief")