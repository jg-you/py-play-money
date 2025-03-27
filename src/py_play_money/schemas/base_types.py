"""
Custom types.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import re
from datetime import datetime

from pydantic import BaseModel, model_validator


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


class CamelCaseModel(BaseModel):
    """Base model that converts between snake_case (Python) and camelCase (API)."""

    model_config = {
        "populate_by_alias": True,
        "alias_generator": lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    }


class DateModel(CamelCaseModel):
    """Base model for entities with created_at / updated_at pairs."""

    created_at: IsoDatetime
    updated_at: IsoDatetime | None = None

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that the creation date is not after the update date."""
        if self.updated_at is not None:
            if self.created_at >= self.updated_at:
                raise ValueError("Creation date cannot be after the update date.")
        return self

