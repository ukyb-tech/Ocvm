import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"
OUT_DIR = "output/cop_dem_10m_tiles"

MIN_LAT = 0
MAX_LAT = 75
MIN_LON = -18
MAX_LON = 180

MAX_WORKERS = 32
RETRIES = 2
TIMEOUT = 60

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def tile_id(lat, lon):
    if lat >= 0:
        lat_str = f"N{lat:02d}_00"
    else:
        lat_str = f"S{abs(lat):02d}_00"

    if lon >= 0:
        lon_str = f"E{lon:03d}_00"
    else:
        lon_str = f"W{abs(lon):03d}_00"

    base = f"Copernicus_DSM_COG_10_{lat_str}_{lon_str}_DEM"
    folder = base
    filename = base + ".tif"
    return folder, filename

def download_tile(lat, lon):
    folder, filename = tile_id(lat, lon)
    url = f"{BASE}/{folder}/{filename}"
    dst = os.path.join(OUT_DIR, filename)

    if os.path.exists(dst):
        return f"[{lat},{lon}] Exists — skipped"

    for attempt in range(RETRIES + 1):
        try:
            r = requests.get(url, stream=True, timeout=TIMEOUT)

            if r.status_code == 404:
                return f"[{lat},{lon}] Missing (ocean)"

            if r.status_code != 200:
                msg = f"[{lat},{lon}] HTTP {r.status_code}"
                if attempt < RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                return msg

            with open(dst, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            return f"[{lat},{lon}] Saved"

        except Exception as e:
            if attempt < RETRIES:
                time.sleep(2 ** attempt)
                continue
            return f"[{lat},{lon}] Error: {e}"

def main():
    ensure_dir(OUT_DIR)

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for lat in range(MIN_LAT, MAX_LAT + 1):
            for lon in range(MIN_LON, MAX_LON + 1):
                tasks.append(executor.submit(download_tile, lat, lon))

        for future in as_completed(tasks):
            print(future.result())

    print("Parallel download complete.")

if __name__ == "__main__":
    main()
