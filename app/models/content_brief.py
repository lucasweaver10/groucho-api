from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentBrief(SQLModel, table=True):
    __tablename__ = "content_briefs"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    # Allow for additional custom key/value pairs.
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    primary_keyword: Optional[str] = Field(default=None, max_length=200)
    secondary_keywords: Optional[str] = Field(default=None)
    author_instructions: str
    writing_sample: str
    negative_words: Optional[str] = Field(default=None, max_length=200)
    suggested_word_count: Optional[int] = None
    product_info: Optional[str] = Field(default=None)
    call_to_action: Optional[str] = Field(default=None)

    user_id: int = Field(foreign_key="users.id", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships: A content brief may have multiple outlines and generated contents.
    outlines: List["ContentOutline"] = Relationship(back_populates="content_brief")
    contents: List["Content"] = Relationship(back_populates="content_brief")
    user: "User" = Relationship(back_populates="content_briefs")