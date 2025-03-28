"""
Tests for the API client.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import requests

from py_play_money import PMClient

BASEURL = "https://api.playmoney.dev/v1/"
TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"


def test_init():
    """Test the initialization of the API client."""
    client = PMClient()
    assert client.base_url is not None


def test_market(vcr_record, compare_api_model):
    """Test the retrieval of markets."""
    client = PMClient()
    with vcr_record.use_cassette('market_passthrough.yaml'):
        # Request through the client
        market = client.market(market_id=TEST_MARKET_ID)

        # Requests directly
        response = requests.get(f"{BASEURL}markets/{TEST_MARKET_ID}", timeout=10)
        api_data = response.json()['data']

        # Compare using the fixture
        model_dict = market.model_dump(by_alias=True)
        compare_api_model(api_data, model_dict)
