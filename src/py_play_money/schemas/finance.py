"""
All finance-related schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import TypeAdapter

from py_play_money.schemas.base_types import (
    CUID,
    CamelCaseModel,
    ConstantsTypeModel,
    DateModel,
    IsoDatetime,
)

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


class Subtotals(ConstantsTypeModel):
    """Balance subtotals."""

    creator_trader_bonus: float = 0.0
    daily_trade_bonus: float = 0.0
    daily_market_bonus: float = 0.0
    daily_comment_bonus: float = 0.0
    daily_liquidity_bonus: float = 0.0
    house_signup_bonus: float = 0.0
    liquidity_deposit: float = 0.0
    liquidity_initialize: float = 0.0
    liquidity_returned: float = 0.0
    liquidity_volume_bonus: float = 0.0
    trade_buy: float = 0.0
    trade_loss: float = 0.0
    trade_win: float = 0.0
    trade_sell: float = 0.0


class UserBalance(DateModel):
    """Balance for a user's account."""

    id: CUID
    account_id: CUID
    asset_type: AssetType
    asset_id: Literal["PRIMARY"] | CUID
    total: float
    subtotals: Subtotals
    market_id: CUID | None = None
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None

    # @model_validator(mode='after')
    # def validate_balance(self) -> Self:
    #     """Ensure subtotals match total."""
    #     total_subtotals = sum(self.subtotals.model_dump().values())
    #     if abs(self.total - total_subtotals) > 0.01:
    #         raise ValueError(
    #             "Total is not close to the sum of subtotals."
    #             f"{self.total} != {total_subtotals}"
    #         )
    #     return self

class MarketBalance(DateModel):
    """Balances for a market's AMM."""

    id: CUID
    account_id: CUID
    asset_type: AssetType
    asset_id: Literal["PRIMARY"] | CUID
    total: float
    subtotals: Subtotals
    market_id: CUID
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


# Type adapters for serialization
market_balances_adapter = TypeAdapter(list[MarketBalance])
