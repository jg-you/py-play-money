"""
Compound schemas for various API endpoints.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import TypeAdapter, field_validator, model_validator
from typing_extensions import Self

from py_play_money.schemas.comments import Comment, CommentReaction
from py_play_money.schemas.market import Market, MarketOption, MarketOptionPosition
from py_play_money.schemas.user import Account, User


class CommentReactionView(CommentReaction):
    """View of a comment reaction with user information."""

    user: User

    @field_validator('user', mode='after')
    @classmethod
    def validate_user(cls, value, info) -> str:
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


class AccountView(Account):
    """View of an account with user information."""

    user: User

    @field_validator('user', mode='after')
    @classmethod
    def validate_account(cls, value, info) -> str:
        """Ensure account_id matches account data."""
        if value.primary_account_id != info.data.get('id'):
            raise ValueError(
                "Account ID does not match the provided account data."
                f"{value.id} != {info.data.get('account_id')}"
            )
        return value

class MarketOptionPositionView(MarketOptionPosition):
    """View of a market option position with user information."""

    account: AccountView
    market: Market
    option: MarketOption

    @model_validator(mode='after')
    def validate_market_ids(self) -> Self:
        """Ensure market_id matches the market data."""
        if self.market.id != self.market_id:
            raise ValueError(
                "Market ID does not match the provided market data."
                f"{self.market.id} != {self.market_id}"
            )
        if self.market_id != self.option.market_id:
            raise ValueError(
                "Market ID does not match the option's market_id."
                f"{self.market_id} != {self.option.market_id}"
            )
        if self.account.id != self.account_id:
            raise ValueError(
                "Account ID does not match the provided account data."
                f"{self.account.id} != {self.account_id}"
            )
        if self.option.id != self.option_id:
            raise ValueError(
                "Option ID does not match the provided option data."
                f"{self.option.id} != {self.option_id}"
            )
        return self

comment_list_adapter = TypeAdapter(list[CommentView])
market_option_position_list_adapter = TypeAdapter(list[MarketOptionPositionView])
