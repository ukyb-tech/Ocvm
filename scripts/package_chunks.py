import os
import struct
import numpy as np

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def main():
    grids_dir = os.path.join("output", "grids_lowres")
    tin_dir = os.path.join("output", "tin")
    flags_dir = os.path.join("output", "flags")
    out_dir = os.path.join("output", "game_terrain", "chunks")
    ensure_dir(out_dir)

    for grid_fname in os.listdir(grids_dir):
        if not grid_fname.endswith(".npy"):
            continue

        base = grid_fname.split("_height")[0]  # tile_X_Y
        grid_path = os.path.join(grids_dir, grid_fname)
        grid = np.load(grid_path).astype(np.float32)
        grid_size = grid.shape[0]

        tin_path = os.path.join(tin_dir, f"{base}_tin.npz")
        if not os.path.exists(tin_path):
            print(f"Missing TIN for {base}, skipping.")
            continue
        tin_data = np.load(tin_path)
        vertices = tin_data["vertices"].astype(np.float32)
        indices = tin_data["indices"].astype(np.uint32)

        flags_path = os.path.join(flags_dir, f"{base}_flags.bin")
        if not os.path.exists(flags_path):
            print(f"Missing flags for {base}, skipping.")
            continue
        with open(flags_path, "rb") as f:
            flag_byte = f.read(1)
        flag_val = flag_byte[0]

        chunk_path = os.path.join(out_dir, f"{base}.terrainchunk")
        with open(chunk_path, "wb") as f:
            # Header
            f.write(b"TRN1")
            f.write(struct.pack("<I", grid_size))
            f.write(struct.pack("<I", vertices.shape[0]))
            f.write(struct.pack("<I", indices.shape[0]))
            f.write(flag_byte)

            # Grid
            f.write(grid.tobytes(order="C"))

            # Vertices
            f.write(vertices.tobytes(order="C"))

            # Indices
            f.write(indices.tobytes(order="C"))

        print(f"Packed chunk: {chunk_path} (flags={flag_val:08b})")

if __name__ == "__main__":
    main()
