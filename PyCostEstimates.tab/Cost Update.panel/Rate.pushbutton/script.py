# -*- coding: utf-8 -*-
import os
import csv
import traceback
from pyrevit import revit, DB, forms

doc = revit.doc

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
script_dir = os.path.dirname(__file__)
csv_folder = os.path.join(script_dir, "material_costs")
recipes_csv = os.path.join(script_dir, "recipes.csv")

# ---------------------------------------------------------------------
# Load material prices
# ---------------------------------------------------------------------
material_prices = {}
loaded_files = []

for fname in os.listdir(csv_folder):
    if not fname.endswith(".csv"):
        continue
    with open(os.path.join(csv_folder, fname), "r") as f:
        for row in csv.DictReader(f):
            try:
                material_prices[row["Item"].strip()] = float(row["UnitCost"])
            except:
                pass
    loaded_files.append(fname)

# ---------------------------------------------------------------------
# Load recipes
# ---------------------------------------------------------------------
recipes = {}
with open(recipes_csv, "r") as f:
    for row in csv.DictReader(f):
        try:
            recipes.setdefault(
                row["Type"].strip(), {}
            )[row["Component"].strip()] = float(row["Quantity"])
        except:
            pass

# ---------------------------------------------------------------------
# Collect SAFE element types only
# ---------------------------------------------------------------------
SAFE_CATEGORIES = [
    DB.BuiltInCategory.OST_Walls,
    DB.BuiltInCategory.OST_Floors,
    DB.BuiltInCategory.OST_Roofs,
    DB.BuiltInCategory.OST_Ceilings,
    DB.BuiltInCategory.OST_Doors,
    DB.BuiltInCategory.OST_Windows,
    DB.BuiltInCategory.OST_StructuralColumns,
    DB.BuiltInCategory.OST_StructuralFraming,
]

type_elements = []
for cat in SAFE_CATEGORIES:
    elems = (
        DB.FilteredElementCollector(doc)
        .OfCategory(cat)
        .WhereElementIsElementType()
        .ToElements()
    )
    type_elements.extend(elems)

materials = list(DB.FilteredElementCollector(doc).OfClass(DB.Material))

# ---------------------------------------------------------------------
# Book-keeping (DETAILED)
# ---------------------------------------------------------------------
updated = {}              # {typename: cost}
skipped = {}              # {typename: reason}
missing_materials = set()
paint_updated = {}

# ---------------------------------------------------------------------
# TRANSACTION (SAFE)
# ---------------------------------------------------------------------
try:
    with revit.Transaction("Update Composite & Paint Costs (Detailed)"):

        for elem in type_elements:
            cost_param = elem.LookupParameter("Cost")
            if not cost_param or cost_param.IsReadOnly:
                continue

            name_param = elem.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
            if not name_param:
                continue

            tname = name_param.AsString()
            if not tname or tname not in recipes:
                continue

            total_cost = 0.0
            valid = True

            for mat, qty in recipes[tname].items():
                if mat not in material_prices:
                    missing_materials.add(mat)
                    skipped[tname] = "missing material: {}".format(mat)
                    valid = False
                    break
                total_cost += qty * material_prices[mat]

            if not valid:
                continue

            cost_param.Set(total_cost)
            updated[tname] = total_cost

        # Paint / finishes
        for mat in materials:
            if mat.Name in material_prices:
                p = mat.LookupParameter("Cost")
                if p and not p.IsReadOnly:
                    p.Set(material_prices[mat.Name])
                    paint_updated[mat.Name] = material_prices[mat.Name]

except Exception:
    forms.alert(traceback.format_exc(), title="Cost Update Failed")
    raise

# ---------------------------------------------------------------------
# DETAILED SORTED SUMMARY
# ---------------------------------------------------------------------
summary = []

if updated:
    summary.append("UPDATED TYPE COSTS:")
    for name in sorted(updated):
        summary.append("- {} : {:.2f} ZMW".format(name, updated[name]))

if paint_updated:
    summary.append("\nUPDATED PAINT / FINISH MATERIALS:")
    for name in sorted(paint_updated):
        summary.append("- {} : {:.2f} ZMW".format(name, paint_updated[name]))

if skipped:
    summary.append("\nSKIPPED TYPES:")
    for name in sorted(skipped):
        summary.append("- {} ({})".format(name, skipped[name]))

if missing_materials:
    summary.append("\nMISSING MATERIALS (NOT PRICED):")
    for m in sorted(missing_materials):
        summary.append("- " + m)

if loaded_files:
    summary.append("\nCSVs LOADED:")
    for f in sorted(loaded_files):
        summary.append("- " + f)

if not summary:
    summary = ["No matching types or materials found."]

forms.alert(
    "\n".join(summary),
    title="Composite & Paint Cost Update"
)
