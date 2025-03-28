"""
Small utility models.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import BaseModel, Field

from py_play_money.schemas.base_types import IsoDatetime


class GraphTick(BaseModel):
    """Tick for graph data."""

    start_at: IsoDatetime
    end_at: IsoDatetime
    # options: list[LiteOption]


class PageInfo(BaseModel):
    """Cursor for pagination."""

    has_next_page: bool = False
    end_cursor: str | None = None
    total: int = Field(ge=0)
