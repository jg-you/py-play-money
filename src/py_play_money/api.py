"""
Handles all API interactions.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import logging
from typing import Literal

import requests

from py_play_money._version import __version__
from py_play_money.adapters import (
    activity_list_adapter,
)
from py_play_money.schemas import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


class MarketWrapper(Market):
    """
    Combines the Market model with API functions.
    """

    def __init__(self, client: 'PMClient', market_data: Market):
        super().__init__(**market_data.model_dump(by_alias=True))
        self._client = client

    def activity(self, **kwargs) -> list[Activity]:
        """Fetch market activity."""
        endpoint = f"markets/{self.id}/activity"
        resp = self._client.execute_get(endpoint, **kwargs)
        return activity_list_adapter.validate_python(resp['data'])

    def balance(self, **kwargs) -> list[MarketBalance]:
        """Fetch market balance."""
        endpoint = f"markets/{self.id}/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        return market_balances_adapter.validate_python(resp['data']['amm'])

    def balances(self, **kwargs) -> list[UserBalance]:
        """Fetch final market balances."""
        endpoint = f"markets/{self.id}/balances"
        resp = self._client.execute_get(endpoint, **kwargs)
        return user_balances_adapter.validate_python(resp['data']['balances'])

    def comments(self, **kwargs) -> list[CommentView]:
        """Fetch market comments."""
        endpoint = f"markets/{self.id}/comments"
        resp = self._client.execute_get(endpoint, **kwargs)
        return comments_adapter.validate_python(resp['data'])

    def graph(self, **kwargs) -> list[MarketGraphTick]:
        """Fetch market graphs."""
        endpoint = f"markets/{self.id}/graph"
        resp = self._client.execute_get(endpoint, **kwargs)
        return market_graph_ticks_adapter.validate_python(resp['data'])

    def positions(self, **kwargs) -> list[MarketOptionPositionView]:
        """Fetch market positions."""
        endpoint = f"markets/{self.id}/positions"
        resp = self._client.execute_get(endpoint, **kwargs)
        return market_option_positions_adapter.validate_python(resp['data'])

    def related(self, **kwargs) -> list[MarketView]:
        """Fetch related markets."""
        endpoint = f"markets/{self.id}/related"
        resp = self._client.execute_get(endpoint, **kwargs)
        return market_views_adapter.validate_python(resp['data'])


class UserWrapper(User):
    """
    Combines the User model with API functions.
    """

    def __init__(self, client: 'PMClient', user_data: User):
        super().__init__(**user_data.model_dump(by_alias=True))
        self._client = client

    def balance(self, **kwargs) -> UserBalance:
        """Fetch user balance."""
        endpoint = f"users/{self.id}/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        return UserBalance(**resp['data']['balance'])

    def graph(self, **kwargs) -> list[UserGraphTick]:
        """Fetch user graphs."""
        endpoint = f"users/{self.id}/graph"
        resp = self._client.execute_get(endpoint, **kwargs)
        return user_graph_ticks_adapter.validate_python(resp['data'])

    def positions(self,
                  cursor: str | None = None,
                  status: Literal['active', 'closed', 'all'] = 'all',
                  limit: int = 10,
                  sort_field: str | None = None,
                  sort_direction: Literal['asc', 'desc'] = 'asc',
                  **kwargs) -> tuple[list[MarketOptionPositionView], PageInfo]:
        """
        Page through positions of the user.

        Args:
            cursor (str | None): Pagination cursor, i.e., the market after which to start.
            status (str): Market status. Can be 'active', 'closed', or 'all'.
            limit (int): Number of markets to return per page.
            sort_field (str | None): Field to sort by.
            sort_direction (str): Sort direction. Can be 'asc' or 'desc'.
            **kwargs: Additional keyword arguments to pass to the request.
     
        Returns:
            tuple: A tuple containing a list of FullMarket objects and a PageInfo object.

        Example:
        ```python
        cursor = None
        while True:
            markets, page_info = client.markets(cursor=cursor, status='active', limit=5)
            print(f"Found {len(markets)} markets")
            cursor = page_info.end_cursor
            if page_info.has_next_page is False:
                break
        ```
        """
        # validate request
        if cursor and not CUID.validate(cursor):
            raise ValueError(f"`cursor` is an invalid market CUID: {cursor}")

        # prepare payload
        payload = {
            "cursor": cursor,
            "status": status,
            "limit": limit,
            "sortField": sort_field,
            "sortDirection": sort_direction
        }

        # make request
        endpoint = f"users/{self.id}/positions"
        response = self._client.execute_get(endpoint, params=payload, **kwargs)
        return (
            market_option_positions_adapter.validate_python(response['data']),
            PageInfo(**response['pageInfo'])
        )


class CommentResource:
    """
    Functions to fetch comment information from the API.
    """

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, comment_id: str = None) -> CommentView:
        if comment_id:
            return self.by_id(comment_id)
        return self

    def by_id(self, comment_id: str, **kwargs) -> CommentView:
        """Fetch a comment by ID."""
        endpoint = f"comments/{comment_id}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return CommentView(**resp['data'])


class MarketResource:
    """
    Functions to fetch market information from the API.
    """

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, market_id=None):
        """Make MarketResource callable."""
        if market_id:
            return self.by_id(market_id)
        return self

    def by_id(self, market_id: str, **kwargs) -> MarketWrapper:
        """Fetch a market by ID."""
        endpoint = f"markets/{market_id}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return MarketWrapper(self._client, Market(**resp['data']))


class UserResource:
    """
    Functions to fetch user information from the API.
    """

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, user_id=None):
        """Make UserResource callable."""
        if user_id:
            return self.by_id(user_id)
        return self

    def by_id(self, user_id: str, **kwargs) -> UserWrapper:
        """Fetch a user by ID."""
        endpoint = f"users/{user_id}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return UserWrapper(self._client, User(**resp['data']))

    def by_username(self, user_name: str, **kwargs) -> UserWrapper:
        """Fetch a user by username."""
        endpoint = f"users/username/{user_name}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return UserWrapper(self._client, User(**resp['data']))

    def by_referral(self, referral_code: str, **kwargs) -> UserWrapper:
        """Fetch a user by username."""
        endpoint = f"users/referral/{referral_code}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return UserWrapper(self._client, User(**resp['data']))


class PMClient:
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
    from py_play_money import PMClient
    client = PMClient()
    # Get a market
    market = client.market(market_id="cm5ifmwfo001g24d2r7fzu34u")
    # Get a user, with timeout
    user = client.user.by_username("user123", timeout=5)
    ```

    """

    def __init__(self, api_key=None, base_url="https://api.playmoney.dev", version="v1") -> None:
        self.api_key = api_key
        self.base_url = f"{base_url}/{version}"
        self.headers = {'User-Agent': f"py-play-money/{__version__}"}
        if api_key:
            self.headers['x-api-key'] = api_key
            self.authenticated = True
        else:
            self.authenticated = False

        # Resource proxies
        self.comment = CommentResource(self)
        self.market = MarketResource(self)
        self.user = UserResource(self)

    def execute_get(self, endpoint, **kwargs) -> dict:
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
        timeout = kwargs.pop("timeout", 10)
        try:
            logger.info("Requesting %s. Timeout: %s. Args: %s", url, timeout, kwargs)
            response = requests.get(url, headers=self.headers, timeout=timeout, **kwargs)
            logger.debug("Response: %s, %s", response.status_code, response.text)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise
    
    def markets(self,
                cursor: str | None = None,
                status: Literal['active', 'closed', 'all'] = 'all',
                created_by: str | None = None,
                tags: list[str] | None = None,
                limit: int = 10,
                sort_field: str | None = None,
                sort_direction: Literal['asc', 'desc'] = 'asc',
                **kwargs) -> tuple[list[MarketView], PageInfo]:
        """
        Page through all markets.

        Args:
            cursor (str | None): Pagination cursor, i.e., the market after which to start.
            status (str): Market status. Can be 'active', 'closed', or 'all'.
            created_by (str | None): Filter by user ID of the market creator.
            tags (list[str] | None): Filter by tags associated with the market.
            limit (int): Number of markets to return per page.
            sort_field (str | None): Field to sort by.
            sort_direction (str): Sort direction. Can be 'asc' or 'desc'.
            **kwargs: Additional keyword arguments to pass to the request.
     
        Returns:
            tuple: A tuple containing a list of FullMarket objects and a PageInfo object.

        Example:
        ```python
        cursor = None
        while True:
            markets, page_info = client.markets(cursor=cursor, status='active', limit=5)
            print(f"Found {len(markets)} markets")
            cursor = page_info.end_cursor
            if page_info.has_next_page is False:
                break
        ```
        """
        # validate request
        if cursor and not CUID.validate(cursor):
            raise ValueError(f"`cursor` is an invalid market CUID: {cursor}")
        if created_by and not CUID.validate(created_by):
            raise ValueError(f"`created_by` is an invalid user CUID: {created_by}")
        
        # prepare payload
        tags = [] if tags is None else tags
        payload = {
            "cursor": cursor,
            "status": status,
            "createdBy": created_by,
            "tags": tags,
            "limit": limit,
            "sortField": sort_field,
            "sortDirection": sort_direction
        }

        # make request
        response = self.execute_get("markets", params=payload, **kwargs)
        return (
            market_views_adapter.validate_python(response['data']),
            PageInfo(**response['pageInfo'])
        )
