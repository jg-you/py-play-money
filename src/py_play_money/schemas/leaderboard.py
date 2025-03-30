"""
Leaderboard models.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from pydantic import Field

from py_play_money.schemas.base_types import CUID, CamelCaseModel

class LeaderboardEntry(CamelCaseModel):
    """Leaderboard entry."""

    user_id: CUID
    display_name: str
    username: str
    avatar_url: str | None
    total: int
    rank: int = Field(ge=0)

class UserRanking(CamelCaseModel):
    """Ranking for authenticated user."""

    trader: LeaderboardEntry
    creator: LeaderboardEntry
    promoter: LeaderboardEntry
    quester: LeaderboardEntry
    referrer: LeaderboardEntry

class Leaderboard(CamelCaseModel):
    """Leaderboard."""

    top_traders: list[LeaderboardEntry]
    top_creators: list[LeaderboardEntry]
    top_promoters: list[LeaderboardEntry]
    top_questers: list[LeaderboardEntry]
    top_referrers: list[LeaderboardEntry]
    user_rankings: UserRanking | None = None
