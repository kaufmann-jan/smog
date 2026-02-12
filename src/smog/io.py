"""Data export and conversion helpers for point-mass clouds."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def mass_cloud_to_dataframe(pos: np.ndarray, m: np.ndarray):
    """
    Create a DataFrame with columns: m, cogx, cogy, cogz.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas is required for mass_cloud_to_dataframe().") from exc

    pos = np.asarray(pos)
    m = np.asarray(m)

    if pos.shape[0] != m.shape[0] or pos.shape[1] != 3:
        raise ValueError("pos must be (N,3) and m must be (N,)")

    return pd.DataFrame(
        {
            "m": m,
            "cogx": pos[:, 0],
            "cogy": pos[:, 1],
            "cogz": pos[:, 2],
        }
    )


def write_ply(filename: str | Path, positions: np.ndarray, m: np.ndarray | None = None) -> None:
    """Write point cloud as ASCII PLY; optionally include mass as vertex property."""
    positions = np.asarray(positions, dtype=float)
    if positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError("positions must be shaped (N, 3)")

    if m is not None:
        m = np.asarray(m, dtype=float)
        if m.shape[0] != positions.shape[0]:
            raise ValueError("m must be shaped (N,) and match positions")

    n_points = positions.shape[0]
    with Path(filename).open("w", encoding="utf-8") as file:
        file.write("ply\n")
        file.write("format ascii 1.0\n")
        file.write(f"element vertex {n_points}\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        if m is not None:
            file.write("property float mass\n")
        file.write("end_header\n")

        for idx in range(n_points):
            if m is None:
                file.write(f"{positions[idx,0]} {positions[idx,1]} {positions[idx,2]}\n")
            else:
                file.write(f"{positions[idx,0]} {positions[idx,1]} {positions[idx,2]} {m[idx]}\n")
