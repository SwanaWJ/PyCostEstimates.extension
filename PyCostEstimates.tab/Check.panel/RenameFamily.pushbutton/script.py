# -*- coding: utf-8 -*-
from pyrevit import revit, forms, script
from Autodesk.Revit.DB import *
import csv
import os

doc = revit.doc

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
CSV_COLUMN = "Type"   # matches your CSV exactly

# --------------------------------------------------
# LOCATE SHARED CSV
# --------------------------------------------------
this_pushbutton = os.path.dirname(script.get_bundle_file("script.py"))
tab_dir = os.path.dirname(os.path.dirname(this_pushbutton))

csv_file = os.path.join(
    tab_dir,
    "Update.panel",
    "Apply Rate.pushbutton",
    "recipes.csv"
)

if not os.path.exists(csv_file):
    forms.alert(
        "CSV file not found:\n{}".format(csv_file),
        exitscript=True
    )

# --------------------------------------------------
# LOAD CSV NAMES
# --------------------------------------------------
csv_names = []

with open(csv_file, "r") as f:
    reader = csv.DictReader(f)

    if CSV_COLUMN not in reader.fieldnames:
        forms.alert(
            "CSV column '{}' not found.\nFound:\n{}"
            .format(CSV_COLUMN, ", ".join(reader.fieldnames)),
            exitscript=True
        )

    for row in reader:
        val = row.get(CSV_COLUMN)
        if val:
            csv_names.append(val.strip())

# remove duplicates, keep order
seen = set()
csv_names = [n for n in csv_names if not (n in seen or seen.add(n))]

if not csv_names:
    forms.alert("No valid names found in CSV.", exitscript=True)

# --------------------------------------------------
# COLLECT FAMILY TYPES (SAFE NAME ACCESS)
# --------------------------------------------------
symbols = (
    FilteredElementCollector(doc)
    .OfClass(FamilySymbol)
    .WhereElementIsElementType()
    .ToElements()
)

if not symbols:
    forms.alert("No family types found in model.", exitscript=True)

def get_type_name(symbol):
    p = symbol.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
    return p.AsString() if p else "<Unnamed>"

family_dict = {}
used_names = set()

for s in symbols:
    name = get_type_name(s)
    key = "{} : {}".format(s.Family.Name, name)
    family_dict[key] = s
    used_names.add(name)

# --------------------------------------------------
# INTERACTIVE RENAME LOOP (100% SAFE)
# --------------------------------------------------
with revit.Transaction("Rename Family Types from Shared CSV"):

    while csv_names and family_dict:

        csv_name = forms.SelectFromList.show(
            csv_names,
            title="Select Build-up Name (CSV)",
            button_name="Use Name"
        )
        if not csv_name:
            break

        if csv_name in used_names:
            forms.alert(
                "This name already exists in the model:\n{}".format(csv_name),
                warn_icon=True
            )
            csv_names.remove(csv_name)
            continue

        fam_key = forms.SelectFromList.show(
            sorted(family_dict.keys()),
            title="Select Family Type to Rename",
            button_name="Rename"
        )
        if not fam_key:
            break

        symbol = family_dict[fam_key]
        old_name = get_type_name(symbol)

        name_param = symbol.get_Parameter(
            BuiltInParameter.SYMBOL_NAME_PARAM
        )

        if not name_param or name_param.IsReadOnly:
            forms.alert(
                "Cannot rename this family type:\n{}".format(old_name),
                warn_icon=True
            )
            continue

        name_param.Set(csv_name)

        # update state
        used_names.add(csv_name)
        csv_names.remove(csv_name)
        family_dict.pop(fam_key)

        if not forms.alert(
            "Renamed:\n{}\n→ {}\n\nContinue?"
            .format(old_name, csv_name),
            ok=False, yes=True, no=True
        ):
            break

forms.alert(
    "Renaming complete.\n\n"
    "Build-up names applied successfully."
)
