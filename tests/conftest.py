"""
Record all API responses once for consistent testing.

Author: JGY <jean.gabriel.young@gmail.com>
"""
from datetime import datetime
from typing import Any

import pytest
import vcr

from py_play_money import PMClient


# == Helper functions ==
def normalize_datetime(dt_value: Any) -> Any:
    """Convert datetime representations to comparable strings."""
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


def normalize_data(obj: Any) -> Any:
    """Recursively walk dicts/lists, normalizing datetimes and numerical fields."""
    if isinstance(obj, dict):
        normalized = {}
        for k, v in obj.items():
            if k.endswith("At") or k.endswith("Date"):
                normalized[k] = normalize_datetime(v)
            elif k in {"amount", "cost", "quantity", "value", "liquidityProbability"}:
                normalized[k] = float(v)
            else:
                normalized[k] = normalize_data(v)
        return normalized
    elif isinstance(obj, list):
        return [normalize_data(i) for i in obj]
    return obj

# == Fixtures ==
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

    def _check_fields_match(norm_api_data: dict, norm_model_data: dict) -> None:
        """Check that all fields match between API and model data."""
        # Compare values
        for key, value in norm_api_data.items():
            # handle the special case of subtotals
            if key == "subtotals":
                for sub_key, sub_value in value.items():
                    assert sub_key in norm_model_data['subtotals'], (
                        f"Field '{key}.{sub_key}' missing from model"
                    )
                    assert abs(norm_model_data['subtotals'][sub_key] - sub_value) < 1e-10, (
                        f"Field '{key}.{sub_key}' mismatch:\n  API:   {sub_value}\n"
                        "Model: {norm_model_data['subtotals'][sub_key]}"
                    )
            else:
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

    def _compare(
        api_data: dict[str, Any],
        model_dict: dict[str, Any],
    ) -> None:
        """
        Compare API response data with a model dump.

        Args:
            api_data (dict): The raw API response data (camelCase keys).
            model_dict (dict): The model dump (camelCase).

        Raises:
            AssertionError: If any fields mismatch or if extra/missing fields are found.

        """
        # Normalize recursively
        norm_api_data = normalize_data(api_data)
        norm_model_data = normalize_data(model_dict)
        _check_fields_match(norm_api_data, norm_model_data)

    return _compare
