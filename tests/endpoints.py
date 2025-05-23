"""
Tests every end point of client.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import random
import string
from datetime import datetime, timezone

import pytest

from py_play_money import PMClient

TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"
TEST_USER_ID = "clzrooq660000a2uznm33y25b"
TEST_USER_USERNAME = "jgyou"
TEST_USER_REFERRAL_CODE = "J2P2"
TEST_COMMENT_ID = "cm5j3371q008elbahtrgixruy"

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

def test_comment(vcr_record, client):
    """Test the retrieval of comments."""
    with vcr_record.use_cassette('comment.yaml'):
        comments = [
            client.comment(TEST_COMMENT_ID),
            client.comment.by_id(TEST_COMMENT_ID),
        ]
        for c in comments:
            # Check if the comment has the expected properties
            assert c is not None
            assert c.id == TEST_COMMENT_ID
            assert c.content == (
                "<p>i bought yes and the price went down??? is that supposed to happen</p>"
            )
            assert c.created_at == datetime(2025, 1, 5, 3, 59, 27, 86000, tzinfo=timezone.utc)
            assert c.updated_at == datetime(2025, 1, 5, 3, 59, 27, 86000, tzinfo=timezone.utc)
            assert c.edited is False
            assert c.author_id == "cm3ze0aqx0000kpj5ai4nv5tm"
            assert c.parent_id is None
            assert c.hidden is False
            assert c.entity_type == "MARKET"
            assert c.entity_id == "cm5ifmwfo001g24d2r7fzu34u"
            # Check if the author is loaded correctly
            assert c.author is not None
            assert c.author.id == "cm3ze0aqx0000kpj5ai4nv5tm"
            # Check if the reactions are loaded properly
            assert c.reactions is not None
            assert len(c.reactions) > 0
            assert c.reactions[0].id == "cm5jwu6kf0001110nhcg2lbgi"
            assert c.reactions[0].emoji == ":smiling_face_with_tear:"

def test_markets_paging(vcr_record, client):
    """Test that we can page through markets."""
    with vcr_record.use_cassette('markets_paging.yaml'):
        markets, page_info = client.markets(limit=10)
        assert len(markets) > 0
        assert page_info is not None
        assert page_info.has_next_page is True
        next_markets, _ = client.markets(limit=10, cursor=page_info.end_cursor)
        assert len(next_markets) > 0
        assert next_markets[0].id != markets[0].id

def test_user_positions_paging(vcr_record, client):
    """Test that we can page through markets."""
    with vcr_record.use_cassette('user_positions_paging.yaml'):
        positions, page_info = client.user(TEST_USER_ID).positions(limit=10)
        assert len(positions) > 0
        assert page_info is not None
        assert page_info.has_next_page is True
        next_pos, _ = client.user(TEST_USER_ID).positions(limit=10, cursor=page_info.end_cursor)
        assert len(next_pos) > 0
        assert next_pos[0].id != positions[0].id

def test_check_username(client):
    """Test that we can check if a username is available."""
    # We do not record to avoid collisions created by maliciously creating a username
    # recorded in the cassette.
    random_username = ''.join(random.choices(string.ascii_letters, k=50))
    assert client.check_username("case") is False
    assert client.check_username(random_username) is True


def test_resolution(vcr_record, client):
    """Test that the resolution endpoint is working."""
    with vcr_record.use_cassette('resolution.yaml'):
        res = client.market(TEST_MARKET_ID).resolution()
        assert res is not None
        assert res.id == "cm6ppf4480002146uoh2izs1h"
        assert res.market_id == TEST_MARKET_ID
        assert res.market.resolved_at == datetime(
            2025, 2, 3, 23, 50, 54, 104000, tzinfo=timezone.utc
        )
        assert res.resolution.name == "No"
        assert res.resolution.probability == 29
        assert res.resolved_by.username == "jgyou"

def test_transactions(vcr_record, client):
    """Test that the transactions endpoint is working."""
    with vcr_record.use_cassette('market_transactions.yaml'):
        transactions = client.market(TEST_MARKET_ID).transactions()
        liquidity_transactions = [t for t in transactions if "LIQUIDITY" in t.type]
        trade_transactions = [t for t in transactions if "TRADE" in t.type]
        assert len(liquidity_transactions) == 1
        assert len(trade_transactions) == 12
        primary_asset_transactions = [
            entry
            for transaction in trade_transactions
            for entry in transaction.entries
            if entry.asset_id == "PRIMARY"
        ]
        total_value = sum([entry.amount for entry in primary_asset_transactions])
        assert abs(total_value - 2246.46) < 0.1

def test_authentication_error():
    """Tests that unauthenticated access to me() raises an error."""
    api_key = None
    client = PMClient(api_key=api_key)
    with pytest.raises(PermissionError, match="No API key provided."):
        client.me()

# def test_search(vcr_record, client):
#     """Test that search returns expected results."""
#     with vcr_record.use_cassette('search.yaml'):
#         results = client.search("case")
#         found_case = False
#         for u in results.users:
#             if u.username == "case":
#                 found_case = True
#                 break
#         assert found_case is True

def test_comments_modifications(vcr_record, authenticated_client):
    """Test all POST/PATCH/DELETE actions on comments"""
    with vcr_record.use_cassette('comments_modifications.yaml'):
        client = authenticated_client
        # Create a comment
        comment = client.comment.create(
            "Hello world.", entity_id=TEST_MARKET_ID, entity_type="market"
        )
        assert comment is not None
        assert comment.content == "Hello world."
        assert comment.entity_id == TEST_MARKET_ID
        assert comment.entity_type == "MARKET"
        # Update the comment
        comment = client.comment.update(content="Hello world?", comment_id=comment.id)
        assert comment is not None
        assert comment.content == "Hello world?"
        # React to the comment
        reaction = client.comment.react(comment_id=comment.id, emoji_code=":+1:")
        assert reaction is not None
        assert reaction.emoji == ":+1:"
        # Delete the comment
        status = client.comment.delete(comment.id)
        assert status is True
        # Check that the comment is deleted
        with pytest.raises(Exception):
            client.comment(comment.id)
