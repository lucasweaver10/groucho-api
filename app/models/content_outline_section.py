from typing import Optional, List, Dict, Any
from datetime import datetime
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    content_outline: "ContentOutline" = Relationship(back_populates="content_outline_sections")
    content_sections: List["ContentSection"] = Relationship(back_populates="content_outline_section")