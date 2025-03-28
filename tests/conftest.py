"""
Record all API responses once for consistent testing.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from datetime import datetime
from typing import Any

import pytest
import vcr

from py_play_money import PMClient


@pytest.fixture
def client():
    """Fixture to create a PMClient instance."""
    return PMClient()

@pytest.fixture(scope="session")
def vcr_record():
    """Fixture to record API responses using VCR.py."""
    return vcr.VCR(
        cassette_library_dir='tests/cassettes',
        record_mode='once',
        match_on=['uri', 'method', 'body'],
        filter_headers=['authorization']
    )

@pytest.fixture
def compare_api_model():
    """Fixture that returns a function to compare API response data with a model dump."""

    def _normalize_datetime(dt_value: Any) -> Any:
        """
        Convert different datetime representations to comparable strings, always returning
        ISO 8601 with millisecond precision and a trailing 'Z' for UTC. If not a valid date,
        return as-is.
        """
        if dt_value is None:
            return None
        if isinstance(dt_value, datetime):
            return dt_value.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        if isinstance(dt_value, str):
            try:
                dt_obj = datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
                return dt_obj.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            except ValueError:
                return dt_value
        return dt_value

    def _normalize_data(obj: Any, dt_fields: set[str]) -> Any:
        """
        Recursively walk dicts/lists, normalizing values if their keys match
        known datetime fields. Everything else is returned as-is.
        """
        if isinstance(obj, dict):
            normalized = {}
            for k, v in obj.items():
                if k in dt_fields or k.endswith("At") or k.endswith("Date"):
                    normalized[k] = _normalize_datetime(v)
                else:
                    normalized[k] = _normalize_data(v, dt_fields)
            return normalized
        elif isinstance(obj, list):
            return [_normalize_data(i, dt_fields) for i in obj]
        return obj

    def _compare(
        api_data: dict[str, Any],
        model_dict: dict[str, Any],
        ignore_fields: list[str] = None,
        datetime_fields: list[str] = None
    ) -> None:
        """
        Compare API response data with a model dump.

        Args:
            api_data (dict): The raw API response data (camelCase keys).
            model_dict (dict): The model dump (camelCase).
            ignore_fields (list): Top-level fields to ignore in the comparison.
            datetime_fields (list): Fields to treat as datetimes (in addition to those ending in 'At'/'Date').

        Raises:
            AssertionError: If any fields mismatch or if extra/missing fields are found.
        """
        ignore_fields = ignore_fields or []
        dt_fields = set(datetime_fields or [])

        # Normalize recursively
        norm_api_data = _normalize_data(api_data, dt_fields)
        norm_model_data = _normalize_data(model_dict, dt_fields)

        # Remove ignored top-level keys
        for field in ignore_fields:
            norm_api_data.pop(field, None)
            norm_model_data.pop(field, None)

        # Compare values
        for key, value in norm_api_data.items():
            assert key in norm_model_data, f"Field '{key}' missing from model"
            assert norm_model_data[key] == value, (
                f"Field '{key}' mismatch:\n  API:   {value}\n  Model: {norm_model_data[key]}"
            )

        # Check for extra fields in the model
        extra_keys = set(norm_model_data) - set(norm_api_data)
        assert not extra_keys, f"Model has extra fields: {extra_keys}"

        # Check for missing fields in the model
        missing_keys = set(norm_api_data) - set(norm_model_data)
        assert not missing_keys, f"Model is missing fields: {missing_keys}"

    return _compare
