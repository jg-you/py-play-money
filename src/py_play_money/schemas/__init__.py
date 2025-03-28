"""
API Schemas

Author: JGY <jean.gabriel.young@gmail.com>
"""
from py_play_money.schemas.activity import Activity, ActivityType, Notification, NotificationType
from py_play_money.schemas.base_types import CUID, IsoDatetime
from py_play_money.schemas.comments import Comment, CommentEntityType, CommentReaction
from py_play_money.schemas.finance import (
    AssetType,
    Transaction,
    TransactionEntry,
    TransactionType,
    UserBalance,
)
from py_play_money.schemas.graphs import (
    MarketGraphTick,
    UserGraphTick,
    market_graph_tick_list_adapter,
    user_graph_tick_list_adapter,
)
from py_play_money.schemas.market import (
    ContributionPolicyType,
    Market,
    MarketList,
    MarketOption,
    MarketOptionPosition,
    MarketResolution,
)
from py_play_money.schemas.user import Account, AccountType, User, UserRoleType
from py_play_money.schemas.utils import PageInfo
from py_play_money.schemas.views import (
    CommentView,
    MarketOptionPositionView,
    MarketView,
    UserBalanceView,
    comments_adapter,
    market_option_positions_adapter,
    market_views_adapter,
    user_balances_adapter,
)
