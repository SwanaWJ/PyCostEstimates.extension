# -*- coding: utf-8 -*-
from pyrevit import revit, forms, script
from Autodesk.Revit.DB import *
import csv
import os

doc = revit.doc

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
CSV_COLUMN = "Type"

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
    forms.alert("CSV file not found:\n{}".format(csv_file), exitscript=True)

# --------------------------------------------------
# LOAD CSV
# --------------------------------------------------
csv_names = []
with open(csv_file, "r") as f:
    reader = csv.DictReader(f)
    if CSV_COLUMN not in reader.fieldnames:
        forms.alert("CSV column '{}' not found.".format(CSV_COLUMN), exitscript=True)
    for row in reader:
        if row.get(CSV_COLUMN):
            csv_names.append(row[CSV_COLUMN].strip())

csv_names = list(dict.fromkeys(csv_names))
if not csv_names:
    forms.alert("No valid names found in CSV.", exitscript=True)

# --------------------------------------------------
# COLLECT USED TYPE IDS (CRITICAL)
# --------------------------------------------------
used_type_ids = set()
for el in FilteredElementCollector(doc).WhereElementIsNotElementType():
    try:
        tid = el.GetTypeId()
        if tid and tid != ElementId.InvalidElementId:
            used_type_ids.add(tid)
    except:
        pass

# --------------------------------------------------
# COLLECT ALL VALID MODEL TYPES (SYSTEM + LOADABLE)
# --------------------------------------------------
type_classes = [
    FamilySymbol,
    WallType,
    FloorType,
    RoofType
]

def get_type_name(t):
    p = t.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
    return p.AsString() if p else t.Name

family_dict = {}
used_names = set()

for cls in type_classes:
    types = FilteredElementCollector(doc).OfClass(cls).WhereElementIsElementType()
    for t in types:
        cat = t.Category
        if not cat:
            continue
        if cat.CategoryType != CategoryType.Model:
            continue
        if cat.IsTagCategory:
            continue
        if t.Id not in used_type_ids:
            continue

        type_name = get_type_name(t)
        if not type_name:
            continue

        key = "{} : {}".format(cat.Name, type_name)
        family_dict[key] = t
        used_names.add(type_name)

if not family_dict:
    forms.alert("No valid model types found in the model.", exitscript=True)

# --------------------------------------------------
# INTERACTIVE RENAME
# --------------------------------------------------
with revit.Transaction("Rename Model Types from CSV"):

    while csv_names and family_dict:

        csv_name = forms.SelectFromList.show(
            csv_names,
            title="Select Build-up Name (CSV)",
            button_name="Use Name"
        )
        if not csv_name:
            break

        if csv_name in used_names:
            forms.alert("Name already exists:\n{}".format(csv_name), warn_icon=True)
            csv_names.remove(csv_name)
            continue

        fam_key = forms.SelectFromList.show(
            sorted(family_dict.keys()),
            title="Select Model Type to Rename",
            button_name="Rename"
        )
        if not fam_key:
            break

        elem_type = family_dict[fam_key]
        old_name = get_type_name(elem_type)

        name_param = elem_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
        if not name_param or name_param.IsReadOnly:
            forms.alert("Cannot rename:\n{}".format(old_name), warn_icon=True)
            continue

        name_param.Set(csv_name)

        used_names.add(csv_name)
        csv_names.remove(csv_name)
        family_dict.pop(fam_key)

        if not forms.alert(
            "Renamed:\n{}\n→ {}\n\nContinue?".format(old_name, csv_name),
            ok=False, yes=True, no=True
        ):
            break

forms.alert("Renaming complete.\nBuild-up names applied successfully.")
