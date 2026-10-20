import os
import argparse
import numpy as np
from scipy.ndimage import zoom

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def downsample(height: np.ndarray, grid_size: int) -> np.ndarray:
    h, w = height.shape
    zoom_y = grid_size / h
    zoom_x = grid_size / w
    return zoom(height, (zoom_y, zoom_x), order=1).astype(np.float32)

def main(grid_size: int):
    in_dir = os.path.join("output", "heightmaps")
    out_dir = os.path.join("output", "grids_lowres")
    ensure_dir(out_dir)

    for fname in os.listdir(in_dir):
        if not fname.endswith("_height.npy"):
            continue
        src = os.path.join(in_dir, fname)
        height = np.load(src)
        low = downsample(height, grid_size)
        dst = os.path.join(out_dir, fname.replace("_height.npy", f"_grid{grid_size}.npy"))
        np.save(dst, low)
        print(f"Downsampled grid: {dst}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid-size", type=int, required=True)
    args = parser.parse_args()
    main(args.grid_size)
