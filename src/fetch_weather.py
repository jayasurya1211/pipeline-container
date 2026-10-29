import json
import os
import sys
from datetime import datetime, timezone

import requests
from google.cloud import storage

URL = "https://api.open-meteo.com/v1/forecast"


def fetch(lat: float, lon: float) -> dict:
    params = {"latitude": lat, "longitude": lon, "hourly": "temperature_2m"}
    resp = requests.get(URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_blob_name(city: str, now: datetime) -> str:
    return f"raw/weather/dt={now:%Y-%m-%d}/{city}_{now:%Y%m%dT%H%M%SZ}.json"


def upload_to_gcs(bucket_name: str, blob_name: str, payload: str) -> None:
    client = storage.Client()
    blob = client.bucket(bucket_name).blob(blob_name)
    blob.upload_from_string(payload, content_type="application/json")


def main() -> int:
    lat = float(os.getenv("LAT", "17.38"))
    lon = float(os.getenv("LON", "78.48"))
    city = os.getenv("CITY", "hyderabad")
    bucket = os.getenv("BUCKET_NAME")

    data = fetch(lat, lon)
    rows = len(data["hourly"]["time"])
    payload = json.dumps(data)
    now = datetime.now(timezone.utc)

    if bucket:
        blob_name = build_blob_name(city, now)
        upload_to_gcs(bucket, blob_name, payload)
        print(f"uploaded gs://{bucket}/{blob_name} with {rows} hourly rows")
    else:
        out_dir = os.getenv("OUT_DIR", "/data")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"weather_{now:%Y%m%dT%H%M%SZ}.json")
        with open(path, "w") as f:
            f.write(payload)
        print(f"wrote {path} with {rows} hourly rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())