"""
Tests every end point of client.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from datetime import datetime, timezone

from py_play_money import PMClient

# from .conftest import vcr_record
# from freezegun import freeze_time


TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"


def test_init():
    """Test the initialization of the API client."""
    client = PMClient()
    assert client.base_url is not None

def test_market(vcr_record):
    """Test the retrieval of markets."""
    client = PMClient()
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

