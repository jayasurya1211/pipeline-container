import json
import os
import sys
from datetime import datetime, timezone

import requests

URL = "https://api.open-meteo.com/v1/forecast"


def fetch(lat: float, lon: float) -> dict:
    params = {"latitude": lat, "longitude": lon, "hourly": "temperature_2m"}
    resp = requests.get(URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    lat = float(os.getenv("LAT", "17.38"))
    lon = float(os.getenv("LON", "78.48"))
    out_dir = os.getenv("OUT_DIR", "/data")
    os.makedirs(out_dir, exist_ok=True)

    data = fetch(lat, lon)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(out_dir, f"weather_{stamp}.json")
    with open(path, "w") as f:
        json.dump(data, f)
    print(f"wrote {path} with {len(data['hourly']['time'])} hourly rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
