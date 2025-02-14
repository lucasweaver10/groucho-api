from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentOutlineSection(SQLModel, table=True):
    __tablename__ = "content_outline_sections"
    id: Optional[int] = Field(default=None, primary_key=True)
    content_outline_id: int = Field(foreign_key="content_outlines.id")     
    text: str
    custom_data: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    # Use an order field to sequence sections (if not using the natural order of IDs)
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    content_outline: "ContentOutline" = Relationship(back_populates="content_outline_sections")
    content_sections: List["ContentSection"] = Relationship(back_populates="content_outline_section")