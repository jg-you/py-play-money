"""
Tests every end point of client.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from datetime import datetime, timezone

from py_play_money import PMClient

TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"
TEST_USER_ID = "clzrooq660000a2uznm33y25b"
TEST_USER_USERNAME = "jgyou"
TEST_USER_REFERRAL_CODE = "J2P2"

def test_init():
    """Test the initialization of the API client."""
    client = PMClient()
    assert client.base_url is not None

def test_market(vcr_record, client):
    """Test retrieval of market data."""
    with vcr_record.use_cassette('market.yaml'):
        markets = [
            client.market(TEST_MARKET_ID),
        ]
        for m in markets:
            assert m is not None
            assert m.id == TEST_MARKET_ID
            assert m.created_by == "clzrooq660000a2uznm33y25b"
            assert m.amm_account_id == "cm5ifmwfo001j24d2s5b1c7t3"
            assert m.slug == "playmoney-api-python-wrapper-in-january-2025"
            assert m.question == "Playmoney API python wrapper in January 2025?"
            assert m.description == (
                "<p>I plan to create a manifoldpy-style "
                "wrapper for playmoney.</p><p>Resolves to YES if all basic API actions can "
                "be performed using publicly available code at the end of the month.</p>"
            )
            assert m.created_at == datetime(2025, 1, 4, 17, 2, 55, 669000, tzinfo=timezone.utc)
            assert m.updated_at == datetime(2025, 2, 3, 23, 50, 54, 104000, tzinfo=timezone.utc)
            assert m.close_date == datetime(2025, 2, 3, 23, 50, 54, 104000, tzinfo=timezone.utc)
            assert m.resolved_at == datetime(2025, 2, 3, 23, 50, 54, 104000, tzinfo=timezone.utc)
            assert m.comment_count == 4
            assert m.unique_traders_count == 5
            assert m.unique_promoters_count == 100
            assert m.liquidity_count == 1816
            assert sorted(m.tags) == [
                "api",
                "playmoney",
                "programming",
                "python",
                "software-development"
            ]
            assert m.parent_list_id is None

def test_user(vcr_record, client):
    """Test the retrieval of user data."""
    with vcr_record.use_cassette('user.yaml'):
        users = [
            client.user(TEST_USER_ID),
            client.user.by_id(TEST_USER_ID),
            client.user.by_username(TEST_USER_USERNAME),
            client.user.by_referral(TEST_USER_REFERRAL_CODE)
        ]
        for u in users:
            u = client.user(TEST_USER_ID)
            assert u is not None
            assert u.id == TEST_USER_ID
            assert u.username == "jgyou"
            assert u.display_name == "jgyou"
            assert u.avatar_url is None
            assert u.twitter_handle is None
            assert u.discord_handle is None
            assert u.website is None
            assert u.bio == "https://manifold.markets/jgyou"
            assert u.timezone == "America/New_York"
            assert u.primary_account_id == "c66cc328ef6c13d1767417889"
            assert u.role == "USER"
            assert u.referral_code == "J2P2"
            assert u.referred_by is None
            assert u.created_at == datetime(2024, 8, 13, 0, 27, 58, 974000, tzinfo=timezone.utc)
            assert u.updated_at == datetime(2024, 10, 1, 5, 40, 44, 407000, tzinfo=timezone.utc)
