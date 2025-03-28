"""
Tests that no data is dropped.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import requests

BASEURL = "https://api.playmoney.dev/v1"
TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"
TEST_USER_ID = "clzrooq660000a2uznm33y25b"
TEST_COMMENT_ID = "cm5j3371q008elbahtrgixruy"

def perform_test(vcr_record, compare_api_model, client, endpoint, item_id, cassette, method_name): # noqa: PLR0913
    """Apply a generic passthrough test."""
    with vcr_record.use_cassette(cassette):
        item = getattr(client, method_name)(item_id)
    response = requests.get(f"{BASEURL}/{endpoint}/{item_id}", timeout=10)
    api_data = response.json()['data']
    compare_api_model(api_data, item.model_dump(by_alias=True))

def test_comment(vcr_record, compare_api_model, client):
    """Test the retrieval of a specific comment."""
    perform_test(vcr_record, compare_api_model, client,
                 endpoint="comments",
                 item_id=TEST_COMMENT_ID,
                 cassette="comment_passthrough.yaml",
                 method_name="comment")

def test_market(vcr_record, compare_api_model, client):
    """Test the retrieval of markets."""
    perform_test(vcr_record, compare_api_model, client,
                 endpoint="markets",
                 item_id=TEST_MARKET_ID,
                 cassette="market_passthrough.yaml",
                 method_name="market")

def test_user(vcr_record, compare_api_model, client):
    """Test the retrieval of users."""
    # Replace with a valid user ID for your tests
    perform_test(vcr_record, compare_api_model, client,
                 endpoint="users",
                 item_id=TEST_USER_ID,
                 cassette="user_passthrough.yaml",
                 method_name="user")
