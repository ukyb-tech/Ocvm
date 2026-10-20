import os
import numpy as np
from scipy.spatial import Delaunay

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def build_tin_from_height(height: np.ndarray, sample_step: int = 16):
    h, w = height.shape
    xs = np.arange(0, w, sample_step)
    ys = np.arange(0, h, sample_step)
    xx, yy = np.meshgrid(xs, ys)
    points_2d = np.vstack([xx.ravel(), yy.ravel()]).T
    z = height[yy, xx].ravel()

    tri = Delaunay(points_2d)
    vertices = np.column_stack([points_2d, z]).astype(np.float32)
    indices = tri.simplices.astype(np.uint32)
    return vertices, indices

def main():
    in_dir = os.path.join("output", "heightmaps")
    out_dir = os.path.join("output", "tin")
    ensure_dir(out_dir)

    for fname in os.listdir(in_dir):
        if not fname.endswith("_height.npy"):
            continue
        src = os.path.join(in_dir, fname)
        height = np.load(src)
        vertices, indices = build_tin_from_height(height)

        base = fname.replace("_height.npy", "")
        dst = os.path.join(out_dir, f"{base}_tin.npz")
        np.savez(dst, vertices=vertices, indices=indices)
        print(f"Built TIN: {dst}")

if __name__ == "__main__":
    main()
