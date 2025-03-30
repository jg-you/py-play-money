"""
User-related schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import TypeAdapter

from py_play_money.schemas.base_types import CUID, CamelCaseModel, DateModel, IsoDatetime

AccountType = Literal["USER", "MARKET_AMM", "MARKET_CLEARING", "HOUSE"]

UserRoleType = Literal["USER", "ADMIN"]


class User(DateModel):
    """User profile."""

    role: UserRoleType
    id: CUID
    username: str
    display_name: str
    avatar_url: str | None
    twitter_handle: str | None
    discord_handle: str | None
    website: str | None
    bio: str | None
    timezone: str
    primary_account_id: CUID
    referral_code: str | None
    referred_by: CUID | None
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


class Account(DateModel):
    """Account for a user."""

    type: AccountType
    id: CUID
    internal_type: str | None = None
    user_id: CUID | None = None
    market_id: CUID | None = None
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


class UserQuest(CamelCaseModel):
    """User quests."""

    title: str
    award: int
    completed: bool
    href: str

class UserStatistics(CamelCaseModel):
    """Usage statistics for user."""

    net_worth: float
    trading_volume: float
    total_markets: int
    last_trade_at: IsoDatetime | None = None
    active_day_count: int
    other_income: float | None = None
    quests: list[UserQuest]

# Type adapters for serialization
users_adapter = TypeAdapter(list[User])
