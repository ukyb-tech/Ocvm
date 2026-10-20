import os
import numpy as np
from PIL import Image

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def normalize_to_8bit(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype(np.float32)
    min_val = float(arr.min())
    max_val = float(arr.max())
    if max_val == min_val:
        return np.zeros_like(arr, dtype=np.uint8)
    norm = (arr - min_val) / (max_val - min_val)
    return (norm * 255.0).clip(0, 255).astype(np.uint8)

def main():
    height_dir = os.path.join("output", "heightmaps")
    flags_dir = os.path.join("output", "flags")
    out_dir = os.path.join("output", "worldpainter")
    ensure_dir(out_dir)

    # For simplicity, merge all tiles into one big heightmap (4x4 tiles).
    tiles = []
    coords = []

    for fname in sorted(os.listdir(height_dir)):
        if not fname.endswith("_height.npy"):
            continue
        parts = fname.split("_")
        if len(parts) < 3:
            continue
        try:
            tx = int(parts[1])
            ty = int(parts[2].split("_")[0])
        except ValueError:
            continue
        height = np.load(os.path.join(height_dir, fname))
        tiles.append(height)
        coords.append((tx, ty))

    if not tiles:
        print("No heightmaps found for WorldPainter export.")
        return

    # Assume 4x4 tiles as in download_dem.py
    tile_size = tiles[0].shape[0]
    grid_x = max(c[0] for c in coords) + 1
    grid_y = max(c[1] for c in coords) + 1

    big_h = tile_size * grid_y
    big_w = tile_size * grid_x
    big_height = np.zeros((big_h, big_w), dtype=np.float32)

    for height, (tx, ty) in zip(tiles, coords):
        y0 = ty * tile_size
        x0 = tx * tile_size
        big_height[y0:y0+tile_size, x0:x0+tile_size] = height

    # Heightmap PNG
    height_8 = normalize_to_8bit(big_height)
    Image.fromarray(height_8, mode="L").save(os.path.join(out_dir, "heightmap.png"))
    print("Saved WorldPainter heightmap: output/worldpainter/heightmap.png")

    # Masks: flat / river / sea
    flat_mask = np.zeros_like(big_height, dtype=np.uint8)
    river_mask = np.zeros_like(big_height, dtype=np.uint8)
    sea_mask = np.zeros_like(big_height, dtype=np.uint8)

    for fname in sorted(os.listdir(flags_dir)):
        if not fname.endswith("_flags.bin"):
            continue
        parts = fname.split("_")
        if len(parts) < 3:
            continue
        try:
            tx = int(parts[1])
            ty = int(parts[2].split("_")[0])
        except ValueError:
            continue

        with open(os.path.join(flags_dir, fname), "rb") as f:
            flag_byte = f.read(1)[0]

        flat_flag = (flag_byte & 0b00000001) != 0
        river_flag = (flag_byte & 0b00000010) != 0
        sea_flag = (flag_byte & 0b00000100) != 0

        y0 = ty * tile_size
        x0 = tx * tile_size

        if flat_flag:
            flat_mask[y0:y0+tile_size, x0:x0+tile_size] = 255
        if river_flag:
            river_mask[y0:y0+tile_size, x0:x0+tile_size] = 255
        if sea_flag:
            sea_mask[y0:y0+tile_size, x0:x0+tile_size] = 255

    Image.fromarray(flat_mask, mode="L").save(os.path.join(out_dir, "flat_mask.png"))
    Image.fromarray(river_mask, mode="L").save(os.path.join(out_dir, "river_mask.png"))
    Image.fromarray(sea_mask, mode="L").save(os.path.join(out_dir, "sea_mask.png"))
    print("Saved WorldPainter masks: flat_mask.png, river_mask.png, sea_mask.png")

if __name__ == "__main__":
    main()
