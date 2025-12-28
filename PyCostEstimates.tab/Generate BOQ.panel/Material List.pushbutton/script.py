# -*- coding: utf-8 -*-
"""
Material List Generator
- Reads recipes.csv
- Multiplies material quantities by BOQ family quantities
- Aggregates materials
- Exports shopping-ready CSV
Compatible with pyRevit / IronPython
"""

import csv
import os
from collections import defaultdict


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)

RECIPES_CSV = os.path.join(
    BASE_DIR,
    "..",
    "..",
    "Rate.panel",
    "Rate.pushbutton",
    "recipes.csv"
)

OUTPUT_CSV = os.path.join(BASE_DIR, "Material_List.csv")


# ------------------------------------------------------------
# GET BOQ ITEMS (PLACEHOLDER)
# ------------------------------------------------------------
def get_boq_items():
    """
    MUST return:
    [
        {"boq_item": "<Type>", "family_qty": <number>},
        ...
    ]

    Replace this later with real BOQ extraction logic.
    """

    # TEMP SAMPLE DATA — SAFE DEFAULT
    return [
        {"boq_item": "Foundation walls_200mm", "family_qty": 10},
        {"boq_item": "Concrete_slab_100mm", "family_qty": 5},
        {"boq_item": "Pad footing 1200x1200x300mm thick", "family_qty": 3},
    ]


# ------------------------------------------------------------
# READ RECIPES.CSV (MATCHES YOUR FILE EXACTLY)
# ------------------------------------------------------------
def read_recipes(csv_path):
    recipes = defaultdict(list)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Required columns from your file
            boq_item = row.get("Type", "").strip()
            component = row.get("Component", "").strip()
            qty_raw = row.get("Quantity", "").strip()

            if not boq_item or not component or not qty_raw:
                continue

            # Skip non-material rows
            skip_words = [
                "labour", "transport", "profit",
                "wastage", "plant", "overhead", "hours"
            ]

            if any(w in component.lower() for w in skip_words):
                continue

            # Ignore percentage rows (e.g. 25%, 7%)
            if "%" in qty_raw:
                continue

            try:
                qty = float(qty_raw)
            except:
                continue

            recipes[boq_item].append({
                "material": component,
                "qty_per_family": qty
            })

    return recipes


# ------------------------------------------------------------
# AGGREGATE MATERIALS
# ------------------------------------------------------------
def generate_material_list(boq_items, recipes):
    material_totals = defaultdict(float)

    for item in boq_items:
        boq_name = item["boq_item"]
        family_qty = item["family_qty"]

        if boq_name not in recipes:
            continue

        for mat in recipes[boq_name]:
            material_totals[mat["material"]] += (
                mat["qty_per_family"] * family_qty
            )

    return material_totals


# ------------------------------------------------------------
# EXPORT TO CSV (EXCEL-READY)
# ------------------------------------------------------------
def export_to_csv(materials, output_path):
    with open(output_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Material", "Total Quantity"])

        for material, qty in sorted(materials.items()):
            writer.writerow([material, round(qty, 3)])


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    if not os.path.exists(RECIPES_CSV):
        raise Exception("recipes.csv not found")

    boq_items = get_boq_items()
    recipes = read_recipes(RECIPES_CSV)

    materials = generate_material_list(boq_items, recipes)
    export_to_csv(materials, OUTPUT_CSV)

    print("Material list generated successfully:")
    print(OUTPUT_CSV)


if __name__ == "__main__":
    main()
