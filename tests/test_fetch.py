from datetime import datetime, timezone
from unittest.mock import patch

from src.fetch_weather import build_blob_name, fetch, main

FAKE = {"hourly": {"time": ["t1"], "temperature_2m": [20.0]}}


def test_fetch_returns_json():
    with patch("src.fetch_weather.requests.get") as get:
        get.return_value.json.return_value = FAKE
        get.return_value.raise_for_status.return_value = None
        assert fetch(1.0, 2.0) == FAKE


def test_build_blob_name():
    now = datetime(2026, 10, 29, 5, 30, 0, tzinfo=timezone.utc)
    assert (
        build_blob_name("hyderabad", now)
        == "raw/weather/dt=2026-10-29/hyderabad_20261029T053000Z.json"
    )


def test_main_uploads_when_bucket_set(monkeypatch):
    monkeypatch.setenv("BUCKET_NAME", "test-bucket")
    with patch("src.fetch_weather.fetch", return_value=FAKE), patch(
        "src.fetch_weather.storage.Client"
    ) as client:
        assert main() == 0
    bucket = client.return_value.bucket
    bucket.assert_called_once_with("test-bucket")
    assert bucket.return_value.blob.call_args[0][0].startswith("raw/weather/dt=")


def test_main_writes_local_without_bucket(monkeypatch, tmp_path):
    monkeypatch.delenv("BUCKET_NAME", raising=False)
    monkeypatch.setenv("OUT_DIR", str(tmp_path))
    with patch("src.fetch_weather.fetch", return_value=FAKE):
        assert main() == 0
    assert len(list(tmp_path.glob("weather_*.json"))) == 1