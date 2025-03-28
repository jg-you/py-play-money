"""
Tests every end point of client.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from datetime import datetime, timezone

from py_play_money import PMClient


TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"
TEST_USER_ID = "clzrooq660000a2uznm33y25b"

def test_init():
    """Test the initialization of the API client."""
    client = PMClient()
    assert client.base_url is not None

def test_market(vcr_record, client):
    """Test retrieval of market data."""
    with vcr_record.use_cassette('market.yaml'):
        market = client.market(market_id=TEST_MARKET_ID)
        assert market is not None
        assert market.id == TEST_MARKET_ID
        assert market.created_by == "clzrooq660000a2uznm33y25b"
        assert market.amm_account_id == "cm5ifmwfo001j24d2s5b1c7t3"
        assert market.slug == "playmoney-api-python-wrapper-in-january-2025"
        assert market.question == "Playmoney API python wrapper in January 2025?"
        assert market.description == (
            "<p>I plan to create a manifoldpy-style "
            "wrapper for playmoney.</p><p>Resolves to YES if all basic API actions can "
            "be performed using publicly available code at the end of the month.</p>"
        )
        assert market.created_at == datetime(2025, 1, 4, 17, 2, 55, 669000, tzinfo=timezone.utc)
        assert market.updated_at == datetime(2025, 2, 3, 23, 50, 54, 104000, tzinfo=timezone.utc)
        assert market.close_date == datetime(2025, 2, 3, 23, 50, 54, 104000, tzinfo=timezone.utc)
        assert market.resolved_at == datetime(2025, 2, 3, 23, 50, 54, 104000, tzinfo=timezone.utc)
        assert market.comment_count == 4
        assert market.unique_traders_count == 5
        assert market.unique_promoters_count == 100
        assert market.liquidity_count == 1816
        assert sorted(market.tags) == [
            "api",
            "playmoney",
            "programming",
            "python",
            "software-development"
        ]
        assert market.parent_list_id is None

def test_user(vcr_record, client):
    """Test the retrieval of user data."""
    with vcr_record.use_cassette('user.yaml'):
        user = client.user(TEST_USER_ID)
        assert user is not None
        assert user.id == TEST_USER_ID
        assert user.username == "jgyou"
        assert user.display_name == "jgyou"
        assert user.avatar_url is None
        assert user.twitter_handle is None
        assert user.discord_handle is None
        assert user.website is None
        assert user.bio == "https://manifold.markets/jgyou"
        assert user.timezone == "America/New_York"
        assert user.primary_account_id == "c66cc328ef6c13d1767417889"
        assert user.role == "USER"
        assert user.referral_code == "J2P2"
        assert user.referred_by is None
        assert user.created_at == datetime(2024, 8, 13, 0, 27, 58, 974000, tzinfo=timezone.utc)
        assert user.updated_at == datetime(2024, 10, 1, 5, 40, 44, 407000, tzinfo=timezone.utc)
