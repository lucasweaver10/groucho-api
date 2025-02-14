from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentSection(SQLModel, table=True):
    __tablename__ = "content_sections"
    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key="contents.id")
    content_outline_section_id: int = Field(foreign_key="content_outline_sections.id")
    # Use an order field to sequence sections (if not using the natural order of IDs)
    order: int = Field(default=0)        
    text: str    
    custom_data: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )    
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    content: "Content" = Relationship(back_populates="content_sections")
    content_outline_section: "ContentOutlineSection" = Relationship(back_populates="content_sections")