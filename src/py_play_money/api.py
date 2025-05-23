"""
Handles all API interactions.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import logging
from typing import Literal

import requests

from py_play_money._version import __version__
from py_play_money.schemas import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class MarketListWrapper(MarketList):
    """Combines the MarketList model with API functions."""

    def __init__(self, client: 'PMClient', list_data: MarketList):
        super().__init__(**list_data.model_dump(by_alias=True))
        self._client = client

    def balance(self, **kwargs) -> MarketListBalanceView:
        """Fetch list balance."""
        endpoint = f"lists/{self.id}/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        return MarketListBalanceView(**resp['data'])

    def comments(self, **kwargs) -> list[CommentView]:
        """Fetch list comments."""
        endpoint = f"lists/{self.id}/comments"
        resp = self._client.execute_get(endpoint, **kwargs)
        return comments_adapter.validate_python(resp['data'])

    def graph(self, **kwargs) -> list[MarketListGraphTick]:
        """Fetch list graphs."""
        endpoint = f"lists/{self.id}/graph"
        resp = self._client.execute_get(endpoint, **kwargs)
        return market_list_graph_ticks_adapter.validate_python(resp['data'])


class MeWrapper(User):
    """Combines the User model with API functions for authenticated user."""

    def __init__(self, client: 'PMClient', user_data: User):
        super().__init__(**user_data.model_dump(by_alias=True))
        self._client = client

    def balance(self, **kwargs) -> float:
        """Fetch the user balance."""
        endpoint = "users/me/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        return resp['data']['balance']
    
    def notifications(self, **kwargs) -> NotificationsView:
        """Fetch notifications for the authenticated user."""
        endpoint = "users/me/notifications"
        resp = self._client.execute_get(endpoint, **kwargs)
        return NotificationsView(**resp['data'])

    def referrals(self, **kwargs) -> list[User]:
        """Fetch all referrals for the authenticated user."""
        endpoint = "users/me/referrals"
        resp = self._client.execute_get(endpoint, **kwargs)
        return users_adapter.validate_python(resp['data'])

class MarketWrapper(Market):
    """Combines the Market model with API functions."""

    def __init__(self, client: 'PMClient', market_data: Market):
        super().__init__(**market_data.model_dump(by_alias=True))
        self._client = client

    def balance(self, **kwargs) -> MarketBalancesView:
        """Fetch market balance."""
        endpoint = f"markets/{self.id}/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        return MarketBalanceView(**resp['data'])

    def balances(self, **kwargs) -> AuthenticatedMarketBalancesView | MarketBalancesView:
        """Fetch final market balances with data about the authenticated user if available."""
        endpoint = f"markets/{self.id}/balances"
        resp = self._client.execute_get(endpoint, **kwargs)
        if self._client.authenticated:
            return AuthenticatedMarketBalancesView(**resp['data'])
        else:
            return MarketBalancesView(**resp['data'])

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
        return markets_adapter.validate_python(resp['data'])

    def resolution(self, **kwargs) -> MarketResolutionView | None:
        """Fetch market resolution."""
        endpoint = f"markets/{self.id}/activity"
        resp = self._client.execute_get(endpoint, **kwargs)
        # look for resolution activity
        for activity in resp['data']:
            if activity['type'] == 'MARKET_RESOLVED':
                return MarketResolutionView(**activity['marketResolution'])
        return None

    def transactions(self, **kwargs) -> list[TransactionView]:
        """Fetch all transactions on a market."""
        endpoint = f"markets/{self.id}/activity"
        resp = self._client.execute_get(endpoint, **kwargs)
        # look for transactions
        transactions = []
        for activity in resp['data']:
            if "TRANSACTION" in activity['type']:
                for t in activity['transactions']:
                    transactions.append(TransactionView(**t))
        return transactions


class UserWrapper(User):
    """Combines the User model with API functions."""

    def __init__(self, client: 'PMClient', user_data: User):
        super().__init__(**user_data.model_dump(by_alias=True))
        self._client = client

    def balance(self, **kwargs) -> UserBalance:
        """Fetch user balance."""
        endpoint = f"users/{self.id}/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        return UserBalance(**resp['data']['balance'])  # we skip the extra layer of json

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
            cursor (str, optional): Pagination cursor, i.e., the position after which to start.
            limit (int, optional): Number of positions to return per page.
            sort_field (str, optional): Field to sort by.
            sort_direction (str, optional): Sort direction.
            status (str, optional): Status of positions to include.
            **kwargs: Additional keyword arguments to pass to requests.

        Returns:
            tuple: A tuple containing a list of positions, and a paging information.

        Example:
        ```python
        cursor = None
        while True:
            positions, page_info = client.user(user_id).positions(cursor=cursor)
            print(f"Found {len(positions)} positions")
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

    def stats(self, **kwargs) -> UserStatistics:
        """Fetch user statistics."""
        endpoint = f"users/{self.id}/stats"
        resp = self._client.execute_get(endpoint, **kwargs)
        return UserStatistics(**resp['data'])

    def transactions(self, **kwargs) -> tuple[list[TransactionView], PageInfo]:
        """
        Page through transactions of the user.

        Args:
            **kwargs: Additional keyword arguments to pass to requests.

        Returns:
            tuple: A tuple containing a list of transactions, and a paging information.

        Example:
        ```python
        cursor = None
        while True:
            transactions, page_info = client.user(user_id).transactions(cursor=cursor)
            print(f"Found {len(transactions)} transactions")
            cursor = page_info.end_cursor
            if page_info.has_next_page is False:
                break
        ```

        """
        # make request
        endpoint = f"users/{self.id}/transactions"
        response = self._client.execute_get(endpoint, **kwargs)
        return (
            transactions_adapter.validate_python(response['data']),
            PageInfo(**response['pageInfo'])
        )



class CommentResource:
    """Functions to interact with comments via the API."""

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, comment_id: str = None, **kwargs) -> CommentView:
        if comment_id:
            return self.by_id(comment_id, **kwargs)
        return self

    def by_id(self, comment_id: str, **kwargs) -> CommentView:
        """Fetch a comment by ID."""
        endpoint = f"comments/{comment_id}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return CommentView(**resp['data'])

    def create(
        self,
        content: str,
        entity_id: str,
        entity_type: Literal['market', 'list'] = "market",
        parent_id: str | None = None,
        **kwargs) -> Comment:
        """
        Create a comment on an entity.

        Args:
            content (str): Text content of the comment
            entity_id (str): ID of the entity to comment on
            entity_type (str): Type of entity, either 'market' or 'list'
            parent_id (str): ID of the parent comment, if any
            **kwargs: Additional keyword arguments to pass to requests

        Returns:
            Comment: The created comment
        """
        if not self._client.authenticated:
            raise PermissionError("API key required to create comments.")

        endpoint = "comments"
        data = {
            "content": content,
            "entityId": entity_id,
            "entityType": entity_type.upper(),
            "parentId": parent_id
        }
        resp = self._client.execute_post(endpoint, data, **kwargs)
        return Comment(**resp['data'])

    def delete(self, comment_id: str, **kwargs) -> bool:
        """
        Delete a comment.

        Args:
            comment_id (str): ID of the comment to delete
            **kwargs: Additional keyword arguments to pass to requests

        Returns:
            bool: True if the comment was successfully deleted
        """
        if not self._client.authenticated:
            raise PermissionError("API key required to delete comments.")

        endpoint = f"comments/{comment_id}"
        resp = self._client.execute_delete(endpoint, **kwargs)
        if resp == 204:
            return True
        return False

    def update(self, comment_id: str, content: str, **kwargs) -> Comment:
        """
        Update a comment.

        Args:
            comment_id (str): ID of the comment to update
            content (str): New text content for the comment
            **kwargs: Additional keyword arguments to pass to requests

        Returns:
            Comment: The updated comment
        """
        if not self._client.authenticated:
            raise PermissionError("API key required to update comments.")

        endpoint = f"comments/{comment_id}"
        data = {"content": content}
        resp = self._client.execute_patch(endpoint, data, **kwargs)
        return Comment(**resp['data'])

    def react(self, comment_id: str, emoji_code: str = ':+1:', **kwargs) -> CommentReaction:
        """
        React to a comment. Will remove reaction if it already exists.
        
        Args:
            comment_id (str): ID of the comment to react to
            emoji_code (str): Reaction emoji. Must be an :emoji_code:
            **kwargs: Additional keyword arguments to pass to requests
            
        Returns:
            CommentReactionView: Details of the reaction
        """
        # validate input
        if not self._client.authenticated:
            raise PermissionError("API key required to react to comments.")
        try:
            EmojiModel.validate_emoji(emoji_code)
        except ValueError as e:
            raise ValueError(f"Invalid emoji: {emoji_code}") from e
        # make request
        endpoint = f"comments/{comment_id}/reaction"
        data = {"emoji": emoji_code}
        resp = self._client.execute_post(endpoint, data, **kwargs)
        return CommentReaction(**resp['data'])


class MarketListResource:
    """Functions to fetch lists from the API."""

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, list_id: str = None, **kwargs) -> MarketListWrapper:
        if list_id:
            return self.by_id(list_id, **kwargs)
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

    def __call__(self, market_id=None, **kwargs) -> MarketWrapper:
        """Make MarketResource callable."""
        if market_id:
            return self.by_id(market_id, **kwargs)
        return self

    def by_id(self, market_id: str, **kwargs) -> MarketWrapper:
        """Fetch a market by ID."""
        endpoint = f"markets/{market_id}"
        resp = self._client.execute_get(endpoint, **kwargs)
        return MarketWrapper(self._client, Market(**resp['data']))


class MeResource:
    """Functions to fetch the authenticated user."""

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, **kwargs) -> MeWrapper:
        if not self._client.authenticated:
            raise PermissionError("No API key provided.")
        endpoint = "users/me"
        resp = self._client.execute_get(endpoint, **kwargs)
        return MeWrapper(self._client, User(**resp['data']))


class UserResource:
    """Functions to fetch users from the API."""

    def __init__(self, client: 'PMClient'):
        self._client = client

    def __call__(self, user_id=None, **kwargs) -> UserWrapper:
        """Make UserResource callable."""
        if user_id:
            return self.by_id(user_id, **kwargs)
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
        self.me = MeResource(self)
        self.user = UserResource(self)

    def execute_delete(self, endpoint, **kwargs) -> dict:
        """
        Execute a DELETE request to the API.

        Args:
            endpoint (str): The API endpoint to call.
            **kwargs: Additional keyword arguments to pass to requests.
                      Timeout defaults to 10 seconds if not specified.
        """
        url = f"{self.base_url}/{endpoint}"
        timeout = kwargs.pop("timeout", 10)
        try:
            logger.info("Requesting %s. Timeout: %s. Args: %s", url, timeout, kwargs)
            response = requests.delete(url, headers=self.headers, timeout=timeout, **kwargs)
            logger.debug("Response: %s, %s", response.status_code, response.text)
            response.raise_for_status()
            return response.status_code
        except requests.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise

    def execute_get(self, endpoint, **kwargs) -> dict:
        """
        Execute a GET request to the API.

        Args:
            endpoint (str): The API endpoint to call.
            **kwargs: Additional keyword arguments to pass to requests.
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

    def execute_patch(self, endpoint, data, **kwargs) -> dict:
        """
        Execute a PATCH request to the API.

        Args:
            endpoint (str): The API endpoint to call.
            data (dict): The data to patch.
            **kwargs: Additional keyword arguments to pass to requests.
                      Timeout defaults to 10 seconds if not specified.
        """
        url = f"{self.base_url}/{endpoint}"
        timeout = kwargs.pop("timeout", 10)
        try:
            logger.info("Requesting %s. Timeout: %s. Args: %s", url, timeout, kwargs)
            response = requests.patch(
                url, headers=self.headers, json=data, timeout=timeout, **kwargs
            )
            logger.debug("Response: %s, %s", response.status_code, response.text)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise

    def execute_post(self, endpoint, data, **kwargs) -> dict:
        """
        Execute a POST request to the API.

        Args:
            endpoint (str): The API endpoint to call.
            data (dict): The data to post.
            **kwargs: Additional keyword arguments to pass to requests.
                      Timeout defaults to 10 seconds if not specified.
        """
        url = f"{self.base_url}/{endpoint}"
        timeout = kwargs.pop("timeout", 10)
        try:
            logger.info("Requesting %s. Timeout: %s. Args: %s", url, timeout, kwargs)
            response = requests.post(
                url, headers=self.headers, json=data, timeout=timeout, **kwargs
            )
            logger.debug("Response: %s, %s", response.status_code, response.text)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise

    def check_username(self, username: str, **kwargs) -> bool:
        """
        Check if a username is available.

        Args:
            username (str): The username to check.
            **kwargs: Additional keyword arguments to pass to requests.

        Returns:
            bool: True if the username is available, False otherwise.

        """
        endpoint = "users/check-username"
        response = self.execute_get(endpoint, params={"username": username}, **kwargs)
        return response['data']['available']

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
            limit (int, optional): Number of markets to return per page.
            sort_field (str, optional): Field to sort by.
            sort_direction (str, optional): Sort direction.
            status (str, optional): Status of markets to include.
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
            markets_adapter.validate_python(response['data']),
            PageInfo(**response['pageInfo'])
        )

    def leaderboard(self,
        year: int | None = None,
        month: int | None = None,
        **kwargs) -> Leaderboard:
        """
        Fetch the leaderboard.

        Args:
            year (int, optional): Year to filter by.
            month (int, optional): Month to filter by.
        """
        if year < 2024:
            raise ValueError("Year must be 2024 or later.")
        payload = {
            "year": year,
            "month": month,
        }
        response = self.execute_get("leaderboard", params=payload, **kwargs)
        return Leaderboard(**response['data'])

    def lists(self,
        cursor: str | None = None,
        limit: int = 10,
        owner_id: str | None = None,
        sort_field: MarketListSortFieldType | None = None,
        sort_direction: Literal['asc', 'desc'] = 'asc',
        **kwargs) -> tuple[list[MarketListView], PageInfo]:
        """
        Page through all lists.

        Args:
            cursor (str, optional): Pagination cursor, i.e., the list after which to start.
            limit (int, optional): Number of lists to return per page.
            owner_id (str, optional): Filter by ID of the list owner.
            sort_field (str, optional): Field to sort by.
            sort_direction (str, optional): Sort direction.

        Returns:
            tuple: A tuple containing a list of market lists, and a paging information.

        Example:
        ```python
        cursor = None
        while True:
            market_lists, page_info = client.lists(cursor=cursor, limit=5)
            print(f"Found {len(market_lists)} market lists")
            cursor = page_info.end_cursor
            if page_info.has_next_page is False:
                break
        ```

        """
        # validate request
        if cursor and not CUID.validate(cursor):
            raise ValueError(f"`cursor` is an invalid market CUID: {cursor}")
        if owner_id and not CUID.validate(owner_id):
            raise ValueError(f"`owner_id` is an invalid user CUID: {owner_id}")

        # prepare payload
        if sort_field:
            first, *others = sort_field.split('_')
            sort_field = ''.join([first.lower(), *map(str.title, others)])
        payload = {
            "cursor": cursor,
            "ownerId": owner_id,
            "limit": limit,
            "sortField": sort_field,
            "sortDirection": sort_direction
        }

        # make request
        response = self.execute_get("lists", params=payload, **kwargs)
        return (
            market_lists_adapter.validate_python(response['data']),
            PageInfo(**response['pageInfo'])
        )

    def search(self, query, **kwargs) -> SearchResults:
        """
        Search for markets, lists and users.

        Args:
            query (str): Search query. Matches on text fields.
            **kwargs: Additional keyword arguments to pass to requests.

        Returns:
            SearchResults: The search results.

        """
        payload = {"query": query}
        response = self.execute_get("search", params=payload, **kwargs)
        return SearchResults(**response['data'])

    def transactions(self,
        cursor: str | None = None,
        limit: int = 10,
        market_id: str | None = None,
        sort_field: MarketListSortFieldType | None = None,
        sort_direction: Literal['asc', 'desc'] = 'asc',
        transaction_type: TransactionTypes | None = None,
        user_id: str | None = None,
        **kwargs) -> tuple[list[TransactionView], PageInfo]:
        """
        Page through transactions on the site.

        Args:
            cursor (str, optional): Pagination cursor, i.e., the transaction after which to start.
            limit (int, optional): Number of transactions to return per page.
            market_id (str, optional): Only include transaction for this market.
            sort_field (str, optional): Field to sort by.
            sort_direction (str, optional): Sort direction.
            status (str, optional): Status of transactions to include.
            transaction_type (str, optional): Type of transaction to include.
            user_id (str, optional): Only include transaction for this user.

            **kwargs: Additional keyword arguments to pass to requests.

        Returns:
            tuple: A tuple containing a list of transactions, and a paging information.

        Example:
        ```python
        cursor = None
        while True:
            transactions, page_info = client.transactions(cursor=cursor)
            print(f"Found {len(transactions)} transactions")
            cursor = page_info.end_cursor
            if page_info.has_next_page is False:
                break
        ```

        """
        # validate request
        for cuid_field in [cursor, market_id, user_id]:
            if cuid_field and not CUID.validate(cuid_field):
                raise ValueError(f"`{cuid_field}` is an invalid CUID: {cuid_field}")

        # prepare payload
        if sort_field:
            first, *others = sort_field.split('_')
            sort_field = ''.join([first.lower(), *map(str.title, others)])
        if transaction_type:
            transaction_type = transaction_type.upper()
        payload = {
            "cursor": cursor,
            "marketId": market_id,
            "limit": limit,
            "sortField": sort_field,
            "sortDirection": sort_direction,
            "transactionType": transaction_type,
            "userId": user_id
        }

        # make request
        endpoint = "transactions"
        response = self.execute_get(endpoint, params=payload, **kwargs)

        return (
            transactions_adapter.validate_python(response['data']),
            PageInfo(**response['pageInfo'])
        )
