"""
Tests for the API client.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import py_play_money as ppm

TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"

def test_api_init():
    """Test the initialization of the API client."""
    client = ppm.Client()
    assert client.base_url is not None


def test_api_get_markets():
    """Test the retrieval of markets."""
    client = ppm.Client()
    market = client.markets.get(market_id=TEST_MARKET_ID)
    assert market is not None
    assert market.id == TEST_MARKET_ID
    assert market.slug == "playmoney-api-python-wrapper-in-january-2025"
    assert market.question == "Playmoney API python wrapper in January 2025?"
    assert market.closeDate is not None
    assert market.createdAt is not None
