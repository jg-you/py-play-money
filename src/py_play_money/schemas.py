"""
Data schemas for the playmoney API.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class Market(BaseModel):
    """Market data."""

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


class LiteOption(BaseModel):
    """Option with only ID and probability."""

    id: str
    probability: int = Field(ge=0, le=100, description="Probability percentage (0-100).")


class Option(LiteOption):
    """Option for a market."""

    name: str
    marketId: str
    color: str
    liquidityProbability: float = Field(ge=0, le=1, description="Liquidity probability (0-1).")
    createdAt: datetime
    updatedAt: datetime

    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def parse_date(cls, value):
        """Parse date strings to datetime objects, before validation."""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value

    @field_validator('color', mode='after')
    @classmethod
    def validate_color(cls, value):
        """Validate that the color is a valid hex color code."""
        if not value.startswith("#") or len(value) != 7:
            raise ValueError("Color must be a valid hex code (e.g., '#FFFFFF').")
        return value


class MarketResolution(BaseModel):
    """Resolution for a market."""

    id: str
    marketId: str
    resolvedById: str
    resolutionId: str
    # Note: Cannot ask for a strict url, isn't validated fully on the frontend
    supportingLink: str | None = Field(default=None, repr=False)
    createdAt: datetime
    updatedAt: datetime
    resolution: Option

    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def parse_date(cls, value):
        """Parse date strings to datetime objects, before validation."""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value


class User(BaseModel):
    """User profile."""

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


class FullMarket(Market):
    """Full market data including options, users."""

    user: User = Field(repr=False)
    options: list[Option] = Field(default=[], repr=False)
    marketResolution: MarketResolution | None = Field(default=None, repr=False)
    resolvedBy: User | None = Field(default=None, repr=False)
    parentList: str | None = Field(default=None, repr=False)

    @model_validator(mode='after')
    def validate_resolution(self):
        """Validate that if the market is resolved, it has a resolution."""
        if self.marketResolution is None and self.resolvedAt is not None:
            raise ValueError("Market is resolved but has no market resolution.")
        return self

class Reaction(BaseModel):
    """Reaction to comments."""

    id: str
    emoji: str
    commentId: str
    user: User

    @field_validator('emoji', mode='after')
    @classmethod
    def validate_emoji(cls, value):
        """Validate that the emoji is a valid code."""
        if not value.startswith(":") or not value.endswith(":"):
            raise ValueError("Emoji must be in the format ':emoji_code:'")


class Comment(BaseModel):
    """Comment on a market."""

    id: str
    content: str
    createdAt: datetime
    updatedAt: datetime
    edited: bool
    authorId: str
    parentId: str | None = Field(default=None)
    hidden: bool
    entityId: str
    entityType: Literal["MARKET"]
    author: User
    reactions: list[Reaction] = Field(default=[])

    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def parse_date(cls, value):
        """Parse date strings to datetime objects, before validation."""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value


class GraphTick(BaseModel):
    """Tick for graph data."""

    startAt: datetime
    endAt: datetime
    options: list[LiteOption]

    @field_validator('startAt', 'endAt', mode='before')
    @classmethod
    def parse_date(cls, value):
        """Parse date strings to datetime objects, before validation."""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value


class PageInfo(BaseModel):
    """Cursor for pagination."""

    hasNextPage: bool = False
    endCursor: str | None = Field(default=None)
    total: int = Field(ge=0)
