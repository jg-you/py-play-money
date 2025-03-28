List of API quirks I worked around

* Accounts inconsistency

  * markets/[ID]/balances :User is stored under account.userPrimary
  * markets/[ID]/positions: User is stored under account.user

    I standardized by choosing userPrimary everywhere
* markets/[ID]/balances
  Returns the data with an additional layer of json
  (data.balance, whereas the rest of the API returns data directly)
* users/[ID]/balances
  Same as above
  data.balances instead of data
* Subtotals:
  In general, subtotals have a random assortment of items. I decided to include them all
  and set unused one to zero

  I'm also noting that user subtotals don't add up to the total.
