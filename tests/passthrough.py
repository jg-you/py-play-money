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

    def test(self,  # noqa: PLR0913
            cassette, endpoint, client_method, item_id,
            nested_method=None, api_transform=None):
        """
        Apply a generic passthrough test.

        Args:
            cassette (str): VCR cassette name
            endpoint (str): API endpoint (e.g., "markets")
            client_method (str): Client method name to get resource associated with endpoint
            item_id (str): Resource ID
            nested_method (str, optional): Nested method name for sub-resources (e.g., "comments"
                to test markets/[ID]/comments.)
            api_transform (callable, optional): Function to transform API data before comparison.

        """
        with self.vcr.use_cassette(cassette):
            resource = getattr(self.client, client_method)(item_id)
            if nested_method is not None:
                resource = getattr(resource, nested_method)()
                resp = requests.get(
                    f"{self.baseurl}/{endpoint}/{item_id}/{nested_method}",
                    timeout=10
                )
            else:
                resp = requests.get(f"{self.baseurl}/{endpoint}/{item_id}", timeout=10)

        api_data = resp.json()['data']
        if api_transform is not None:
            api_data = api_transform(api_data)

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

def rename_user_subfield(data):
    """
    Rename user subfield.
    
    The inconsistency breaks some passthrough tests.
    """
    new_data = []
    for d in data:
        new_data.append(d)
        new_data[-1]['account']['userPrimary'] = d['account'].pop('user')
    return new_data

# == Test Cases ==
def test_comment(api_tester):
    """Test the retrieval of a specific comment."""
    api_tester.test(
        cassette="comment_passthrough.yaml",
        endpoint="comments",
        client_method="comment",
        item_id=TEST_COMMENT_ID,
    )

# == users/ endpoints ==
def test_user(api_tester):
    """Test the retrieval of an individual user."""
    api_tester.test(
        cassette="user_passthrough.yaml",
        endpoint="users",
        client_method="user",
        item_id=TEST_USER_ID,
    )

def test_user_balance(api_tester):
    """Test the retrieval of a user's balance."""
    api_tester.test(
        cassette="user_balance_passthrough.yaml",
        endpoint="users",
        client_method="user",
        item_id=TEST_USER_ID,
        nested_method="balance",
        api_transform=lambda data: data['balance']
    )


def test_user_positions(vcr_record, compare_api_model, client):
    """Test the retrieval of a user's positions."""
    with vcr_record.use_cassette("user_position_passthrough.yaml"):
        # client
        positions, page_info = client.user(TEST_USER_ID).positions(
            limit=10,
            sort_direction='asc',
            status='all'
        )
        # direct API call
        params = {
            "limit": 10,
            "sortDirection": 'asc',
            "status": 'all'
        }
        resp = requests.get(
            f"{BASEURL}/users/{TEST_USER_ID}/positions",
            params=params,
            timeout=10
        )
        api_data = resp.json()['data']
        api_data = rename_user_subfield(api_data)
        api_page_info = resp.json()['pageInfo']
        assert len(positions) == len(api_data), "Number of items doesn't match"
        for i, item in enumerate(positions):
            compare_api_model(api_data[i], item.model_dump(by_alias=True))
        assert page_info.total == api_page_info['total'], (
            "Total number of markets doesn't match"
        )
        assert page_info.has_next_page == api_page_info['hasNextPage'], (
            "Has next page doesn't match"
        )
        assert page_info.end_cursor == api_page_info['endCursor'], (
            "End cursor doesn't match"
        )


def test_user_graph(api_tester):
    """Test the retrieval of a user's graph."""
    api_tester.test(
        cassette="user_graph_passthrough.yaml",
        endpoint="users",
        client_method="user",
        item_id=TEST_USER_ID,
        nested_method="graph",
    )

# == markets/ endpoints ==

def test_markets(vcr_record, compare_api_model, client):
    """Test the retrieval of an individual market."""
    with vcr_record.use_cassette("markets_passthrough.yaml"):
        # client
        markets, page_info = client.markets(
            limit=10,
            sort_direction='asc',
            status='all'
        )
        # direct API call
        params = {
            "limit": 10,
            "sortDirection": 'asc',
            "status": 'all'
        }
        resp = requests.get(
            f"{BASEURL}/markets",
            params=params,
            timeout=10
        )
        api_data = resp.json()['data']
        api_page_info = resp.json()['pageInfo']
        assert len(markets) == len(api_data), "Number of items doesn't match"
        for i, item in enumerate(markets):
            compare_api_model(api_data[i], item.model_dump(by_alias=True))
        assert page_info.total == api_page_info['total'], (
            "Total number of markets doesn't match"
        )
        assert page_info.has_next_page == api_page_info['hasNextPage'], (
            "Has next page doesn't match"
        )
        assert page_info.end_cursor == api_page_info['endCursor'], (
            "End cursor doesn't match"
        )


def test_market(api_tester):
    """Test the retrieval of an individual market."""
    api_tester.test(
        cassette="market_passthrough.yaml",
        endpoint="markets",
        client_method="market",
        item_id=TEST_MARKET_ID,
    )

def test_market_balance(api_tester):
    """Test the retrieval of the AMM balance for a specific market."""
    api_tester.test(
        cassette="market_balance_passthrough.yaml",
        endpoint="markets",
        client_method="market",
        item_id=TEST_MARKET_ID,
        nested_method="balance",
        api_transform=lambda data: data['amm']
    )

def test_market_balances(api_tester):
    """Test the retrieval of the final balances for a specific market."""
    api_tester.test(
        cassette="market_balances_passthrough.yaml",
        endpoint="markets",
        client_method="market",
        item_id=TEST_MARKET_ID,
        nested_method="balances",
        api_transform=lambda data: data['balances']
    )

def test_market_comment(api_tester):
    """Test the retrieval of the comments on a specific market."""
    api_tester.test(
        cassette="market_comments_passthrough.yaml",
        endpoint="markets",
        client_method="market",
        item_id=TEST_MARKET_ID,
        nested_method="comments"
    )

def test_market_graph(api_tester):
    """Test the retrieval of a market graph."""
    api_tester.test(
        cassette="market_graph_passthrough.yaml",
        endpoint="markets",
        client_method="market",
        item_id=TEST_MARKET_ID,
        nested_method="graph"
    )

def test_market_positions(api_tester):
    """Test the retrieval of the positions in a specific market."""
    api_tester.test(
        cassette="market_positions_passthrough.yaml",
        endpoint="markets",
        client_method="market",
        item_id=TEST_MARKET_ID,
        nested_method="positions",
        api_transform=rename_user_subfield
    )

def test_market_related(api_tester):
    """Test the retrieval of related markets."""
    api_tester.test(
        cassette="market_related_passthrough.yaml",
        endpoint="markets",
        client_method="market",
        item_id=TEST_MARKET_ID,
        nested_method="related"
    )
