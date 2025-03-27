"""
Handles all API interactions.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import logging

import requests

from py_play_money.schemas import User
from py_play_money import __version__

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


class UserWrapper(User):
    """
    User wrapper.

    Combines the User model with API functions.
    """
    def __init__(self, client, user_data: User):
        super().__init__(**user_data.model_dump(by_alias=True))
        self._client = client

    def balance(self, **kwargs):
        """Fetch user balance."""
        endpoint = f"users/{self.id}/balance"
        resp = self._client.execute_get(endpoint, **kwargs)
        return resp['data']

    def graph(self, **kwargs):
        """Fetch user graphs."""
        resp = self._client.execute_get(f"users/{self.id}/graph", **kwargs)
        return resp['data']

    def positions(self, **kwargs):
        """Fetch current user positions."""
        resp = self._client.execute_get(f"users/{self.id}/positions", **kwargs)
        return resp['data']


class UserResource:
    """
    User resources.
    
    Functions to fetch user information from the API.
    """
    def __init__(self, client):
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
        user_data = User(**resp['data'])
        print(user_data)
        return UserWrapper(self._client, user_data)

    def by_username(self, user_name: str, **kwargs) -> UserWrapper:
        """Fetch a user by username."""
        resp = self._client.execute_get(f"users/username/{user_name}", **kwargs)
        return UserWrapper(self._client, User(**resp['data']))

    # def by_referral(self, code: str, **kwargs) -> UserWrapper:
    #     resp = self.client.execute_get(f"users/referral/{code}", **kwargs)
    #     return UserWrapper(self.client, User(**resp['data']))


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
        from py_play_money import Client
        client = Client()
        # Get a market
        market = client.markets.get(market_id="cm5ifmwfo001g24d2r7fzu34u")
        # Get a user, with timeout
        user = client.users.get(user_id="user123", timeout=5)
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
        # self._market_resource = MarketResource(self)
        self.user = UserResource(self)

    def execute_get(self, endpoint, **kwargs):
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


    # def markets(self, **kwargs):
    #     # Paginated market listing remains intact.
    #     response = self.execute_get("markets", params=kwargs)
    #     markets = [Market(self, m['id']) for m in response['data']]
    #     return markets, response['pageInfo']

    # def check_username(self, user_name, **kwargs):
    #     return self.execute_get(f"users/check-username/{user_name}", **kwargs)['data']
