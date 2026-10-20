import os
import json
import argparse
import numpy as np

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def main(config_path: str):
    with open(config_path, "r") as f:
        cfg = json.load(f)

    zoom = cfg.get("zoom", 11)
    print(f"Using zoom level (synthetic): {zoom}")

    out_dir = os.path.join("output", "raw_dem_tiles")
    ensure_dir(out_dir)

    # Synthetic: 4x4 tiles
    tiles_x = 4
    tiles_y = 4

    for tx in range(tiles_x):
        for ty in range(tiles_y):
            size = 256
            x = np.linspace(0, 1, size)
            y = np.linspace(0, 1, size)
            xx, yy = np.meshgrid(x, y)

            # Synthetic terrain: hills + offset per tile
            height = (
                100.0 * np.sin(xx * np.pi) * np.cos(yy * np.pi)
                + 20.0 * (tx + ty)
            )

            path = os.path.join(out_dir, f"tile_{tx}_{ty}.npy")
            np.save(path, height.astype(np.float32))
            print(f"Saved synthetic DEM tile: {path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    main(args.config)
