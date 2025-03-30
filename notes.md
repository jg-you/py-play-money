List of API quirks I worked around

* Accounts inconsistency

  * markets/[ID]/balances :User is stored under account.userPrimary
  * markets/[ID]/positions: User is stored under account.user

  I standardized by choosing userPrimary everywhere

Balances
  * users/[ID]/balance
    A bit weird that the balance is nested under data given there's nothing else in the response.
    I can see the argument for, though given how balance(s) work for markets.
  * markets/[ID]/balances
    Inconsistent schema depending on whether the request is authenticated (user is not included as an empty dict)
  * users/me/balance only returns a number, the rest of the balance endpoints contain more complete information.

Constraint violations?
  * User subtotals don't add up to the total
  * Some balances have update dates that predate their creation. e.g. asset cm65c2om5000lxcoebnye5dqi on list cm5u8dctb0001onmw6aap1vxn

* In general, subtotals have a random assortment of items. 
  I decided to include them all and set unused one to zero.

* Some markets fields are always null?
  E.g.: resolvedAt, canceledAt,

* the GET lists/ endpoints wraps the markets under a list in repeated information.
  unsure what is added by this tripled of ids + created_at

* I decided to replace "activity" by a transaction endpoints that just returns transaction.
  * Comments are available in their own end points,
  * Creation and resolution are available in the market() endpoint directly
  * Which leaves only transaction as the missing piece
  
* Transactions return the option.. which includes a probability
  But that probability is the final value, not at time of purchase, so the information is not super useful

* users/[id]/transactions could use some search options! sort directions etc. 
  Since it is already paginated. And since /transactions has them

* Transactions for daily comment bonuses on a *list* don't return said list.