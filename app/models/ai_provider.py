from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from enum import Enum

class AIProvider(SQLModel, table=True):
    __tablename__ = "ai_providers"
    id: int = Field(primary_key=True)
    name: str
    api_endpoint: str
    pydantic_ai_wrapper: str = Field(default="OpenAI")
    is_openai_compatible: bool = Field(default=False)
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    models: List["AIModel"] = Relationship(back_populates="provider")