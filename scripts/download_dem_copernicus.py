import os
import requests

BASE = "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"
OUT_DIR = "output/cop_dem_10m_tiles"

MIN_LAT = 0
MAX_LAT = 75
MIN_LON = -18
MAX_LON = 180

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def tile_id(lat, lon):
    # Latitude
    if lat >= 0:
        lat_str = f"N{lat:02d}_00"
    else:
        lat_str = f"S{abs(lat):02d}_00"

    # Longitude
    if lon >= 0:
        lon_str = f"E{lon:03d}_00"
    else:
        lon_str = f"W{abs(lon):03d}_00"

    base = f"Copernicus_DSM_COG_10_{lat_str}_{lon_str}_DEM"
    folder = base
    filename = base + ".tif"
    return folder, filename

def main():
    ensure_dir(OUT_DIR)

    for lat in range(MIN_LAT, MAX_LAT + 1):
        for lon in range(MIN_LON, MAX_LON + 1):

            folder, filename = tile_id(lat, lon)
            url = f"{BASE}/{folder}/{filename}"
            dst = os.path.join(OUT_DIR, filename)

            print(f"Fetching {url}")

            r = requests.get(url, stream=True, timeout=30)

            if r.status_code == 404:
                print(f"Missing tile: {filename}")
                continue

            if r.status_code != 200:
                print(f"HTTP {r.status_code} for {filename}")
                continue

            with open(dst, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Saved {dst}")

    print("Download complete.")

if __name__ == "__main__":
    main()
