import os
import math
import requests

# Your bounding box
MIN_LAT = 0.0
MAX_LAT = 75.0
MIN_LON = -18.0
MAX_LON = 180.0

BUCKET = "https://copernicus-dem-30m.s3.amazonaws.com"
OUT_DIR = "output/raw_dem"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def tile_name(lat, lon):
    # Degrees only (no minutes), Copernicus uses 5° steps
    lat_deg = int(lat)
    lon_deg = int(lon)

    if lat_deg >= 0:
        lat_str = f"N{lat_deg:02d}_00"
    else:
        lat_str = f"S{abs(lat_deg):02d}_00"

    if lon_deg >= 0:
        lon_str = f"E{lon_deg:03d}_00"
    else:
        lon_str = f"W{abs(lon_deg):03d}_00"

    return f"Copernicus_DSM_COG_30_{lat_str}_{lon_str}_DEM.tif"

def main():
    ensure_dir(OUT_DIR)

    # Snap to 5-degree grid
    lat_start = math.floor(MIN_LAT / 5) * 5
    lat_end   = math.floor(MAX_LAT / 5) * 5

    lon_start = math.floor(MIN_LON / 5) * 5
    lon_end   = min(math.floor(MAX_LON / 5) * 5, 175)

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
                r = requests.get(url, stream=True, timeout=30)

                if r.status_code == 404:
                    print(f"Missing tile (likely ocean-only): {name}")
                    continue
                if r.status_code != 200:
                    print(f"HTTP {r.status_code} for {name}")
                    continue

                with open(dst, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Saved {dst}")

            except Exception as e:
                print(f"Error downloading {name}: {e}")

    print("Copernicus DEM download complete.")

if __name__ == "__main__":
    main()
