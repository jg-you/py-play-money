"""
Comment schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import field_validator

from py_play_money.schemas.base_types import CUID, CamelCaseModel, DateModel, IsoDatetime

CommentEntityType = Literal["MARKET", "COMMENT", "LIST"]


class Comment(DateModel):
    """Comment on a market."""

    entity_type: CommentEntityType
    id: CUID
    content: str
    edited: bool = False
    author_id: CUID
    parent_id: CUID | None = None
    hidden: bool = False
    entity_id: CUID
    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None


class CommentReaction(CamelCaseModel):
    """Reaction to comments."""

    id: CUID
    emoji: str
    user_id: CUID
    comment_id: CUID

    @field_validator('emoji', mode='after')
    @classmethod
    def validate_emoji(cls, value):
        """Validate that the emoji is a valid code."""
        if value is None:
            return value
        if not isinstance(value, str):
            return value
        if not value.startswith(":") or not value.endswith(":"):
            raise ValueError("Emoji must be in the format ':emoji_code:'")
        return value
