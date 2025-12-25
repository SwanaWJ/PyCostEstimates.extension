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
for fname in os.listdir(csv_folder):
    if not fname.endswith(".csv"):
        continue
    with open(os.path.join(csv_folder, fname), "r") as f:
        for row in csv.DictReader(f):
            try:
                material_prices[row["Item"].strip()] = float(row["UnitCost"])
            except:
                pass

# ---------------------------------------------------------------------
# Load recipes
# ---------------------------------------------------------------------
recipes = {}
with open(recipes_csv, "r") as f:
    for row in csv.DictReader(f):
        try:
            recipes.setdefault(row["Type"].strip(), {})[
                row["Component"].strip()
            ] = float(row["Quantity"])
        except:
            pass

# ---------------------------------------------------------------------
# Collect ONLY SAFE TYPES (NO RAW FamilySymbol)
# ---------------------------------------------------------------------
type_collections = []

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

for cat in SAFE_CATEGORIES:
    elems = (
        DB.FilteredElementCollector(doc)
        .OfCategory(cat)
        .WhereElementIsElementType()
        .ToElements()
    )
    type_collections.extend(elems)

materials = list(DB.FilteredElementCollector(doc).OfClass(DB.Material))

updated = []
skipped = []
missing = set()
paint_updated = []

# ---------------------------------------------------------------------
# TRANSACTION (VERY CONTROLLED)
# ---------------------------------------------------------------------
try:
    with revit.Transaction("Update Composite & Paint Costs (Safe)"):

        for elem in type_collections:
            cost_param = elem.LookupParameter("Cost")
            if not cost_param or cost_param.IsReadOnly:
                continue

            name_param = elem.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
            if not name_param:
                continue

            tname = name_param.AsString()
            if not tname or tname not in recipes:
                continue

            total = 0.0
            valid = True
            for mat, qty in recipes[tname].items():
                if mat not in material_prices:
                    missing.add(mat)
                    valid = False
                    break
                total += qty * material_prices[mat]

            if not valid:
                skipped.append(tname)
                continue

            cost_param.Set(total)
            updated.append((tname, total))

        # Paint materials
        for mat in materials:
            if mat.Name in material_prices:
                p = mat.LookupParameter("Cost")
                if p and not p.IsReadOnly:
                    p.Set(material_prices[mat.Name])
                    paint_updated.append(mat.Name)

except Exception:
    forms.alert(traceback.format_exc(), title="Crash Guard")
    raise

# ---------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------
summary = []
summary.append("Updated Types: {}".format(len(updated)))
summary.append("Updated Paint Materials: {}".format(len(paint_updated)))
summary.append("Skipped Types: {}".format(len(skipped)))
summary.append("Missing Materials: {}".format(len(missing)))

forms.alert("\n".join(summary), title="Cost Update Complete")
