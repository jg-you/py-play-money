"""
Handles all API interactions.

Author: JGY <jeangabriel.young@gmail.com>
"""
import logging
from os import getenv
from importlib.resources import files
from typing import Literal

import yaml
import requests

from py_play_money.schemas import Market, User, Comment


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_configs():
    """
    Retrieve API configurations.
    """
    config_file = files("py_play_money").joinpath("configs.yaml")
    with config_file.open("r") as f:
        return yaml.safe_load(f)


class Client():
    """
    Client for interacting with the Play Money API.
    
    All requests accept keyword arguments that are passed to the `requests` library.

    Examples:
    ```python
    client = Client()
    # Get a market
    market = client.markets.get(market_id="cm5ifmwfo001g24d2r7fzu34u")
    # Get a user, with timeout
    user = client.users.get(user_id="user123", timeout=5)
    ```
    """

    def __init__(self):
        # Load configs
        self.configs = get_configs()
        self.api_version = self.configs['api_version']
        self.base_url = self.configs['base_url'] + f"/{self.api_version}"
        self.api_key = getenv('PLAYMONEY_API_KEY', None)
        if self.api_key is None:
            logger.warning(
                "PLAYMONEY_API_KEY not found in environment, "
                "won't be able to execute POST requests."
            )

        # Set up headers
        self.headers = {
            'User-Agent': 'py-play-money/0.1 (https://github.com/jg-you/py-play-money)'
        }
        if self.api_key:
            self.headers['x-api-key'] = self.api_key

        # Assign resources
        self.market = self.MarketResource(self)
        self.user = self.UserResource(self)

    def execute_get(self, endpoint: str, **kwargs):
        """
        Execute a GET request to the API.

        Parameters:
        - endpoint (str): The API endpoint to call.
        - **kwargs: Additional keyword arguments to pass to the request.
                    Timeout defaults to 10 seconds if not specified.

        Returns:
        - response (requests.Response): The response object from the request.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            if "timeout" not in kwargs:
                timeout = 10
            else:
                timeout = kwargs.pop("timeout")
            response = requests.get(url, headers=self.headers, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response.json()['data']
        except requests.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise

    def markets(self, status=):
        """Page through all markets"""
        return self.market

    class MarketResource:
        """Regroups all resources related to individual markets."""
        def __init__(self, client):
            self.client = client
            
        def get(self, market_id: str, **kwargs) -> Market:
            """Retrieve a market by ID."""
            endpoint = f"markets/{market_id}"
            return Market(**self.client.execute_get(endpoint, **kwargs))

        def get_activity(self, market_id: str, **kwargs):
            pass

        def get_balance(self, market_id: str, **kwargs):
            pass

        def get_balances(self, market_id: str, **kwargs):
            pass

        def get_comments(self, market_id: str, **kwargs) -> list[Comment]:
            """Retrieve comments for a market by ID."""
            endpoint = f"markets/{market_id}/comments"
            data = self.client.execute_get(endpoint, **kwargs)
            return [Comment(**comment) for comment in data]

        def get_graph(self, market_id: str, **kwargs):
            pass

        def get_positions(self, market_id: str, **kwargs):
            pass

        def get_related(self, market_id: str, **kwargs):
            pass

    class UserResource:
        """Regroups all resources related to users."""
        def __init__(self, client):
            self.client = client
            # Assign resources
            self.me = self.Me(client, client.api_key is not None)

        def get(self, user_id: str, **kwargs) -> User:
            """Retrieve user by ID."""
            endpoint = f"users/{user_id}"
            return User(**self.client.execute_get(endpoint, **kwargs))

        def get_by_username(self, user_name: str, **kwargs) -> User:
            """Retrieve user by username."""
            endpoint = f"users/username/{user_name}"
            return User(**self.client.execute_get(endpoint, **kwargs))

        def get_balance(self, user_id: str, **kwargs):
            pass

        def get_graph(self, user_id: str, **kwargs):
            pass

        def get_positions(self, user_id: str, **kwargs):
            pass

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
                return User(**self.client.execute_get(endpoint, **kwargs))

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
