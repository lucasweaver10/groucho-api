from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class ContentSeries(SQLModel, table=True):
    __tablename__ = "content_series"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    description: Optional[str] = None
    custom_data: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    contents: List["Content"] = Relationship(back_populates="series")
    user: "User" = Relationship(back_populates="content_series")