import csv
import os
import codecs
from Autodesk.Revit.DB import *
from pyrevit import revit

doc = revit.doc

# Output CSV to Desktop
desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
output_path = os.path.join(desktop, "FamilyTypes_With_Comments.csv")

collector = FilteredElementCollector(doc).OfClass(FamilySymbol)

rows = []

for symbol in collector:
    # Type Name (safe, no .Name)
    name_param = symbol.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
    type_name = name_param.AsString() if name_param else ""

    # Type Comments
    comment_param = symbol.LookupParameter("Type Comments")
    type_comments = comment_param.AsString() if comment_param else ""

    rows.append([type_name or "", type_comments or ""])

# Write UTF-8 CSV (IronPython-safe)
with codecs.open(output_path, "w", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Type", "Type Comments"])
    writer.writerows(rows)

print("CSV created successfully:")
print(output_path)
