"""
Market-related schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import re
from typing import Literal

from pydantic import Field, field_validator

from py_play_money.schemas.base_types import CUID, DateModel, IsoDatetime

ContributionPolicyType = Literal[
    "PUBLIC",
    "DISABLED",
    "OWNERS_ONLY",
    "FRIENDS_ONLY"
]


class Market(DateModel):
    """Market data."""

    # Identifiers
    id: CUID
    question: str
    description: str
    slug: str
    parent_list_id: CUID | None = None
    tags: list[str] = []

    # Dates
    created_at: IsoDatetime
    close_date: IsoDatetime | None = None
    resolved_at: IsoDatetime | None = None
    canceled_at: IsoDatetime | None = None
    updated_at: IsoDatetime | None = None

    # User IDs
    created_by: CUID
    amm_account_id: CUID
    clearing_account_id: CUID
    canceled_by_id: CUID | None = None

    # Activity
    comment_count: int = Field(ge=0)
    unique_traders_count: int = Field(ge=0)
    unique_promoters_count: int = Field(ge=0)
    liquidity_count: int | None = Field(ge=0, default=None)


# Note: This is renamed from `List` to `MarketList` to avoid conflicts with the `List` type.
class MarketList(DateModel):
    """List of markets."""

    id: CUID
    title: str
    slug: str
    description: str | None = None
    owner_id: CUID
    contribution_policy: ContributionPolicyType
    contribution_review: bool | None = None
    tags: list[str] = []
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


class MarketResolution(DateModel):
    """Resolution for a market."""

    id: CUID
    market_id: CUID
    resolved_by_id: CUID
    resolution_id: CUID
    supporting_link: str | None = None
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


class MarketOption(DateModel):
    """Option for a market."""

    id: CUID
    name: str
    market_id: CUID
    color: str
    liquidity_probability: float = Field(ge=0, le=1)
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None
    probability: int | None = Field(
        ge=0,
        le=100,
        description="Probability percentage (0-100).",
        default=None
    )

    @field_validator('color', mode='after')
    @classmethod
    def validate_color(cls, value):
        """Validate that the color is a valid hex color code."""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise ValueError("Color must be a valid hex code (e.g., '#FFFFFF').")
        return value


class MarketOptionPosition(DateModel):
    """Position on a market."""

    id: CUID
    account_id: CUID
    market_id: CUID
    option_id: CUID
    cost: float
    quantity: float
    value: float = Field(ge=0)
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None
