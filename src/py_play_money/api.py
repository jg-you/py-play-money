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


class MarketListWrapper(MarketList):
    """Combines the MarketList model with API functions."""

    def __init__(self, client: 'PMClient', list_data: MarketList):
        super().__init__(**list_data.model_dump(by_alias=True))
        self._client = client

    def balance(self, **kwargs) -> list[MarketBalance]:
        """Fetch list balance."""
        endpoint = f"lists/{self.id}/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        print(resp['data'])
        return market_balances_adapter.validate_python(resp['data']['user'])


class MarketWrapper(Market):
    """Combines the Market model with API functions."""

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
    """Combines the User model with API functions."""

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

    def positions(
        self,
        cursor: str | None = None,
        limit: int = 10,
        sort_field: Literal['cost', 'quantity', 'value', 'created_at', 'updated_at'] | None = None,
        sort_direction: Literal['asc', 'desc'] = 'asc',
        status: Literal['active', 'closed', 'all'] = 'all',
        **kwargs
    ) -> tuple[list[MarketOptionPositionView], PageInfo]:
        """
        Page through positions of the user.

        Args:
            cursor (str, optional): Pagination cursor, i.e., the market after which to start.
            limit (int, optional): Number of markets to return per page. Defaults to 10.
            sort_field (str, optional): Field to sort by.
                Can be 'cost', 'quantity', 'value', 'created_at', 'updated_at'.
            sort_direction (str, optional): Sort direction. Can be 'asc' or 'desc'.
            status (str, optional): Market status to include. Can be 'active', 'closed', or 'all'.
                Defaults to 'all'
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            tuple: A tuple containing a list of positions, and a paging information.

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
        if sort_field:
            first, *others = sort_field.split('_')
            sort_field = ''.join([first.lower(), *map(str.title, others)])
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
    """Functions to fetch comment information from the API."""

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

class MarketListResource:
    """Functions to fetch lists from the API."""

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, list_id: str = None) -> MarketListWrapper:
        if list_id:
            return self.by_id(list_id)
        return self

    def by_id(self, list_id: str, **kwargs) -> MarketListWrapper:
        """Fetch a list by ID."""
        endpoint = f"lists/{list_id}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return MarketListWrapper(self._client, MarketList(**resp['data']))


class MarketResource:
    """Functions to fetch markets from the API."""

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, market_id=None) -> MarketWrapper:
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
    """Functions to fetch users from the API."""

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, user_id=None) -> UserWrapper:
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
        api_key (str, optional): API key to use for authenticated requests.
        base_url (str, optional): Base URL of the API.
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

    def __init__(
        self,
        api_key: str | None=None,
        base_url: str="https://api.playmoney.dev",
        version: Literal["v1"] = "v1"
    ) -> None:
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
        self.list = MarketListResource(self)
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
        created_by: str | None = None,
        cursor: str | None = None,
        limit: int = 10,
        sort_field: MarketSortFieldType | None = None,
        sort_direction: Literal['asc', 'desc'] = 'asc',
        status: Literal['active', 'closed', 'all'] = 'all',
        tags: list[str] | None = None,
        **kwargs) -> tuple[list[MarketView], PageInfo]:
        """
        Page through all markets.

        Args:
            created_by (str, optional): Filter by user ID of the market creator.
            cursor (str, optional): Pagination cursor, i.e., the market after which to start.
            limit (int, optional): Number of markets to return per page. Defaults to 10.
            sort_field (str, optional): Field to sort by.
                Can be 'cost', 'quantity', 'value', 'created_at', 'updated_at'.
            sort_direction (str, optional): Sort direction. Can be 'asc' or 'desc'.
            status (str, optional): Market status to include. Can be 'active', 'closed', or 'all'.
                Defaults to 'all'
            tags (list[str], optional): Filter by tags associated with the market.

        Returns:
            tuple: A tuple containing a list of markets, and a paging information.

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
        if sort_field:
            first, *others = sort_field.split('_')
            sort_field = ''.join([first.lower(), *map(str.title, others)])
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
