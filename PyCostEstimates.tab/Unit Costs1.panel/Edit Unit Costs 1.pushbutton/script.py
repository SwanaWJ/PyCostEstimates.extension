import os
import subprocess
from pyrevit import script

script_dir = os.path.dirname(__file__)

csv_path = os.path.abspath(
    os.path.join(
        script_dir,
        "..",
        "material_costs",
        "material_unit_costs.csv"
    )
)

if not os.path.exists(csv_path):
    script.exit()

try:
    subprocess.Popen(
        ["cmd", "/c", "start", "", csv_path],
        shell=False
    )
except Exception:
    pass
