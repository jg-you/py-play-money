"""
User-related schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import BaseModel, Field

from .base_types import CUID, IsoDatetime

AccountType = Literal["USER", "MARKET_AMM", "MARKET_CLEARING", "HOUSE"]

UserRoleType = Literal["USER", "ADMIN"]


class User(BaseModel):
    """User profile."""

    id: CUID
    username: str
    displayName: str
    avatarUrl: str | None = Field(default=None)
    twitterHandle: str | None = Field(default=None)
    discordHandle: str | None = Field(default=None)
    website: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    timezone: str
    primaryAccountId: CUID
    role: UserRoleType
    referralCode: str | None = Field(default=None)
    referredBy: CUID | None = Field(default=None)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime



class Account(BaseModel):
    """Account for a user."""

    type: AccountType
    id: CUID
    internalType: str | None = None
    userId: CUID | None = None
    marketId: CUID | None = None
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    # user: User | None = None
    # market: Market | None = None