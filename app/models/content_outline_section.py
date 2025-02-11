from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.content_outline import ContentOutline
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentOutlineSection(SQLModel, table=True):
    __tablename__ = "content_outline_sections"
    id: Optional[int] = Field(default=None, primary_key=True)
    content_outline_id: int = Field(foreign_key="content_outlines.id")    
    # Use an order field to sequence sections (if not using the natural order of IDs)
    order: int = Field(default=0)
    # Allow for nested sections by self-referencing.
    parent_id: Optional[int] = Field(default=None, foreign_key="content_outline_sections.id")

    content_outline: ContentOutline = Relationship(back_populates="content_outline_sections")
    children: List["ContentOutlineSection"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"remote_side": "ContentOutlineSection.id"},
    )
    parent: Optional["ContentOutlineSection"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "ContentOutlineSection.id"},
    )