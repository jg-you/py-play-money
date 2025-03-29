"""
Small utility models.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import Field

from py_play_money.schemas.base_types import CamelCaseModel


class PageInfo(CamelCaseModel):
    """Cursor for pagination."""

    has_next_page: bool = False
    end_cursor: str | None = None
    total: int = Field(ge=0)
