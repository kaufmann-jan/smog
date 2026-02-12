from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from smog import (
    mass_cloud_to_dataframe,
    point_mass_cloud_from_mass_props,
    write_ply,
    write_rbd_pointMasses,
)


def _breadth_at_x(breadth: float, x: float) -> float:
    if x < 10.0 or x > 130.0:
        return 0.75 * breadth
    return breadth


def test_sectional_mass_pipeline_creates_outputs(tmp_path: Path) -> None:
    pd = pytest.importorskip("pandas")
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    plt = pytest.importorskip("matplotlib.pyplot")

    csv_path = Path(__file__).resolve().parents[1] / "tests" / "resources" / "sectional_masses.csv"
    masses = pd.read_csv(csv_path)
    assert not masses.empty

    breadth = 11.75
    frames = []
    all_pos = []
    all_m = []
    for section in masses.to_dict("records"):
        pos, m = point_mass_cloud_from_mass_props(
            total_mass=float(section["m"]),
            cog_xyz=(float(section["cog_x"]), float(section["cog_y"]), float(section["cog_z"])),
            ixx=float(section["Ixx"]),
            iyy=float(section["Iyy"]),
            izz=float(section["Izz"]),
            n_points=20 * 6 * 6,
            span_xyz=(
                float(section["xend"] - section["xstart"]),
                _breadth_at_x(breadth, float(section["cog_x"])),
                2.0 * float(section["cog_z"]),
            ),
        )
        frames.append(mass_cloud_to_dataframe(pos, m))
        all_pos.append(pos)
        all_m.append(m)

    cloud_df = pd.concat(frames, ignore_index=True)
    pos_cloud = np.vstack(all_pos)
    m_cloud = np.concatenate(all_m)

    rbd_path = tmp_path / "point_masses.txt"
    ply_path = tmp_path / "point_masses.ply"
    png_path = tmp_path / "point_masses_3d.png"

    write_rbd_pointMasses(cloud_df, rbd_path)
    write_ply(ply_path, pos_cloud, m_cloud)

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(projection="3d")
    ax.scatter(pos_cloud[:, 0], pos_cloud[:, 1], pos_cloud[:, 2], s=1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    fig.tight_layout()
    fig.savefig(png_path, dpi=160)
    plt.close(fig)

    assert rbd_path.exists()
    assert ply_path.exists()
    assert png_path.exists()

    ply_text = ply_path.read_text(encoding="utf-8")
    assert "ply" in ply_text.splitlines()[0]
    assert "format ascii 1.0" in ply_text
    assert f"element vertex {len(pos_cloud)}" in ply_text

    rbd_lines = rbd_path.read_text(encoding="utf-8").splitlines()
    assert len(rbd_lines) == len(cloud_df)
    assert rbd_lines[0].startswith("((")
