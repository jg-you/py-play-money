"""
Market-related schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from py_play_money.schemas.base_types import CUID, IsoDatetime
from py_play_money.schemas.user import User

ContributionPolicyType = Literal[
    "PUBLIC",
    "DISABLED",
    "OWNERS_ONLY",
    "FRIENDS_ONLY"
]


class Market(BaseModel):
    """Market data."""

    # Identifiers
    id: CUID
    question: str
    description: str
    slug: str
    tags: list[str] = Field(
        default=[]
    )

    # Dates
    createdAt: IsoDatetime
    closeDate: IsoDatetime
    resolvedAt: IsoDatetime | None = Field(default=None)
    canceledAt: IsoDatetime | None = Field(default=None)
    updatedAt: IsoDatetime | None = Field(default=None)

    # User IDs
    createdBy: CUID
    ammAccountId: CUID
    clearingAccountId: CUID
    canceledById: CUID | None = None

    # Activity
    commentCount: int = Field(ge=0)
    uniqueTradersCount: int = Field(ge=0)
    uniquePromotersCount: int = Field(ge=0)
    liquidityCount: int | None = Field(ge=0, default=None)
    parentListId: CUID | None = None

    # Validators
    @model_validator(mode='after')
    def validate_creation_date(self):
        """Validate that the creation date is not after the close date."""
        if self.createdAt > self.closeDate:
            raise ValueError("Creation date cannot be after the close date.")
        return self


class LiteOption(BaseModel):
    """Option with only ID and probability."""

    id: CUID
    probability: int | None = Field(
        ge=0,
        le=100,
        description="Probability percentage (0-100).",
        default=None  # for compatibility with older versions
    )


class Option(LiteOption):
    """Option for a market."""

    name: str
    marketId: CUID
    color: str
    liquidityProbability: float = Field(ge=0, le=1)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime

    @field_validator('color', mode='after')
    @classmethod
    def validate_color(cls, value):
        """Validate that the color is a valid hex color code."""
        if not value.startswith("#") or len(value) != 7:
            raise ValueError("Color must be a valid hex code (e.g., '#FFFFFF').")
        return value


class MarketResolution(BaseModel):
    """Resolution for a market."""

    id: CUID
    marketId: CUID
    resolvedById: CUID
    resolutionId: CUID
    supportingLink: str | None = Field(default=None)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    resolution: Option
    resolvedBy: User
    market: Market


class FullMarket(Market):
    """Full market data including options, users."""

    def __init__(self, **data):
        """Remove optional fields for some use cases of the model."""
        super().__init__(**data)
        for field in self.model_fields:
            if field not in self.model_fields_set:
                if field in {"resolvedBy", "parentList", "sharedTagsCount", "options", "marketResolution"}:
                    self.__dict__.pop(field, None)

    user: User
    options: list[Option] = Field(default=[])
    marketResolution: MarketResolution | None = Field(default=None)
    resolvedBy: User | None = Field(default=None)
    parentList: str | None = Field(default=None)
    sharedTagsCount: int = Field(default=None)


class MarketList(BaseModel):
    """List of markets."""

    id: CUID
    title: str
    slug: str
    description: str
    ownerId: CUID
    contributionPolicy: ContributionPolicyType
    contributionReview: bool
    tags: list[str]
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
