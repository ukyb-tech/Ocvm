import os
import yaml
import numpy as np

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

# Bit layout:
# bit 0: flat
# bit 1: river
# bit 2: sea

def compute_slope(height: np.ndarray) -> np.ndarray:
    dy = np.gradient(height, axis=0)
    dx = np.gradient(height, axis=1)
    slope = np.sqrt(dx * dx + dy * dy)
    return slope

def main():
    settings_path = os.path.join("config", "terrain_settings.yaml")
    with open(settings_path, "r") as f:
        cfg = yaml.safe_load(f)

    sea_level = cfg["sea_level"]
    flat_slope_thr = cfg["flat_slope_threshold"]
    flat_var_thr = cfg["flat_variance_threshold"]
    river_elev_max = cfg["river_elevation_max"]

    in_dir = os.path.join("output", "heightmaps")
    out_dir = os.path.join("output", "flags")
    ensure_dir(out_dir)

    for fname in os.listdir(in_dir):
        if not fname.endswith("_height.npy"):
            continue
        src = os.path.join(in_dir, fname)
        height = np.load(src)

        slope = compute_slope(height)
        variance = float(np.var(height))

        flat_flag = int((float(np.mean(slope)) < flat_slope_thr) and (variance < flat_var_thr))

        mean_elev = float(np.mean(height))
        river_flag = int(sea_level < mean_elev < river_elev_max)
        sea_flag = int(mean_elev <= sea_level)

        flag_byte = (flat_flag << 0) | (river_flag << 1) | (sea_flag << 2)

        dst = os.path.join(out_dir, fname.replace("_height.npy", "_flags.bin"))
        with open(dst, "wb") as f:
            f.write(bytes([flag_byte]))
        print(f"Computed flags {flag_byte:08b} for {dst}")

if __name__ == "__main__":
    main()
