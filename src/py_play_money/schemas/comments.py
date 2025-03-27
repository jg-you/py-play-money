"""
Comment schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from py_play_money.schemas.base_types import CUID, IsoDatetime
from py_play_money.schemas.user import User

CommentEntityType = Literal["MARKET", "COMMENT"]

class Reaction(BaseModel):
    """Reaction to comments."""

    id: CUID
    emoji: str
    userId: CUID
    commentId: CUID
    user: User

    @field_validator('emoji', mode='after')
    @classmethod
    def validate_emoji(cls, value):
        """Validate that the emoji is a valid code."""
        if not value.startswith(":") or not value.endswith(":"):
            raise ValueError("Emoji must be in the format ':emoji_code:'")


class Comment(BaseModel):
    """Comment on a market."""

    id: CUID
    content: str
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    edited: bool
    authorId: CUID
    parentId: CUID | None = Field(default=None)
    hidden: bool
    entityId: CUID
    entityType: CommentEntityType
    author: User
    reactions: list[Reaction] = Field(default=[])
