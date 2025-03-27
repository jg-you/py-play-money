"""
Custom types.

Author: JGY <jean.gabriel.young@gmail.com>
"""
import re
from datetime import datetime


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
