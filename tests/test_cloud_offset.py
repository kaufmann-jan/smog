from __future__ import annotations

import numpy as np

from smog import compute_mass_props, point_mass_cloud_from_mass_props


def test_point_cloud_can_be_shifted_relative_to_cog() -> None:
    pos, m = point_mass_cloud_from_mass_props(
        total_mass=10.0,
        cog_xyz=(0.0, 0.0, 1.0),
        ixx=9.0,
        iyy=10.0,
        izz=5.0,
        n_points=64,
        span_xyz=(2.0, 2.0, 4.0),
        grid_offset_xyz=(0.0, 0.0, 1.0),
    )

    # Requested z-span: 0..4 when CoG z=1 and z-offset=+1 with span=4.
    assert pos[:, 2].min() >= -1e-9
    assert pos[:, 2].max() <= 4.0 + 1e-9

    total_mass, cog, (ixx, iyy, izz) = compute_mass_props(pos, m)
    assert np.isclose(total_mass, 10.0, atol=1e-6)
    assert np.allclose(cog, np.array([0.0, 0.0, 1.0]), atol=1e-6)
    assert np.isclose(ixx, 9.0, atol=1e-5)
    assert np.isclose(iyy, 10.0, atol=1e-5)
    assert np.isclose(izz, 5.0, atol=1e-5)
