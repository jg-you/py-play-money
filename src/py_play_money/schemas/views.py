"""
Compound schemas for various API endpoints.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import TypeAdapter, field_validator

from py_play_money.schemas.comments import Comment, CommentReaction
from py_play_money.schemas.user import User


class CommentReactionView(CommentReaction):
    """View of a comment reaction with user information."""

    user: User

    @field_validator('user', mode='after')
    @classmethod
    def validate_user(cls, value, info):
        """Ensure user_id matches user data."""
        user_id = info.data.get('user_id')
        if user_id != value.id:
            raise ValueError(
                f"User ID does not match the provided user data. {user_id} != {value.id}"
            )
        return value


class CommentView(Comment):
    """View of a comment with reactions and user information."""

    author: User
    reactions: list[CommentReactionView] = []


comment_list_adapter = TypeAdapter(list[CommentView])
