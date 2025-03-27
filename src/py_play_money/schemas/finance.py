"""
All finance-related schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from py_play_money.schemas.base_types import CUID, IsoDatetime
from py_play_money.schemas.user import User

AssetType = Literal["MARKET_OPTION", "CURRENCY"]

TransactionType = Literal[
    "TRADE_BUY",
    "TRADE_SELL",
    "TRADE_WIN",
    "TRADE_SELL",
    "CREATOR_TRADER_BONUS",
    "LIQUIDITY_INITIALIZE",
    "LIQUIDITY_DEPOSIT",
    "LIQUIDITY_WITHDRAWAL",
    "LIQUIDITY_RETURNED",
    "LIQUIDITY_VOLUME_BONUS",
    "DAILY_TRADE_BONUS",
    "DAILY_MARKET_BONUS",
    "DAILY_COMMENT_BONUS",
    "DAILY_LIQUIDITY_BONUS",
    "HOUSE_GIFT",
    "HOUSE_SIGNUP_BONUS",
    "REFERRER_BONUS",
    "REFERREE_BONUS",
]

class Position(BaseModel):
    """Position on a market."""

    id: CUID
    accountId: CUID
    marketId: CUID
    optionId: CUID
    cost: float
    quantity: float
    value: float = Field(ge=0)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime

    @model_validator(mode='after')
    def validate_update_date(self):
        """Validate that the creation date is not after the update date."""
        if self.createdAt > self.updatedAt:
            raise ValueError("Creation date cannot be after the update date.")
        return self



class TransactionEntry(BaseModel):
    """Ledger entry for a transaction."""

    id: CUID
    amount: float
    assetType: AssetType
    assetId: Literal["PRIMARY"] | CUID
    fromAccountId: CUID
    toAccountId: CUID
    transactionId: CUID
    createdAt: IsoDatetime


class Transaction(BaseModel):
    """Transaction."""

    id: CUID
    type: TransactionType
    initiatorId: CUID
    isReverse: bool | None = Field(default=None)
    reverseOfId: CUID | None = Field(default=None)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    batchId: CUID | None = Field(default=None)
    marketId: CUID
    entries: list[TransactionEntry]
    initiator: User
