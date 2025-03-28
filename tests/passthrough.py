"""
Tests that no data is dropped.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import pytest
import requests

BASEURL = "https://api.playmoney.dev/v1"
TEST_MARKET_ID = "cm5ifmwfo001g24d2r7fzu34u"
TEST_USER_ID = "clzrooq660000a2uznm33y25b"
TEST_COMMENT_ID = "cm5j3371q008elbahtrgixruy"

class ApiPassthroughTester:
    """Helper class for API passthrough testing."""

    def __init__(self, vcr_record, compare_api_model, client):
        """
        Initialize with test fixtures.

        Args:
            vcr_record: VCR fixture for recording API responses.
            compare_api_model: Fixture to compare API response data with model dumps.
            client: PMClient instance for making API calls.

        """
        self.vcr = vcr_record
        self.compare_api_model = compare_api_model
        self.client = client
        self.baseurl = BASEURL

    def test(self, endpoint, item_id, cassette, client_method, nested_method=None):
        """
        Apply a generic passthrough test.

        Args:
            endpoint (str): API endpoint (e.g., "markets")
            item_id (str): Resource ID
            cassette (str): VCR cassette name
            client_method (str): Client method name to get resource associated with endpoint
            nested_method (str, optional): Nested method name for sub-resources (e.g., "comments"
                to test markets/[ID]/comments.)

        """
        with self.vcr.use_cassette(cassette):
            resource = getattr(self.client, client_method)(item_id)

        if nested_method is not None:
            resource = getattr(resource, nested_method)()
            resp = requests.get(f"{self.baseurl}/{endpoint}/{item_id}/{nested_method}", timeout=10)
        else:
            resp = requests.get(f"{self.baseurl}/{endpoint}/{item_id}", timeout=10)

        api_data = resp.json()['data']

        if isinstance(resource, list):
            assert len(resource) == len(api_data), "Number of items doesn't match"
            for i, item in enumerate(resource):
                self.compare_api_model(api_data[i], item.model_dump(by_alias=True))
        else:
            self.compare_api_model(api_data, resource.model_dump(by_alias=True))

@pytest.fixture(name="api_tester")
def api_tester_fixture(vcr_record, compare_api_model, client):
    """Fixture providing an ApiPassthroughTester instance."""
    return ApiPassthroughTester(
        vcr_record=vcr_record,
        compare_api_model=compare_api_model,
        client=client
    )

# == Test Cases ==
def test_comment(api_tester):
    """Test the retrieval of a specific comment."""
    api_tester.test(
        endpoint="comments",
        item_id=TEST_COMMENT_ID,
        cassette="comment_passthrough.yaml",
        client_method="comment"
    )

def test_market(api_tester):
    """Test the retrieval of markets."""
    api_tester.test(
        endpoint="markets",
        item_id=TEST_MARKET_ID,
        cassette="market_passthrough.yaml",
        client_method="market"
    )

def test_user(api_tester):
    """Test the retrieval of users."""
    api_tester.test(
        endpoint="users",
        item_id=TEST_USER_ID,
        cassette="user_passthrough.yaml",
        client_method="user"
    )

def test_market_comment(api_tester):
    """Test the retrieval of comments for a specific market."""
    api_tester.test(
        endpoint="markets",
        item_id=TEST_MARKET_ID,
        cassette="market_comments_passthrough.yaml",
        client_method="market",
        nested_method="comments"
    )

def test_market_positions(api_tester):
    """Test the retrieval of positions for a specific market."""
    api_tester.test(
        endpoint="markets",
        item_id=TEST_MARKET_ID,
        cassette="market_positions_passthrough.yaml",
        client_method="market",
        nested_method="positions"
    )
