"""Point-mass cloud generation and mass-property utilities."""

from __future__ import annotations

import numpy as np


def _choose_grid_shape(n_points: int) -> tuple[int, int, int]:
    """
    Choose (nx, ny, nz) with nx*ny*nz == n_points and as cubic as possible.
    """
    if n_points < 1:
        raise ValueError("n_points must be >= 1")
    best = None
    best_score = None
    for nx in range(1, int(round(n_points ** (1 / 3))) + 3):
        if n_points % nx != 0:
            continue
        rem = n_points // nx
        for ny in range(1, int(np.sqrt(rem)) + 2):
            if rem % ny != 0:
                continue
            nz = rem // ny
            dims = np.array(sorted([nx, ny, nz]), dtype=float)
            score = dims[-1] / dims[0]
            if best is None or score < best_score:
                best = (nx, ny, nz)
                best_score = score
    if best is None:
        raise ValueError("Could not factor n_points into a 3D grid.")
    return best


def _linspace_centered(n: int, halfspan: float) -> np.ndarray:
    """Return n points in [-halfspan, +halfspan]."""
    if n == 1:
        return np.array([0.0], dtype=float)
    return np.linspace(-halfspan, +halfspan, n, dtype=float)


def _solve_min_variation_nonnegative(
    A: np.ndarray,
    b: np.ndarray,
    m0: np.ndarray,
    *,
    tol: float = 1e-10,
    max_iter: int = 200,
) -> np.ndarray:
    """
    Solve min ||m - m0||^2 with constraints A m = b and m >= 0.
    """
    _, n_vars = A.shape
    free = np.ones(n_vars, dtype=bool)
    m = m0.copy()

    for _ in range(max_iter):
        fixed = ~free
        m[fixed] = 0.0

        afree = A[:, free]
        if afree.size == 0:
            raise ValueError("Infeasible: all variables fixed at 0 but constraints remain.")

        m0f = m0[free]
        rhs = b - A[:, fixed] @ m[fixed] - afree @ m0f

        mmat = afree @ afree.T
        try:
            lam = np.linalg.solve(mmat, rhs)
        except np.linalg.LinAlgError:
            lam = np.linalg.lstsq(mmat, rhs, rcond=None)[0]

        m[free] = m0f + afree.T @ lam

        neg_idx = np.where((m < -tol) & free)[0]
        if neg_idx.size == 0:
            m[m < 0] = 0.0
            afree = A[:, free]
            m0f = m[free]
            rhs = b - A[:, fixed] @ m[fixed] - afree @ m0f
            mmat = afree @ afree.T
            try:
                lam = np.linalg.solve(mmat, rhs)
            except np.linalg.LinAlgError:
                lam = np.linalg.lstsq(mmat, rhs, rcond=None)[0]
            m[free] = m0f + afree.T @ lam
            m[m < 0] = 0.0
            return m

        free[neg_idx] = False

    raise ValueError("Active-set solver did not converge; constraints may be infeasible.")


def point_mass_cloud_from_mass_props(
    total_mass: float,
    cog_xyz: tuple[float, float, float],
    ixx: float,
    iyy: float,
    izz: float,
    n_points: int,
    span_xyz: tuple[float, float, float],
    *,
    tol: float = 1e-8,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build a regular point-mass cloud that matches mass, CoG, and diagonal inertias.
    """
    total_mass = float(total_mass)
    if total_mass <= 0:
        raise ValueError("total_mass must be > 0")
    sx, sy, sz = map(float, span_xyz)
    if sx <= 0 or sy <= 0 or sz <= 0:
        raise ValueError("span_xyz components must be > 0")
    if n_points < 7:
        raise ValueError("n_points must be >= 7 (need at least 7 DoF for constraints).")

    cx, cy, cz = map(float, cog_xyz)

    nx, ny, nz = _choose_grid_shape(n_points)
    x = _linspace_centered(nx, sx / 2.0)
    y = _linspace_centered(ny, sy / 2.0)
    z = _linspace_centered(nz, sz / 2.0)
    grid_x, grid_y, grid_z = np.meshgrid(x, y, z, indexing="ij")
    rel = np.column_stack([grid_x.ravel(), grid_y.ravel(), grid_z.ravel()])
    n_grid = rel.shape[0]
    assert n_grid == n_points

    xi, yi, zi = rel[:, 0], rel[:, 1], rel[:, 2]
    A = np.vstack(
        [
            np.ones(n_grid),
            xi,
            yi,
            zi,
            yi * yi + zi * zi,
            xi * xi + zi * zi,
            xi * xi + yi * yi,
        ]
    )
    b = np.array([total_mass, 0.0, 0.0, 0.0, float(ixx), float(iyy), float(izz)], dtype=float)

    r2_max_x = (sy / 2) ** 2 + (sz / 2) ** 2
    r2_max_y = (sx / 2) ** 2 + (sz / 2) ** 2
    r2_max_z = (sx / 2) ** 2 + (sy / 2) ** 2
    if ixx > total_mass * r2_max_x + 1e-9 or iyy > total_mass * r2_max_y + 1e-9 or izz > total_mass * r2_max_z + 1e-9:
        raise ValueError(
            "Requested inertia is too large for the given mass and span. "
            "Increase span_xyz or reduce ixx/iyy/izz."
        )

    m0 = np.full(n_grid, total_mass / n_grid, dtype=float)
    m = _solve_min_variation_nonnegative(A, b, m0)
    pos = rel + np.array([cx, cy, cz], dtype=float)

    res = A @ m - b
    if np.max(np.abs(res)) > tol * max(1.0, np.max(np.abs(b))):
        raise ValueError(f"Solution residual too large: max|A m - b| = {np.max(np.abs(res))}")
    if np.min(m) < -1e-12:
        raise ValueError("Negative mass found (unexpected after nonnegativity solver).")
    m[m < 0] = 0.0

    keep = m > tol
    return pos[keep], m[keep]


def compute_mass_props(pos: np.ndarray, m: np.ndarray) -> tuple[float, np.ndarray, tuple[float, float, float]]:
    """Compute total mass, CoG, and diagonal inertias about CoG axes."""
    pos = np.asarray(pos, float)
    m = np.asarray(m, float)
    total_mass = m.sum()
    cog = (pos * m[:, None]).sum(axis=0) / total_mass
    rel = pos - cog[None, :]
    x, y, z = rel[:, 0], rel[:, 1], rel[:, 2]
    ixx = (m * (y * y + z * z)).sum()
    iyy = (m * (x * x + z * z)).sum()
    izz = (m * (x * x + y * y)).sum()
    return total_mass, cog, (ixx, iyy, izz)
