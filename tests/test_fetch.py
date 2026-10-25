from unittest.mock import patch

from src.fetch_weather import fetch


def test_fetch_returns_json():
    fake = {"hourly": {"time": ["t1"], "temperature_2m": [20.0]}}
    with patch("src.fetch_weather.requests.get") as get:
        get.return_value.json.return_value = fake
        get.return_value.raise_for_status.return_value = None
        assert fetch(1.0, 2.0) == fake
