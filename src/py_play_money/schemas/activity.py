"""
Schemas for all social features.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import BaseModel

from py_play_money.schemas.base_types import IsoDatetime


ActivityType = Literal[
    "COMMENT", 
    "TRADE_TRANSACTION",
    "LIQUIDITY_TRANSACTION",
    "MARKET_CREATED",
    "MARKET_RESOLVED"
]

NotificationType = Literal [
    "MARKET_RESOLVED",
    "MARKET_CANCELED",
    "MARKET_TRADE",
    "MARKET_LIQUIDITY_ADDED",
    "MARKET_COMMENT",

    "LIST_COMMENT",
    "LIST_MARKET_ADDED",

    "COMMENT_REPLY",
    "COMMENT_MENTION",
    "COMMENT_REACTION",

    "REFERRER_BONUS",
]


class Activity(BaseModel):
    """Activity data."""

    type: ActivityType
    timestampAt: IsoDatetime

    # Optional fields, will be removed by mixin if not present
    comment: Comment | None = None
    transactions: list[Transaction] | None = None
    option: Option | None = None
    market: FullMarket | None = None
    marketResolution: MarketResolution | None = None
