from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field

class Upload(SQLModel, table=True):
    __tablename__ = "uploads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    file_path: str
    original_filename: str
    file_size: int
    mime_type: str
    description: Optional[str] = None
    upload_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Remove the relationship with User but keep the foreign key 