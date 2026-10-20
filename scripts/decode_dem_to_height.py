import os
import numpy as np
from PIL import Image

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def terrain_rgb_to_height(img: Image.Image) -> np.ndarray:
    arr = np.array(img).astype(np.float32)
    if arr.shape[2] == 4:
        arr = arr[:, :, :3]  # drop alpha

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    height = (r * 256.0 + g + b / 256.0) - 32768.0
    return height.astype(np.float32)

def main():
    in_dir = os.path.join("output", "raw_dem_tiles")
    out_dir = os.path.join("output", "heightmaps")
    ensure_dir(out_dir)

    for fname in os.listdir(in_dir):
        if not fname.endswith(".png"):
            continue

        src = os.path.join(in_dir, fname)
        img = Image.open(src).convert("RGBA")
        height = terrain_rgb_to_height(img)

        dst = os.path.join(out_dir, fname.replace(".png", "_height.npy"))
        np.save(dst, height)
        print(f"Decoded {src} -> {dst}")

if __name__ == "__main__":
    main()
