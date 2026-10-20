import os
import requests

# Your bounding box
MIN_LAT = 0
MAX_LAT = 75
MIN_LON = -18
MAX_LON = 180

BUCKET = "https://copernicus-dem-30m.s3.amazonaws.com"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def tile_name(lat, lon):
    # Latitude
    if lat >= 0:
        lat_str = f"N{lat:02d}"
    else:
        lat_str = f"S{abs(lat):02d}"

    # Longitude
    if lon >= 0:
        lon_str = f"E{lon:03d}"
    else:
        lon_str = f"W{abs(lon):03d}"

    return f"Copernicus_DSM_COG_30_{lat_str}{lon_str}.tif"

def main():
    out_dir = "output/raw_dem"
    ensure_dir(out_dir)

    print("Downloading Copernicus DEM tiles...")

    # Loop through 5-degree tiles
    for lat in range(MIN_LAT, MAX_LAT + 1, 5):
        for lon in range(MIN_LON, min(MAX_LON, 175) + 1, 5):

            name = tile_name(lat, lon)
            url = f"{BUCKET}/{name}"
            dst = os.path.join(out_dir, name)

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
