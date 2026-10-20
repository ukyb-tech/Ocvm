import os
import rasterio
import numpy as np

RAW_DIR = "output/raw_dem"
OUT_DIR = "output/heightmaps"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    ensure_dir(OUT_DIR)

    print("Decoding Copernicus DEM tiles into heightmaps...")

    for fname in os.listdir(RAW_DIR):
        if not fname.endswith(".tif"):
            continue

        src_path = os.path.join(RAW_DIR, fname)
        out_name = fname.replace(".tif", ".npy")
        out_path = os.path.join(OUT_DIR, out_name)

        try:
            with rasterio.open(src_path) as src:
                arr = src.read(1).astype(np.float32)

            # Save heightmap tile
            np.save(out_path, arr)
            print(f"Saved heightmap: {out_path}")

        except Exception as e:
            print(f"Error decoding {src_path}: {e}")

    print("All Copernicus tiles decoded.")

if __name__ == "__main__":
    main()
