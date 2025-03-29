"""
Graph models.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import TypeAdapter, model_validator

from py_play_money.schemas.base_types import CUID, CamelCaseModel, IsoDatetime


class GraphTickOption(CamelCaseModel):
    """Option information for a graph tick."""

    id: CUID
    probability: int

class MarketGraphTick(CamelCaseModel):
    """Ticks of a market graph."""

    start_at: IsoDatetime
    end_at: IsoDatetime
    options: list[GraphTickOption]

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that the start date is not after the end_date."""
        if self.start_at > self.end_at:
            raise ValueError("Start date cannot be after the end_date.")
        return self


class MarketListGraphTick(CamelCaseModel):
    """Ticks of a list graph."""

    start_at: IsoDatetime
    end_at: IsoDatetime
    markets: list[GraphTickOption]

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that the start date is not after the end_date."""
        if self.start_at > self.end_at:
            raise ValueError("Start date cannot be after the end_date.")
        return self


class UserGraphTick(CamelCaseModel):
    """Ticks of a user graph."""

    start_at: IsoDatetime
    end_at: IsoDatetime
    balance: float
    liquidity: float
    markets: float

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that the start date is not after the end_date."""
        if self.start_at > self.end_at:
            raise ValueError("Start date cannot be after the end_date.")
        return self

# Type adapters for serialization
market_graph_ticks_adapter = TypeAdapter(list[MarketGraphTick])
market_list_graph_ticks_adapter = TypeAdapter(list[MarketListGraphTick])
user_graph_ticks_adapter = TypeAdapter(list[UserGraphTick])
