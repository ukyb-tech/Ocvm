import os
import rasterio
import numpy as np

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    in_path = "output/raw_dem/copernicus_dem.tif"
    out_dir = "output/heightmaps"
    ensure_dir(out_dir)

    with rasterio.open(in_path) as src:
        arr = src.read(1).astype(np.float32)

    np.save(os.path.join(out_dir, "heightmap.npy"), arr)
    print("Saved heightmap.npy")

if __name__ == "__main__":
    main()
