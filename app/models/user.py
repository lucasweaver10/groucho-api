from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stripe_customer_id: Optional[str] = Field(default=None, unique=True)
    stripe_subscription_id: Optional[str] = Field(default=None, unique=True)
    stripe_product_id: Optional[str] = None
    stripe_price_id: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_end_date: Optional[datetime] = None
    lifetime_access: bool = Field(default=False)
    total_paid: float = Field(default=0.0)

    # Relationships
    content_briefs: List["ContentBrief"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    content_brief_templates: List["ContentBriefTemplate"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    contents: List["Content"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    content_series: List["ContentSeries"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    content_outlines: List["ContentOutline"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def has_premium_access(self) -> bool:
        """
        Check if the user has premium access based on their subscription status or lifetime access.
        Returns True if the user has an active subscription or lifetime access.
        """
        return self.subscription_status == "active" or self.lifetime_access