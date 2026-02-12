"""Plot helpers for point-mass clouds."""

from __future__ import annotations

import numpy as np

from smog.cloud import compute_mass_props


def scatter_plot(pos: np.ndarray, m: np.ndarray | None = None):
    """Render a 3D scatter plot of point locations and optional center of mass."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("matplotlib is required for scatter_plot().") from exc

    pos = np.asarray(pos, dtype=float)
    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError("pos must be shaped (N, 3)")

    cog = None
    if m is not None:
        _, cog, _ = compute_mass_props(pos, m)

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(projection="3d")
    ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], s=10, depthshade=True)

    if cog is not None:
        ax.scatter(cog[0], cog[1], cog[2], color="red", s=80, label="centreOfMass")
        ax.legend()

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Point masses generated from mass properties")

    max_range = (pos.max(axis=0) - pos.min(axis=0)).max() / 2.0
    mid = pos.mean(axis=0)
    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    plt.tight_layout()
    plt.show()
