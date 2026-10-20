import os
import numpy as np
from PIL import Image

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def normalize(arr):
    arr = arr.astype(np.float32)
    arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-6)
    return (arr * 255).astype(np.uint8)

def main():
    height_dir = "output/heightmaps"
    flags_dir = "output/flags"
    out_dir = "output/layers"
    ensure_dir(out_dir)

    # Merge tiles into one big heightmap
    tiles = []
    coords = []

    for fname in sorted(os.listdir(height_dir)):
        if not fname.endswith("_height.npy"):
            continue

        parts = fname.split("_")
        zoom = int(parts[1])
        x = int(parts[2])
        y = int(parts[3].split(".")[0])

        height = np.load(os.path.join(height_dir, fname))
        tiles.append(height)
        coords.append((x, y))

    tile_size = tiles[0].shape[0]
    max_x = max(c[0] for c in coords)
    max_y = max(c[1] for c in coords)

    big = np.zeros(((max_y+1)*tile_size, (max_x+1)*tile_size), dtype=np.float32)

    for height, (x, y) in zip(tiles, coords):
        big[y*tile_size:(y+1)*tile_size, x*tile_size:(x+1)*tile_size] = height

    # Compute masks
    slope = np.sqrt(np.gradient(big)[0]**2 + np.gradient(big)[1]**2)
    flatmask = (slope < 0.5).astype(np.uint8) * 255
    seamask = (big < 0).astype(np.uint8) * 255
    rivermask = ((big > 0) & (big < 50)).astype(np.uint8) * 255

    # Biome mask (simple placeholder)
    biomemask = normalize(big)

    # Land type mask (placeholder)
    landmask = normalize(slope)

    # Save PNGs
    Image.fromarray(flatmask).save(os.path.join(out_dir, "flatmask.png"))
    Image.fromarray(seamask).save(os.path.join(out_dir, "seamask.png"))
    Image.fromarray(rivermask).save(os.path.join(out_dir, "rivermask.png"))
    Image.fromarray(biomemask).save(os.path.join(out_dir, "biomemask.png"))
    Image.fromarray(landmask).save(os.path.join(out_dir, "landmask.png"))

    print("Generated terrain layers.")

if __name__ == "__main__":
    main()
