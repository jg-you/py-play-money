"""
Data schemas for the playmoney API.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ================================== Helpers ==================================
class IsoDatetime(datetime):
    """Custom datetime class for ISO formatted strings."""

    @classmethod
    def __get_validators__(cls):
        """Magic method to get validators for the custom datetime class."""
        yield cls.validate

    @classmethod
    def validate(cls, v: str, _):
        """Validate that the input is a valid ISO datetime string."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class CUID(str):
    """CUID v1 type for string validation."""

    _pattern = re.compile(r'^c[^\s-]{8,}$')

    @classmethod
    def __get_validators__(cls):
        """Magic method to get validators for the CUID type."""
        yield cls.validate

    @classmethod
    def validate(cls, v: str, _):
        """Validate that the input is a valid CUID v1 string."""
        if not isinstance(v, str):
            raise TypeError("CUID must be a string")
        if not cls._pattern.match(v):
            raise ValueError(
                "Invalid CUID v1 format. "
                "Must start with 'c' followed by at least 8 non-whitespace characters"
            )
        return cls(v)


class OptionalFieldMixin(BaseModel):
    """Base class to remove optional fields from the model."""

    def __init__(self, **data):
        super().__init__(**data)
        for field in self.model_fields:
            if field not in self.model_fields_set:
                self.__dict__.pop(field, None)

# ================================ Literals ================================

AccountType = Literal["USER", "MARKET_AMM", "MARKET_CLEARING", "HOUSE"]

ActivityType = Literal[
    "COMMENT", 
    "TRADE_TRANSACTION",
    "LIQUIDITY_TRANSACTION",
    "MARKET_CREATED",
    "MARKET_RESOLVED"
]

AssetType = Literal["MARKET_OPTION", "CURRENCY"]

CommentEntityType = Literal["MARKET", "COMMENT"]

ContributionPolicyType = Literal[
    "PUBLIC",
    "DISABLED",
    "OWNERS_ONLY",
    "FRIENDS_ONLY"
]
    
NotificationType = Literal [
    "MARKET_RESOLVED",
    "MARKET_CANCELED",
    "MARKET_TRADE",
    "MARKET_LIQUIDITY_ADDED",
    "MARKET_COMMENT",

    "LIST_COMMENT",
    "LIST_MARKET_ADDED",

    "COMMENT_REPLY",
    "COMMENT_MENTION",
    "COMMENT_REACTION",

    "REFERRER_BONUS",
]

TransactionType = Literal[
    "TRADE_BUY",
    "TRADE_SELL",
    "TRADE_WIN",
    "TRADE_SELL",

    "CREATOR_TRADER_BONUS",

    "LIQUIDITY_INITIALIZE",
    "LIQUIDITY_DEPOSIT",
    "LIQUIDITY_WITHDRAWAL",
    "LIQUIDITY_RETURNED",
    "LIQUIDITY_VOLUME_BONUS",

    "DAILY_TRADE_BONUS",
    "DAILY_MARKET_BONUS",
    "DAILY_COMMENT_BONUS",
    "DAILY_LIQUIDITY_BONUS",

    "HOUSE_GIFT",
    "HOUSE_SIGNUP_BONUS",

    "REFERRER_BONUS",
    "REFERREE_BONUS",
]

UserRoleType = Literal["USER", "ADMIN"]

# ================================ API Schemas ================================
class Market(BaseModel):
    """Market data."""

    # Identifiers
    id: CUID = Field(description="The unique identifier for the market.")
    question: str = Field(description="Short title for the market.")
    description: str = Field(description="Detailed description.")
    slug: str = Field(description="URL-friendly identifier.")
    tags: list[str] = Field(
        default = [],
        description="List of tags associated with the market."
    )
    @property
    def url(self) -> str:
        """Generate the URL for the market."""
        return f"https://playmoney.dev/questions/{self.id}/{self.slug}"

    # Dates
    createdAt: IsoDatetime
    closeDate: IsoDatetime
    resolvedAt: IsoDatetime | None = Field(default=None)
    canceledAt: IsoDatetime | None = Field(default=None)
    updatedAt: IsoDatetime | None = Field(default=None)

    # User IDs
    createdBy: CUID = Field(
        description="ID of the user who created the market."
    )
    ammAccountId: CUID = Field(
        description="ID of the Automated Market Maker associated with the market."
    )
    clearingAccountId: CUID = Field(
        description="ID of the clearing account for the market."
    )
    canceledById: CUID | None = Field(
        description="ID of the user who canceled the market.",
        default=None
    )

    # Activity
    commentCount: int = Field(ge=0)
    uniqueTradersCount: int = Field(ge=0)
    uniquePromotersCount: int = Field(ge=0)
    liquidityCount: int | None = Field(ge=0, default=None)
    parentListId: CUID | None = Field(default=None)

    # Validators
    @model_validator(mode='after')
    def validate_creation_date(self):
        """Validate that the creation date is not after the close date."""
        if self.createdAt > self.closeDate:
            raise ValueError("Creation date cannot be after the close date.")
        return self


class LiteOption(BaseModel):
    """Option with only ID and probability."""

    id: CUID
    probability: int | None = Field(
        ge=0,
        le=100,
        description="Probability percentage (0-100).",
        default=None  # for compatibility with older versions
    )


