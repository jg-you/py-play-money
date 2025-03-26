"""
Handles all API interactions.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import logging
from typing import Literal

import requests

from py_play_money.adapters import (
    activity_list_adapter,
    comment_list_adapter,
    position_list_adapter,
)
from py_play_money.schemas import (
    Activity,
    Comment,
    FullMarket,
    GraphTick,
    Market,
    MarketList,
    PageInfo,
    Position,
    User,
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Client:
    """
    Client for interacting with the Play Money API.

    All requests accept keyword arguments that are passed to the `requests` library.

    Args:
        api_key (str | None): API key to use for authenticated requests.
        base_url (str): Base URL of the API. 
            Defaults to the API of the main hosted instance of PlayMoney.dev. 
        version (str): Version of the API to use. Supported: 'v1'.

    Examples:
        ```python
        from py_play_money import Client
        client = Client()
        # Get a market
        market = client.markets.get(market_id="cm5ifmwfo001g24d2r7fzu34u")
        # Get a user, with timeout
        user = client.users.get(user_id="user123", timeout=5)
        ```

    """

    def __init__(
            self,
            api_key: str | None = None,
            base_url = "https://api.playmoney.dev",
            version: Literal["v1"] = "v1"
        ) -> None:

        # Load configs
        self.base_url = base_url + f"/{version}"
        self.api_key = api_key
        if self.api_key is None:
            self.authenticated = False
            logger.warning(
                "No key provided, won't be able to execute POST requests."
            )
        else:
            self.authenticated = True

        # Set up headers
        self.headers = {
            'User-Agent': 'py-play-money/0.1 (https://github.com/jg-you/py-play-money)'
        }
        if self.api_key:
            self.headers['x-api-key'] = self.api_key

        # Assign resources
        self.market = self.MarketResource(self)
        self.list = self.MarketListResource(self)
        self.user = self.UserResource(self)

    def execute_get(self, endpoint: str, **kwargs):
        """
        Execute a GET request to the API.

        Args:
            endpoint (str): The API endpoint to call.
            **kwargs: Additional keyword arguments to pass to the request.
                      Timeout defaults to 10 seconds if not specified.

        Returns:
            response (requests.Response): The response object from the request.

        """
        url = f"{self.base_url}/{endpoint}"
        try:
            if "timeout" not in kwargs:
                timeout = 10
            else:
                timeout = kwargs.pop("timeout")
            logger.info("Requesting %s. Timeout: %s. Args: %s", url, timeout, kwargs)
            response = requests.get(url, headers=self.headers, timeout=timeout, **kwargs)
            logger.debug("Response: %s, %s", response.status_code, response.text)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise

    def activity(self, **kwargs) -> list[Activity]:
        """Retrieve activity for the whole website."""
        endpoint = "activity"
        data = self.execute_get(endpoint, **kwargs)['data']
        return [Activity(**d) for d in data]

    def comments(self, comment_id: str, **kwargs) -> Comment:
        """
        Retrieve a comment by ID.

        Args:
            comment_id (str): The ID of the comment to retrieve.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            Comment: The retrieved Comment object.

        """
        endpoint = f"comments/{comment_id}"
        return Comment(**self.execute_get(endpoint, **kwargs)['data'])

    def markets(self,
                cursor: str | None = None,
                status: Literal['active', 'closed', 'all'] = 'all',
                createdBy: str | None = None,
                tags: list[str] | None = None,
                limit: int = 10,
                sortField: str | None = None,
                sortDirection: Literal['asc', 'desc'] = 'asc',
                **kwargs) -> tuple[list[FullMarket], PageInfo]:
        """
        Page through all markets.

        Args:
            cursor (str | None): Pagination cursor, i.e., the market after which to start.
            status (str): Market status. Can be 'active', 'closed', or 'all'.
            createdBy (str | None): Filter by user ID of the market creator.
            tags (list[str] | None): Filter by tags associated with the market.
            limit (int): Number of markets to return per page.
            sortField (str | None): Field to sort by.
            sortDirection (str): Sort direction. Can be 'asc' or 'desc'.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            tuple: A tuple containing a list of FullMarket objects and a PageInfo object.

        Example:
            ```python
            cursor = None
            while True:
                markets, page_info = client.markets(cursor=cursor, status='active', limit=5)
                print(f"Found {len(markets)} markets")
                cursor = page_info.endCursor
                if page_info.hasNextPage is False:
                    break
            ```

        """
        if tags is None:
            tags = []
        payload = {
            "cursor": cursor,
            "status": status,
            "createdBy": createdBy,
            "tags": tags,
            "limit": limit,
            "sortField": sortField,
            "sortDirection": sortDirection
        }
        response = self.execute_get("markets", params=payload, **kwargs)
        return (
            [FullMarket(**market) for market in response['data']],
            PageInfo(**response['pageInfo'])
        )

    class MarketResource:
        """Regroups all resources related to individual markets."""

        def __init__(self, client):
            self.client = client

        def get(self, market_id: str, **kwargs) -> Market:
            """Retrieve a market by ID."""
            endpoint = f"markets/{market_id}"
            return Market(**self.client.execute_get(endpoint, **kwargs)['data'])

        def get_activity(self, market_id: str, **kwargs) -> list[Activity]:
            """Retrieve activity for a market by ID."""
            endpoint = f"markets/{market_id}/activity"
            data = self.client.execute_get(endpoint, **kwargs)['data']
            return activity_list_adapter.validate_python(data)

        def get_balance(self, market_id: str, **kwargs):
            pass

        def get_balances(self, market_id: str, **kwargs):
            pass

        def get_comments(self, market_id: str, **kwargs) -> list[Comment]:
            """Retrieve comments for a market by ID."""
            endpoint = f"markets/{market_id}/comments"
            return comment_list_adapter.validate_python(
                self.client.execute_get(endpoint, **kwargs)['data']
                )

        def get_graph(self, market_id: str, **kwargs) -> list[GraphTick]:
            """Retrieve graph data for a market by ID."""
            endpoint = f"markets/{market_id}/graph"
            data = self.client.execute_get(endpoint, **kwargs)['data']
            return [GraphTick(**tick) for tick in data]

        def get_positions(self, market_id: str, **kwargs) -> list[Position]:
            """Retrieve positions for a market by ID."""
            endpoint = f"markets/{market_id}/positions"
            return position_list_adapter.validate_python(
                self.client.execute_get(endpoint, **kwargs)['data']
                )

        def get_related(self, market_id: str, **kwargs):
            """Retrieve related markets for a market by ID."""
            endpoint = f"markets/{market_id}/related"
            data = self.client.execute_get(endpoint, **kwargs)['data']
            return [FullMarket(**market) for market in data]


    class MarketListResource:
        """Regroups all resources related to lists of markets."""

        def __init__(self, client):
            self.client = client

        def get(self, list_id: str, **kwargs) -> MarketList:
            """Retrieve a list by ID."""
            endpoint = f"lists/{list_id}"
            return MarketList(**self.client.execute_get(endpoint, **kwargs)['data'])

        def get_balance(self, list_id: str, **kwargs):
            pass

        def get_comments(self, list_id: str, **kwargs) -> list[Comment]:
            """Retrieve comments for a list by ID."""
            endpoint = f"lists/{list_id}/comments"
            data = self.client.execute_get(endpoint, **kwargs)['data']
            return [Comment(**comment) for comment in data]

        def get_graph(self, list_id: str, **kwargs) -> list[GraphTick]:
            """Retrieve graph data for a list by ID."""
            endpoint = f"lists/{list_id}/graph"
            data = self.client.execute_get(endpoint, **kwargs)['data']
            return [GraphTick(**tick) for tick in data]


    class UserResource:
        """Regroups all resources related to users."""

        def __init__(self, client):
            self.client = client
            # Assign resources
            self.me = self.Me(client, client.api_key is not None)

        def get(self, user_id: str, **kwargs) -> User:
            """Retrieve user by ID."""
            endpoint = f"users/{user_id}"
            return User(**self.client.execute_get(endpoint, **kwargs)['data'])

        def get_by_username(self, user_name: str, **kwargs) -> User:
            """Retrieve user by username."""
            endpoint = f"users/username/{user_name}"
            return User(**self.client.execute_get(endpoint, **kwargs)['data'])

        def get_balance(self, user_id: str, **kwargs):
            pass

        def get_graph(self, user_id: str, **kwargs):
            pass

        def get_positions(self, user_id: str, **kwargs) -> list[Position]:
            """Retrieve positions for a user by ID."""
            endpoint = f"users/{user_id}/positions"
            data = self.client.execute_get(endpoint, **kwargs)['data']
            return [Position(**position) for position in data]

        def get_stats(self, user_id: str, **kwargs):
            pass

        def get_transactions(self, user_id: str, **kwargs):
            pass


        class Me:
            """Represents the authenticated user."""

            def __init__(self, client, authenticated: bool = False):
                self.authenticated = authenticated
                self.client = client

            def get(self, **kwargs) -> User:
                """Retrieve the authenticated user by username."""
                if not self.authenticated:
                    raise ValueError("User is not authenticated.")
                endpoint = "users/me"
                return User(**self.client.execute_get(endpoint, **kwargs)['data'])

            def get_notifications(self, **kwargs):
                """Retrieve notifications for the authenticated user."""
                if not self.authenticated:
                    raise ValueError("User is not authenticated.")
                endpoint = "users/me/notifications"
                return self.client.execute_get(endpoint, **kwargs)

            def get_referrals(self, **kwargs):
                """Retrieve referrals for the authenticated user."""
                if not self.authenticated:
                    raise ValueError("User is not authenticated.")
                endpoint = "users/me/referrals"
                return self.client.execute_get(endpoint, **kwargs)

            def get_balance(self, **kwargs):
                """Retrieve balance for the authenticated user."""
                if not self.authenticated:
                    raise ValueError("User is not authenticated.")
                endpoint = "users/me/balance"
                return self.client.execute_get(endpoint, **kwargs)
