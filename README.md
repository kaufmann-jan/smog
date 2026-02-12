# smog

`smog` computes point-mass clouds from target mass properties (total mass, CoG, and inertias),
and provides output/export helpers and plotting utilities.

## Package layout

- `src/smog/cloud.py`: cloud generation and mass-property computations
- `src/smog/io.py`: dataframe conversion and PLY export
- `src/smog/plotting.py`: 3D scatter plotting
- `src/smog/mass_handling.py`: compatibility API that re-exports the main functions

## Development

Create and activate the local virtual environment:

```bash
python3 -m venv --prompt smog .venv
source .venv/bin/activate
```
