from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from smog import scatter_plot


def test_scatter_plot_can_save_png_and_return_axis(tmp_path: Path) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")

    pos = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.5],
            [0.0, 1.0, 1.0],
            [1.0, 1.0, 1.5],
        ],
        dtype=float,
    )
    m = np.array([1.0, 1.0, 1.0, 1.0], dtype=float)
    out_png = tmp_path / "scatter.png"

    ax = scatter_plot(pos, m, save_path=out_png, show=False, return_ax=True)

    assert out_png.exists()
    assert ax is not None
