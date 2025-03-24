"""
Data schemas for the playmoney API.

Author: JGY <jeangabriel.young@gmail.com>
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl


class Market(BaseModel):
    """Represents a market in the playmoney API."""

    # Identifiers
    id: str = Field(description="The unique identifier for the market.")
    question: str = Field(description="Short title for the market.")
    description: str = Field(description="Detailed description.", repr=False)
    slug: str = Field(description="URL-friendly identifier.", repr=False)
    tags: list[str] = Field(
        default = [],
        description="List of tags associated with the market.",
        repr=False
    )
    @property
    def url(self) -> str:
        """Generate the URL for the market."""
        return f"https://playmoney.dev/questions/{self.id}/{self.slug}"

    # Dates
    createdAt: datetime
    closeDate: datetime
    resolvedAt: datetime | None = Field(default=None, repr=False)
    canceledAt: datetime | None = Field(default=None, repr=False)
    updatedAt: datetime | None = Field(default=None, repr=False)

    # User IDs
    createdBy: str = Field(
        description="ID of the user who created the market.",
        repr=False
    )
    ammAccountId: str = Field(
        description="ID of the Automated Market Maker associated with the market.",
    repr=False
    )
    clearingAccountId: str = Field(
        description="ID of the clearing account for the market.",
        repr=False
    )
    canceledById: str | None = Field(
        description="ID of the user who canceled the market.",
        default=None,
        repr=False
    )

    # Activity
    commentCount: int = Field(ge=0, repr=False)
    uniqueTradersCount: int = Field(ge=0, repr=False)
    uniquePromotersCount: int = Field(ge=0, repr=False)
    liquidityCount: int = Field(ge=0, repr=True)
    parentListId: str | None = Field(default=None, repr=False)

    # Validators
    @field_validator(
        'createdAt', 'closeDate', 'resolvedAt', 'canceledAt', 'updatedAt',
        mode='before'
    )
    @classmethod
    def parse_date(cls, value):
        """Parse date strings to datetime objects, before validation."""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value

    @model_validator(mode='after')
    def validate_creation_date(self):
        """Validate that the creation date is not after the close date."""
        if self.createdAt > self.closeDate:
            raise ValueError("Creation date cannot be after the close date.")
        return self

class User(BaseModel):
    """Represents a user in the playmoney API."""
    id: str = Field(description="Unique identifier for the user.")
    username: str
    displayName: str
    avatarUrl: HttpUrl | None = Field(default=None, repr=False)
    twitterHandle: HttpUrl | None = Field(default=None, repr=False)
    discordHandle: HttpUrl | None = Field(default=None, repr=False)
    website: HttpUrl | None = Field(default=None, repr=False)
    bio: str | None = Field(default=None, repr=False)
    timezone: str
    primaryAccountId: str = Field(description="ID of the user's primary account.")
    role: Literal["USER", "ADMIN"]
    referralCode: str | None = Field(default=None, repr=False)
    referredBy: str | None = Field(default=None, repr=False)
    createdAt: datetime
    updatedAt: datetime

    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def parse_date(cls, value):
        """Parse date strings to datetime objects, before validation."""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value
