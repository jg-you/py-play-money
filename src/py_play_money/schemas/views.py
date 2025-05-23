"""
View schemas for API endpoints.

Created by extending base schemas.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import TypeAdapter, field_validator, model_validator
from typing_extensions import Self

from py_play_money.schemas.activity import Notification, NotificationGroup
from py_play_money.schemas.base_types import CUID, CamelCaseModel, IsoDatetime
from py_play_money.schemas.comments import Comment, CommentReaction
from py_play_money.schemas.finance import MarketBalance, Transaction, TransactionEntry, UserBalance
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
        """Ensure account_id matches account data."""
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

class MarketResolutionView(MarketResolution):
    """View of a market resolution with user information."""

    resolved_by: User
    resolution: MarketOption
    market: Market | None = None

    @model_validator(mode='after')
    def remove_none_market(self) -> 'MarketResolutionView':
        """Remove market if it's None."""
        # Handle the case where the market is not included in the response,
        # which is the most common, except for the activity endpoint.
        if self.market is None:
            object.__delattr__(self, 'market')
        return self

    @model_validator(mode='after')
    def validate_ids(self) -> Self:
        """Ensure market_id matches the market data."""
        if self.market_id != self.resolution.market_id:
            raise ValueError(
                "resolution.market_id does not match market.id."
                f"{self.resolution.market_id} != {self.market_id}"
            )
        if self.resolved_by.id != self.resolved_by_id:
            raise ValueError(
                "resolved_by.id does not match resolved_by_id."
                f"{self.resolved_by.id} != {self.resolved_by_id}"
            )
        return self


class MarketView(Market):
    """Augmented view of a market."""

    user: User
    options: list[MarketOption]
    market_resolution: MarketResolutionView | None = None
    parent_list: str | None = None
    shared_tags_count: int | None = None

    @model_validator(mode='after')
    def remove_none_shared_tags(self) -> 'MarketView':
        """Remove shared_tags_count if it's None."""
        if self.shared_tags_count is None:
            object.__delattr__(self, 'shared_tags_count')
        return self

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


class MarketBalanceView(CamelCaseModel):
    """View of a market balance."""

    amm: list[MarketBalance]
    user: list[MarketBalance]
    user_positions: list[MarketOptionPosition]


class MarketListBalanceView(CamelCaseModel):
    """View of a market list balance."""

    user: list[MarketBalance]
    user_positions: list[MarketOptionPosition]


class AuthenticatedMarketBalancesView(CamelCaseModel):
    """View of a final market balances for authenticated user."""

    balances: list[UserBalanceView]
    user: UserBalanceView


class MarketBalancesView(CamelCaseModel):
    """View of a final market balances."""

    balances: list[UserBalanceView]

# Note: The following three classes are needed to wrap the API
#       response, even if this is inelegant.
class MarketInList(Market):
    """Simplified market model used within lists."""

    options: list[MarketOption]
    market_resolution: MarketResolutionView | None = None

class MarketListEntry(CamelCaseModel):
    """Represents a market entry in a list."""

    id: CUID
    list_id: CUID
    market_id: CUID
    created_at: IsoDatetime
    market: MarketInList

class MarketListView(MarketList):
    """Augmented view of a market list."""

    owner: User
    markets: list[MarketListEntry]

    @model_validator(mode='after')
    def validate_market_ids(self) -> Self:
        """Ensure list ids match."""
        for m in self.markets:
            if m.market.parent_list_id != self.id:
                raise ValueError(
                    "Market parent_list_id does not match the market list's ID."
                    f"{m.parent_list_id} != {self.id}"
                )
            if m.list_id != self.id:
                raise ValueError(
                    "Market list_id does not match the market list's ID."
                    f"{m.list_id} != {self.id}"
                )
        return self

class TransactionView(Transaction):
    """View of a transaction with user information."""

    entries: list[TransactionEntry]
    market: Market | None
    initiator: User | None
    options: list[MarketOption]


# Note: The following four classes are needed to wrap the API
#       response, even if this is inelegant.
class TransactionViewForNotification(Transaction):
    """View of a transaction for notification."""

    entries: list[TransactionEntry]

class NotificationView(Notification):
    """View of a notification with user information."""

    actor: User | None = None
    market: Market | None = None
    comment: Comment | None = None
    comment_reaction: CommentReaction | None = None
    parent_comment: Comment | None = None
    transaction: TransactionViewForNotification | None = None
    market_option: MarketOption | None = None

class NotificationGroupView(NotificationGroup):
    """View of a notification group with details about the events."""

    last_notification: NotificationView

class NotificationsView(CamelCaseModel):
    """View of a user's notifications."""

    notifications: list[NotificationGroupView]
    unread_count: int

# Note: The following four classes are needed to wrap the API
#       response, even if this is inelegant.
class RankedMarket(Market):
    """Market with rank information."""

    rank: float

class RankedUser(User):
    """User with rank information."""

    rank: float

class RankedMarketList(MarketList):
    """Market list with rank information."""

    rank: float

class SearchResults(CamelCaseModel):
    """View of search results."""

    markets: list[RankedMarket]
    users: list[RankedUser]
    lists: list[RankedMarketList]

# Type adapters for serialization
comments_adapter = TypeAdapter(list[CommentView])
market_lists_adapter = TypeAdapter(list[MarketListView])
market_option_positions_adapter = TypeAdapter(list[MarketOptionPositionView])
markets_adapter = TypeAdapter(list[MarketView])
transactions_adapter = TypeAdapter(list[TransactionView])
user_balances_adapter = TypeAdapter(list[UserBalanceView])