class Option(LiteOption):
    """Option for a market."""

    name: str
    marketId: CUID
    color: str
    liquidityProbability: float = Field(ge=0, le=1, description="Liquidity probability (0-1).")
    createdAt: IsoDatetime
    updatedAt: IsoDatetime

    @field_validator('color', mode='after')
    @classmethod
    def validate_color(cls, value):
        """Validate that the color is a valid hex color code."""
        if not value.startswith("#") or len(value) != 7:
            raise ValueError("Color must be a valid hex code (e.g., '#FFFFFF').")
        return value


class User(BaseModel):
    """User profile."""

    id: CUID = Field(description="Unique identifier for the user.")
    username: str
    displayName: str
    avatarUrl: str | None = Field(default=None)
    twitterHandle: str | None = Field(default=None)
    discordHandle: str | None = Field(default=None)
    website: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    timezone: str
    primaryAccountId: CUID = Field(description="ID of the user's primary account.")
    role: UserRoleType
    referralCode: str | None = Field(default=None)
    referredBy: CUID | None = Field(default=None)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime


class MarketResolution(BaseModel):
    """Resolution for a market."""

    id: CUID
    marketId: CUID
    resolvedById: CUID
    resolutionId: CUID
    supportingLink: str | None = Field(default=None)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    resolution: Option
    resolvedBy: User
    market: Market



class Account(BaseModel):
    """Account for a user."""

    id: CUID
    type: AccountType
    internalType: str | None = None
    userId: CUID
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    user: User

class FullMarket(Market):
    """Full market data including options, users."""

    def __init__(self, **data):
        """Remove optional fields for some use cases of the model."""
        super().__init__(**data)
        for field in self.model_fields:
            if field not in self.model_fields_set:
                if field in {"resolvedBy", "parentList", "sharedTagsCount", "options", "marketResolution"}:
                    self.__dict__.pop(field, None)

    user: User
    options: list[Option] = Field(default=[])
    marketResolution: MarketResolution | None = Field(default=None)
    resolvedBy: User | None = Field(default=None)
    parentList: str | None = Field(default=None)
    sharedTagsCount: int = Field(default=None)



class MarketList(BaseModel):
    """List of markets."""

    id: CUID
    title: str
    slug: str
    description: str
    ownerId: CUID
    contributionPolicy: ContributionPolicyType
    contributionReview: bool
    tags: list[str]
    createdAt: IsoDatetime
    updatedAt: IsoDatetime


class Reaction(BaseModel):
    """Reaction to comments."""

    id: CUID
    emoji: str
    userId: CUID
    commentId: CUID
    user: User

    @field_validator('emoji', mode='after')
    @classmethod
    def validate_emoji(cls, value):
        """Validate that the emoji is a valid code."""
        if not value.startswith(":") or not value.endswith(":"):
            raise ValueError("Emoji must be in the format ':emoji_code:'")


class Comment(BaseModel):
    """Comment on a market."""

    id: CUID
    content: str
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    edited: bool
    authorId: CUID
    parentId: CUID | None = Field(default=None)
    hidden: bool
    entityId: CUID
    entityType: CommentEntityType
    author: User
    reactions: list[Reaction] = Field(default=[])


class GraphTick(BaseModel):
    """Tick for graph data."""

    startAt: IsoDatetime
    endAt: IsoDatetime
    options: list[LiteOption]


class PageInfo(BaseModel):
    """Cursor for pagination."""

    hasNextPage: bool = False
    endCursor: str | None = Field(default=None)
    total: int = Field(ge=0)


class Position(BaseModel):
    """Position on a market."""

    id: CUID = Field(description="Unique identifier for the position.")
    accountId: CUID = Field(description="ID of the account holding the position.")
    marketId: CUID = Field(description="ID of the market for the position.")
    optionId: CUID = Field(description="ID of the option in the position.")
    cost: float = Field(description="Cost of the position.")
    quantity: float = Field(description="Quantity of the position.")
    value: float = Field(description="Current value of the position.", ge=0)
    createdAt: IsoDatetime = Field(description="Timestamp when the position was created.")
    updatedAt: IsoDatetime = Field(description="Timestamp when the position was last updated.")
    account: Account
    market: Market
    option: Option

    @model_validator(mode='after')
    def validate_update_date(self):
        """Validate that the creation date is not after the update date."""
        if self.createdAt > self.updatedAt:
            raise ValueError("Creation date cannot be after the update date.")
        return self


class TransactionEntry(BaseModel):
    """Ledger entry for a transaction."""

    id: CUID
    amount: float
    assetType: AssetType
    assetId: Literal["PRIMARY"] | CUID
    fromAccountId: CUID
    toAccountId: CUID
    transactionId: CUID
    createdAt: IsoDatetime


class Transaction(BaseModel):
    """Transaction."""

    id: CUID
    type: TransactionType
    initiatorId: CUID
    isReverse: bool | None = Field(default=None)
    reverseOfId: CUID | None = Field(default=None)
    createdAt: IsoDatetime
    updatedAt: IsoDatetime
    batchId: CUID | None = Field(default=None)
    marketId: CUID
    entries: list[TransactionEntry]
    market: Market
    initiator: User
    options: list[Option] = Field(default=[])


class Activity(OptionalFieldMixin):
    """Activity data."""

    type: ActivityType
    timestampAt: IsoDatetime

    # Optional fields, will be removed by mixin if not present
    comment: Comment | None = None
    transactions: list[Transaction] | None = None
    option: Option | None = None
    market: FullMarket | None = None
    marketResolution: MarketResolution | None = None