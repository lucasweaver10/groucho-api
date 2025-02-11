from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.content import Content
from app.models.content_outline_section import ContentOutlineSection
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentSection(SQLModel, table=True):
    __tablename__ = "content_sections"
    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key="content.id")
    content_outline_section_id: int = Field(foreign_key="content_outline_sections.id")
    # Use an order field to sequence sections (if not using the natural order of IDs)
    order: int = Field(default=0)
    # The context used for prompting the AI – for traceability and for potential revisions.
    prompt_context: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    # The actual AI-generated markdown text.
    text: str
    # Any additional metadata (timestamps, status flags, etc.)
    metadata: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    # Revision history – an array of past versions (could include timestamp, previous text, etc.)
    revision_history: List[Dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    content: Content = Relationship(back_populates="content_sections")
    content_outline_section: ContentOutlineSection = Relationship(back_populates="content_sections")