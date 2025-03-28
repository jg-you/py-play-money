"""
Small utility models.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import BaseModel, Field


class PageInfo(BaseModel):
    """Cursor for pagination."""

    has_next_page: bool = False
    end_cursor: str | None = None
    total: int = Field(ge=0)
