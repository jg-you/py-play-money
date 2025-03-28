"""
View schemas for API endpoints.

Created by extending the base schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import TypeAdapter, field_validator, model_validator
from typing_extensions import Self

from py_play_money.schemas.comments import Comment, CommentReaction
from py_play_money.schemas.finance import UserBalance
from py_play_money.schemas.market import (
    Market,
    MarketList,
    MarketOption,
    MarketOptionPosition,
    MarketResolution,
)
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

    user_primary: User

    @model_validator(mode='before')
    @classmethod
    def process_input_data(cls, data):
        """Rename user to user_primary if needed."""
        if 'user' in data and 'user_primary' not in data:
            data['userPrimary'] = data.pop('user')
        return data

    @model_validator(mode='after')
    def validate_account(self) -> Self:
        """Ensure account_id matches account data."""
        if self.user_primary.primary_account_id != self.id:
            raise ValueError(
                "primary_account_id does not match user_primary.id."
                f"{self.id} != {self.user_primary.primary_account_id}"
            )
        return self

class UserBalanceView(UserBalance):
    """View of a final market balances."""

    account: AccountView

    @model_validator(mode='after')
    def validate_account(self) -> Self:
        if self.account.id != self.account_id:
            raise ValueError(
                "account_id does not match the account.id."
                f"{self.account.id} != {self.account_id}"
            )
        return self


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
                "marked_id does not match market.id."
                f"{self.market.id} != {self.market_id}"
            )
        if self.market_id != self.option.market_id:
            raise ValueError(
                "The option's market_id does not not match market.id."
                f"{self.market_id} != {self.option.market_id}"
            )
        if self.account.id != self.account_id:
            raise ValueError(
                "account_id does not match account.id."
                f"{self.account.id} != {self.account_id}"
            )
        if self.option.id != self.option_id:
            raise ValueError(
                "option_id does not match option.id."
                f"{self.option.id} != {self.option_id}"
            )
        return self


class MarketView(Market):
    """Augmented view of a market."""

    user: User
    options: list[MarketOption]
    market_resolution: MarketResolution | None = None
    parent_list: MarketList | None = None
    shared_tags_count: int = 0

    @model_validator(mode='before')
    @classmethod
    def process_input_data(cls, data):
        """Remove shared_tags_count if not provided. Handles related markets."""
        if isinstance(data, dict) and 'sharedTagsCount' not in data:
            data.pop('shared_tags_count', None)
        return data

    @model_validator(mode='after')
    def validate_market_ids(self) -> Self:
        """Ensure market_id matches the market data."""
        if self.user.id != self.created_by:
            raise ValueError(
                "user.id does not match created_by."
                f"{self.user.id} != {self.created_by}"
            )
        if self.parent_list is not None:
            if self.parent_list.id != self.parent_list_id:
                raise ValueError(
                    "Parent list ID does not match parent_list_id."
                    f"{self.parent_list.id} != {self.parent_list_id}"
                )
        for option in self.options:
            if option.market_id != self.id:
                raise ValueError(
                    "Option market_id does not match the market's ID."
                    f"{option.market_id} != {self.id}"
                )
        return self

# Type adapters for serialization
comments_adapter = TypeAdapter(list[CommentView])
market_option_positions_adapter = TypeAdapter(list[MarketOptionPositionView])
market_views_adapter = TypeAdapter(list[MarketView])
user_balances_adapter = TypeAdapter(list[UserBalanceView])
