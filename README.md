# py-play-money

API wrapper for playmoney.dev's API.

API documentation: https://api.playmoney.dev/


## Usage

```python
from py_play_money import PMClient
api_key = None  # optionally set an API key to execute authenticated requests
client = PMClient(api_key)

# Fetch a market
market = client.market(market_id=MARKET_ID)
market = client.market.by_id(market_id=MARKET_ID)

# Access properties of the market
print(market.question)

# Get various details about the market not included in the base request
activity  = market.activity()
balance   = market.balance()
balances  = market.balances()
comments  = market.comments()
graph     = market.graph()
positions = market.positions()
related   = market.related()

# List all markets, with pagination
markets, page_info = client.markets(status='all', limit=10)
if page_info.has_next_page:
    cursor = page_info.end_cursor
    markets, _ = client.markets(status='all', limit=10, cursor=cursor)

# Fetch a user
user = client.user(user_id=USER_ID)
user = client.user.by_id(user_id=USER_ID)
user = client.user.by_username(user_name=USER_NAME)
user = client.user.by_referral(code=REFERRAL_CODE)

# Access properties of the user
print(user.bio)

# Get various details about the user not included in the base request
balance      = user.balance()
graph        = user.graph()
positions    = user.positions()
stats        = user.stats()
transactions = user.transactions()

# Check if a username is available
client.check_username(user_name=USER_NAME)
```