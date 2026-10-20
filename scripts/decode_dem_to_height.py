import os
import numpy as np

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def main():
    in_dir = os.path.join("output", "raw_dem_tiles")
    out_dir = os.path.join("output", "heightmaps")
    ensure_dir(out_dir)

    for fname in os.listdir(in_dir):
        if not fname.endswith(".npy"):
            continue
        src = os.path.join(in_dir, fname)
        height = np.load(src)
        dst = os.path.join(out_dir, fname.replace(".npy", "_height.npy"))
        np.save(dst, height.astype(np.float32))
        print(f"Decoded heightmap: {dst}")

if __name__ == "__main__":
    main()
