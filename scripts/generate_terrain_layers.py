import os
import numpy as np
from scipy.ndimage import gaussian_filter, sobel

HEIGHT_DIR = "output/heightmaps"
LAYER_DIR = "output/layers"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_layers_for_tile(heightmap_path, out_prefix):
    h = np.load(heightmap_path).astype(np.float32)

    # Elevation
    elev = h

    # Slope
    gy, gx = np.gradient(h)
    slope = np.sqrt(gx**2 + gy**2)

    # Curvature
    gyy, gyx = np.gradient(gy)
    gxy, gxx = np.gradient(gx)
    curvature = np.abs(gxx + gyy)

    # Roughness (local variance)
    rough = gaussian_filter((h - h.mean())**2, sigma=1)

    # Hydrology (flow accumulation)
    flow = np.sqrt(sobel(h, axis=0)**2 + sobel(h, axis=1)**2)
    rivers = flow < 0.3  # low gradient = water flow

    # Moisture proxy (low slope + low roughness)
    moisture = gaussian_filter((1 / (1 + slope)) * (1 / (1 + rough)), sigma=2)

    # Terrain classification
    forest = (moisture > 0.6) & (slope < 15)
    marsh = (moisture > 0.75) & (slope < 5)
    mountain = (slope > 25) | (elev > 1800)
    steppe = (moisture < 0.4) & (rough < 10)
    desert = (moisture < 0.25) & (rough > 20)
    tundra = (elev > 1500) & (moisture < 0.4)

    # Save masks
    np.save(out_prefix + "_forest.npy", forest.astype(np.uint8))
    np.save(out_prefix + "_marsh.npy", marsh.astype(np.uint8))
    np.save(out_prefix + "_mountain.npy", mountain.astype(np.uint8))
    np.save(out_prefix + "_steppe.npy", steppe.astype(np.uint8))
    np.save(out_prefix + "_desert.npy", desert.astype(np.uint8))
    np.save(out_prefix + "_tundra.npy", tundra.astype(np.uint8))
    np.save(out_prefix + "_rivers.npy", rivers.astype(np.uint8))

def main():
    ensure_dir(LAYER_DIR)

    for fname in os.listdir(HEIGHT_DIR):
        if not fname.endswith(".npy"):
            continue

        src = os.path.join(HEIGHT_DIR, fname)
        out_prefix = os.path.join(LAYER_DIR, fname.replace(".npy", ""))

        print(f"Generating terrain layers for {src}")
        generate_layers_for_tile(src, out_prefix)

    print("Layer generation complete.")

if __name__ == "__main__":
    main()
