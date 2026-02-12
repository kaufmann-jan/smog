def write_rbd_pointMasses(df: pd.DataFrame, filepath: str):
    """
    Write a point-mass cloud DataFrame to a text file readable by
    an OpenFOAM Table reader <TableReader<point, scalar>>  List<Tuple2<point, scalar>>

    Each line format:
      ((cogx cogy cogz ) m )

    Requirements:
      - columns: m, cogx, cogy, cogz
      - no header, no index
      - space-separated
    """
    required_cols = ["m", "cogx", "cogy", "cogz"]
    if not all(c in df.columns for c in required_cols):
        raise ValueError(f"DataFrame must contain columns {required_cols}")

    with open(filepath, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            line = (
                f"(({row['cogx']} {row['cogy']} {row['cogz']} ) "
                f"{row['m']} )"
            )
            f.write(line + "\n")

from pathlib import Path

csv_path = Path(__file__).resolve().parents[1] / "tests" / "resources" / "sectional_masses.csv"
masses = pd.read_csv(csv_path)

def B(breadth,x):
    
    if x < 10. or x > 130.:
        return 0.75*breadth
    else:
        return breadth

breadth = 11.75

mass_cloud = []
for i,row in masses.iterrows():   
    pos, m = point_mass_cloud_from_mass_props(
        total_mass=row['m'],
        cog_xyz=(row['cog_x'],row['cog_y'],row['cog_z']),
        ixx=row['Ixx'], iyy=row['Iyy'], izz=row['Izz'], 
        n_points=50*10*10, 
        span_xyz=(row['xend'] - row['xstart'], B(breadth,row['cog_x']), 2*row['cog_z'])
    )

    mass_cloud.append(mass_cloud_to_dataframe(pos,m))

mass_cloud = pd.concat(mass_cloud)
display(mass_cloud)
write_rbd_pointMasses(mass_cloud, 'point_masses.txt')
