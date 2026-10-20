import os
import requests

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    out_dir = "output/raw_dem"
    ensure_dir(out_dir)

    # Copernicus DEM GLO-30 tile covering Europe/Asia/North Africa
    url = "https://copernicus-dem-30m.s3.amazonaws.com/COP30_EUR_ASIA_NAFRICA.tif"

    dst = os.path.join(out_dir, "copernicus_dem.tif")

    print(f"Downloading Copernicus DEM from {url}")
    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(dst, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Saved DEM to {dst}")

if __name__ == "__main__":
    main()
