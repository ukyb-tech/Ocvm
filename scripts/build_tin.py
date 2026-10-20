import os
import numpy as np
from scipy.spatial import Delaunay
from scipy.ndimage import sobel, gaussian_filter

HEIGHT_DIR = "output/heightmaps"
TIN_DIR = "output/tin"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def build_tin_for_tile(heightmap_path, out_path,
                       base_step=6,
                       slope_threshold=8.0,
                       curvature_threshold=0.6,
                       variance_threshold=3.0,
                       river_threshold=0.4,
                       edge_threshold=0.7):

    h = np.load(heightmap_path).astype(np.float32)
    ny, nx = h.shape

    # Base sampling (coarse)
    ys, xs = np.mgrid[0:ny:base_step, 0:nx:base_step]
    base_points = np.column_stack([xs.ravel(), ys.ravel(), h[ys, xs].ravel()])

    # Slope refinement
    gy, gx = np.gradient(h)
    slope = np.sqrt(gy**2 + gx**2)
    slope_mask = slope > slope_threshold

    # Curvature refinement
    gyy, gyx = np.gradient(gy)
    gxy, gxx = np.gradient(gx)
    curvature = np.abs(gxx + gyy)
    curvature_mask = curvature > curvature_threshold

    # Variance refinement
    local_var = gaussian_filter((h - h.mean())**2, sigma=1)
    variance_mask = local_var > variance_threshold

    # Hydrology refinement (rivers & basins)
    # Sobel detects flow lines
    flow = np.sqrt(sobel(h, axis=0)**2 + sobel(h, axis=1)**2)
    river_mask = flow < river_threshold  # low gradient = water flow

    # Edge refinement (ridges & cliffs)
    edges = np.sqrt(sobel(h, axis=0)**2 + sobel(h, axis=1)**2)
    edge_mask = edges > edge_threshold

    # Combine masks
    mask = slope_mask | curvature_mask | variance_mask | river_mask | edge_mask
    ys_ref, xs_ref = np.where(mask)
    ref_points = np.column_stack([xs_ref, ys_ref, h[ys_ref, xs_ref]])

    # Combine all points
    points = np.vstack([base_points, ref_points])

    # Optional thinning (performance)
    # Remove points that are too close to each other
    # (simple grid-based thinning)
    keep = []
    seen = set()
    for p in points:
        key = (int(p[0] / 2), int(p[1] / 2))  # 2m grid
        if key not in seen:
            seen.add(key)
            keep.append(p)
    points = np.array(keep)

    # Triangulate
    tri = Delaunay(points[:, :2])

    np.savez(out_path, points=points, triangles=tri.simplices)

def main():
    ensure_dir(TIN_DIR)

    for fname in os.listdir(HEIGHT_DIR):
        if not fname.endswith(".npy"):
            continue

        src = os.path.join(HEIGHT_DIR, fname)
        out = os.path.join(TIN_DIR, fname.replace(".npy", "_tin.npz"))

        print(f"Building optimized TIN for {src}")
        build_tin_for_tile(src, out)

    print("TIN generation complete.")

if __name__ == "__main__":
    main()
