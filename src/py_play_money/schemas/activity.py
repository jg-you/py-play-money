"""
Schemas for all social features.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import HttpUrl, Json

from py_play_money.schemas.base_types import CUID, CamelCaseModel, DateModel, IsoDatetime

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

class Notification(DateModel):
    """Notification data."""

    type: NotificationType
    id: CUID
    recipient_id: CUID
    actor_id: CUID
    content: Json | None
    market_id: CUID | None
    market_option_id: CUID | None
    market_resolution_id: CUID | None
    transaction_id: CUID | None
    list_id: CUID | None
    comment_id: CUID | None
    parent_comment_id: CUID | None
    comment_reaction_id: CUID | None
    action_url: HttpUrl
    read_at: IsoDatetime | None = None
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


# class NotificationGroup(DateModel):
#     """Notification group data."""

#     type: NotificationType
#     id: CUID
#     recipient_id: CUID
#     count: int = Field(ge=0, default=0)
#     last_notification_id: CUID
#     group_window_end: IsoDatetime
#     group_key: str
#     created_at: IsoDatetime
#     updated_at: IsoDatetime


class Activity(CamelCaseModel):
    """Activity data."""

    type: ActivityType
    timestamp_at: IsoDatetime

#     # Optional fields, will be removed by mixin if not present
#     comment: Comment | None = None
#     transactions: list[Transaction] | None = None
#     option: Option | None = None
#     market: FullMarket | None = None
#     marketResolution: MarketResolution | None = None
