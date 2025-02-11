from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from enum import Enum

class AIModel(SQLModel, table=True):
    __tablename__ = "ai_models"
    id: int = Field(primary_key=True)
    name: str
    provider_id: int = Field(foreign_key="ai_providers.id")    
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    #Relationships
    provider: "AIProvider" = Relationship(back_populates="models")