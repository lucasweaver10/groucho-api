from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from app.models.user import User

class ContentBriefTemplate(SQLModel, table=True):
    __tablename__ = "content_brief_templates"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    author_instructions: str
    writing_sample: str
    negative_words: Optional[str] = Field(default=None, max_length=200)
    product_info: Optional[str] = Field(default=None)
    call_to_action: Optional[str] = Field(default=None)
    user_id: int = Field(foreign_key="users.id", index=True)
    user: User = Relationship(back_populates="content_brief_templates")
    # Allow for additional custom key/value pairs
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)