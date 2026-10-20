import os
import json
import math
import argparse
import requests

AWS_TERRAIN_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def latlon_to_tile(lat: float, lon: float, zoom: int):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def main(config_path: str):
    with open(config_path, "r") as f:
        cfg = json.load(f)

    min_lon = cfg["min_lon"]
    max_lon = cfg["max_lon"]
    min_lat = cfg["min_lat"]
    max_lat = cfg["max_lat"]
    zoom    = cfg.get("zoom", 11)

    out_dir = os.path.join("output", "raw_dem_tiles")
    ensure_dir(out_dir)

    # Compute tile range
    x_min, y_max = latlon_to_tile(min_lat, min_lon, zoom)
    x_max, y_min = latlon_to_tile(max_lat, max_lon, zoom)

    x_min, x_max = min(x_min, x_max), max(x_min, x_max)
    y_min, y_max = min(y_min, y_max), max(y_min, y_max)

    print(f"Downloading AWS Terrain-RGB tiles z={zoom}, x={x_min}..{x_max}, y={y_min}..{y_max}")

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            url = AWS_TERRAIN_URL.format(z=zoom, x=x, y=y)
            dst = os.path.join(out_dir, f"tile_{zoom}_{x}_{y}.png")

            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                with open(dst, "wb") as f:
                    f.write(r.content)
                print(f"Downloaded {url} -> {dst}")
            except Exception as e:
                print(f"Failed {url}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    main(args.config)
