from pyrevit import revit, forms
from Autodesk.Revit.DB import (
    BuiltInParameter,
    ElementId,
    ParameterFilterElement,
    ElementParameterFilter,
    FilterStringRule,
    FilterStringEquals,
    ParameterValueProvider,
    FilteredElementCollector,
    View3D,
    ViewDuplicateOption
)
from System.Collections.Generic import List

doc = revit.doc
uidoc = revit.uidoc
active_view = doc.ActiveView

# --------------------------------------------------
# BASIC VALIDATION
# --------------------------------------------------
if not isinstance(active_view, View3D):
    forms.alert(
        "Please run this tool from a 3D View.",
        exitscript=True
    )

# --------------------------------------------------
# CATEGORY SELECTION
# --------------------------------------------------
categories = [
    c for c in doc.Settings.Categories
    if c.CategoryType.ToString() == "Model"
    and not c.IsTagCategory
]

cat_map = {c.Name: c for c in categories}

category_name = forms.SelectFromList.show(
    sorted(cat_map.keys()),
    title="Type Consistency Check",
    multiselect=False
)

if not category_name:
    forms.alert("No category selected.", exitscript=True)

category = cat_map[category_name]

# --------------------------------------------------
# TYPE NAME INPUT
# --------------------------------------------------
type_name = forms.ask_for_string(
    prompt="Enter expected Type Name",
    title="Type Consistency Check"
)

if not type_name:
    forms.alert("No type name provided.", exitscript=True)

# --------------------------------------------------
# ISOLATE OPTION
# --------------------------------------------------
isolate = forms.alert(
    "Isolate this type?\n\nYes = hide all other elements in this category",
    options=["Yes", "No"]
)

# --------------------------------------------------
# PARAMETER PROVIDER (Type Name)
# --------------------------------------------------
provider = ParameterValueProvider(
    ElementId(BuiltInParameter.SYMBOL_NAME_PARAM)
)

# --------------------------------------------------
# CATEGORY IDS (.NET COLLECTION)
# --------------------------------------------------
cat_ids = List[ElementId]()
cat_ids.Add(category.Id)

# --------------------------------------------------
# VIEW DUPLICATION
# --------------------------------------------------
with revit.Transaction("Duplicate QA View"):

    new_view_id = active_view.Duplicate(ViewDuplicateOption.Duplicate)
    qa_view = doc.GetElement(new_view_id)

    qa_view.Name = "{} – TYPE QA – {} – {}".format(
        active_view.Name,
        category.Name,
        type_name
    )

# Switch to QA view
uidoc.ActiveView = qa_view

# --------------------------------------------------
# UNIQUE FILTER NAMES
# --------------------------------------------------
show_filter_name = "TCC_SHOW_{}_{}".format(category.Name, type_name)
hide_filter_name = "TCC_HIDE_{}_{}".format(category.Name, type_name)

# --------------------------------------------------
# APPLY FILTERS IN QA VIEW
# --------------------------------------------------
with revit.Transaction("Apply Type Consistency Filters"):

    # Remove conflicting filters (global, safe)
    existing_filters = FilteredElementCollector(doc).OfClass(ParameterFilterElement)
    for f in existing_filters:
        if f.Name in [show_filter_name, hide_filter_name]:
            doc.Delete(f.Id)

    # ---------- SHOW FILTER ----------
    show_rule = FilterStringRule(
        provider,
        FilterStringEquals(),
        type_name
    )

    show_filter = ParameterFilterElement.Create(
        doc,
        show_filter_name,
        cat_ids
    )
    show_filter.SetElementFilter(
        ElementParameterFilter(show_rule)
    )

    qa_view.AddFilter(show_filter.Id)
    qa_view.SetFilterVisibility(show_filter.Id, True)

    # ---------- HIDE FILTER ----------
    if isolate == "Yes":
        hide_rule = FilterStringRule(
            provider,
            FilterStringEquals(),
            type_name
        )

        hide_filter = ParameterFilterElement.Create(
            doc,
            hide_filter_name,
            cat_ids
        )
        hide_filter.SetElementFilter(
            ElementParameterFilter(hide_rule, True)  # inverted
        )

        qa_view.AddFilter(hide_filter.Id)
        qa_view.SetFilterVisibility(hide_filter.Id, False)

# --------------------------------------------------
# DONE
# --------------------------------------------------
forms.alert(
    "Type Consistency Check complete.\n\n"
    "A QA view was created:\n\n{}\n\n"
    "Hidden elements indicate naming inconsistencies."
    .format(qa_view.Name)
)
