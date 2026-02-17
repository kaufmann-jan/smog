# smog

`smog` computes point-mass clouds from target mass properties (total mass, CoG, and inertias),
and provides output/export helpers and plotting utilities.

## Installation

Install directly from GitHub (including optional plotting/data dependencies):

```bash
pip install "git+https://github.com/kaufmann-jan/smog.git#egg=smog[all]"
```

## Package layout

- `src/smog/cloud.py`: cloud generation and mass-property computations
- `src/smog/io.py`: dataframe conversion and PLY export
- `src/smog/plotting.py`: 3D scatter plotting
- `src/smog/mass_handling.py`: compatibility API that re-exports the main functions

## Example

```python
from smog import point_mass_cloud_from_mass_props, compute_mass_props, scatter_plot

m, cogx, cogy, cogz, xstart, xend, ixx, iyy, izz = (
    285313, 65.0, 0.0, 1.253, 60.0, 70.0, 3245427, 2525644, 5475015
)

B = 11.75
nx, ny, nz = 20, 10, 5

pos, masses = point_mass_cloud_from_mass_props(
    total_mass=m,
    cog_xyz=(cogx, cogy, cogz),
    ixx=ixx,
    iyy=iyy,
    izz=izz,
    n_points=nx * ny * nz,
    span_xyz=(xend - xstart, B, 2 * cogz),
    grid_offset_xyz=(0.0, 0.0, 0.0),
)

print(compute_mass_props(pos, masses))
scatter_plot(pos, masses, save_path="point_mass_cloud.png", show=False)
```

## Development

Create and activate the local virtual environment and install in editable mode with optional dependencies:

```bash
python3 -m venv --prompt smog .venv
source .venv/bin/activate
pip install -e ".[all]"
```
