# Notebooks

`smog_usage_example.ipynb` shows a full package workflow using
`tests/resources/sectional_masses.csv`:

- generate sectional point-mass clouds
- combine them into one cloud
- export OpenFOAM point masses (`.txt`)
- export ParaView-readable point cloud (`.ply`)
- visualize with a 3D matplotlib plot

Run from the repository root after installing optional dependencies:

```bash
source .venv/bin/activate
pip install -e ".[all]"
jupyter notebook notebooks/smog_usage_example.ipynb
```

Install directly from GitHub (including optional plotting/data dependencies):

```bash
pip install "git+https://github.com/kaufmann-jan/smog.git#egg=smog[all]"
```
