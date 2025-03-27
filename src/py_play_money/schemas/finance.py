"""
All finance-related schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import Field, Json

from py_play_money.schemas.base_types import CUID, IsoDatetime, CamelCaseModel, DateModel

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


class Position(DateModel):
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


class Transaction(DateModel):
    """Transaction."""

    type: TransactionType
    id: CUID
    initiator_id: CUID
    is_reverse: bool | None = None
    reverse_of_id: CUID | None = None
    batch_id: CUID | None = None
    market_id: CUID | None = None
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


class TransactionEntry(CamelCaseModel):
    """Ledger entry for a transaction."""

    asset_type: AssetType
    id: CUID
    amount: float
    asset_id: Literal["PRIMARY"] | CUID
    from_account_id: CUID
    to_account_id: CUID
    transactionId: CUID
    created_at: IsoDatetime


class Balance(DateModel):
    """Account balance."""

    asset_type: AssetType
    id: CUID
    account_id: CUID
    asset_id: Literal["PRIMARY"] | CUID
    total: float
    subtotals: Json
    market_id: CUID | None = None
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None
