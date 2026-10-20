import os
import math
import requests

# Your original bounding box
MIN_LAT = 0.0
MAX_LAT = 75.0
MIN_LON = -18.0
MAX_LON = 180.0

BUCKET = "https://copernicus-dem-30m.s3.amazonaws.com"
OUT_DIR = "output/raw_dem"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def tile_name(lat, lon):
    # Latitude
    if lat >= 0:
        lat_str = f"N{int(lat):02d}"
    else:
        lat_str = f"S{int(abs(lat)):02d}"

    # Longitude
    if lon >= 0:
        lon_str = f"E{int(lon):03d}"
    else:
        lon_str = f"W{int(abs(lon)):03d}"

    return f"Copernicus_DSM_COG_30_{lat_str}{lon_str}.tif"

def main():
    ensure_dir(OUT_DIR)

    # Snap to 5-degree grid
    lat_start = math.floor(MIN_LAT / 5) * 5
    lat_end   = math.floor(MAX_LAT / 5) * 5

    lon_start = math.floor(MIN_LON / 5) * 5
    lon_end   = math.floor(MAX_LON / 5) * 5

    # Clamp longitude to Copernicus DEM limit (175E)
    lon_end = min(lon_end, 175)

    print(f"Lat range: {lat_start} to {lat_end} (step 5)")
    print(f"Lon range: {lon_start} to {lon_end} (step 5)")

    print("Downloading Copernicus DEM tiles...")

    for lat in range(int(lat_start), int(lat_end) + 1, 5):
        for lon in range(int(lon_start), int(lon_end) + 1, 5):

            name = tile_name(lat, lon)
            url = f"{BUCKET}/{name}"
            dst = os.path.join(OUT_DIR, name)

            print(f"Fetching {url}")

            try:
                r = requests.get(url, stream=True, timeout=20)
                if r.status_code == 200:
                    with open(dst, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Saved {dst}")
                else:
                    print(f"Tile missing: {url} (HTTP {r.status_code})")
            except Exception as e:
                print(f"Error downloading {url}: {e}")

    print("Copernicus DEM download complete.")

if __name__ == "__main__":
    main()
