"""
Adapters for pydantic models.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import TypeAdapter

from py_play_money.schemas import (
    Activity,
    Market,
    MarketOption,
    MarketOptionPosition,
    User,
)

activity_list_adapter = TypeAdapter(list[Activity])
market_list_adapter = TypeAdapter(list[Market])
option_list_adapter = TypeAdapter(list[MarketOption])
position_list_adapter = TypeAdapter(list[MarketOptionPosition])
user_list_adapter = TypeAdapter(list[User])
