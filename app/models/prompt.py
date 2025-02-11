from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from enum import Enum

class TypeEnum(str, Enum):
    user = "user"
    system = "system"

class Prompt(SQLModel, table=True):
    __tablename__ = "prompts"
    id: int = Field(primary_key=True)
    title: str
    description: Optional[str] = None
    type: TypeEnum = Field(default=TypeEnum.user)
    prompt: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    