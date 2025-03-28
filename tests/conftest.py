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
    """
    Fixture that returns a function to compare API response data with a model dump.

    Handles camelCase to snake_case conversion and special cases like datetime fields.
    """
    def _normalize_datetime(dt_value):
        """Convert different datetime representations to comparable strings."""
        if dt_value is None:
            return None
        if isinstance(dt_value, str):
            try:
                dt_obj = datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
            except ValueError:
                return dt_value
        elif isinstance(dt_value, datetime):
            dt_obj = dt_value
        else:
            return dt_value
        return dt_obj.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def _compare(
        api_data: dict[str, Any],
        model_dict: dict[str, Any],
        ignore_fields: list[str] = None,
        datetime_fields: list[str] = None
    ) -> None:
        """
        Compare API response data with a model dump.

        Args:
            api_data: The raw API response data (camelCase keys)
            model_dict: The model dump (with snake_case keys translated to camelCase)
            ignore_fields: List of fields to ignore in the comparison
            datetime_fields: List of fields that should be treated as datetimes

        """
        ignore_fields = ignore_fields or []
        if datetime_fields is None:
            datetime_fields = [k for k in api_data if k.endswith("At") or k.endswith("Date")]

        api_filtered = {k: v for k, v in api_data.items() if k not in ignore_fields}
        model_filtered = {k: v for k, v in model_dict.items() if k not in ignore_fields}

        for key, value in api_filtered.items():
            assert key in model_filtered, f"Field '{key}' missing from model"
            if key in datetime_fields and value is not None:
                norm_api = _normalize_datetime(value)
                norm_model = _normalize_datetime(model_filtered[key])
                assert norm_api == norm_model, (
                    f"Field '{key}' datetime mismatch: API: {value}, Model: {model_filtered[key]}"
                )
            else:
                assert model_filtered[key] == value, (
                    f"Field '{key}' incorrect: expected {value}, got {model_filtered[key]}"
                )

        extra_keys = set(model_filtered) - set(api_filtered)
        assert not extra_keys, f"Model has extra fields: {extra_keys}"
        missing_keys = set(api_filtered) - set(model_filtered)
        assert not missing_keys, f"Model is missing fields: {missing_keys}"

    return _compare
