# -*- coding: utf-8 -*-
from pyrevit import revit, forms
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter
from System.Collections.Generic import List

doc = revit.doc
uidoc = revit.uidoc

# Get all model categories (not tags/imports)
all_categories = sorted(
    [cat.Name for cat in doc.Settings.Categories 
     if cat.CategoryType == CategoryType.Model and not cat.IsTagCategory and cat.AllowsBoundParameters]
)

# Let user pick one category
selected_category_name = forms.SelectFromList.show(
    all_categories,
    title="Select a Category to Allow in Selection",
    button_name="Continue",
    multiselect=False
)

if not selected_category_name:
    forms.alert("No category selected. Script cancelled.", title="Cancelled")
    script.exit()

# Create a custom selection filter
class CategorySelectionFilter(ISelectionFilter):
    def __init__(self, category_name):
        self.category_name = category_name

    def AllowElement(self, element):
        return element.Category and element.Category.Name == self.category_name

    def AllowReference(self, reference, position):
        return True

# Ask user to select elements, but only allow selected category
try:
    picked_refs = uidoc.Selection.PickObjects(
        ObjectType.Element,
        CategorySelectionFilter(selected_category_name),
        "Select only elements of category: {}".format(selected_category_name)
    )

    selected_ids = List[ElementId]([ref.ElementId for ref in picked_refs])
    uidoc.Selection.SetElementIds(selected_ids)

    forms.alert("Selected {} element(s) from category '{}'.".format(len(selected_ids), selected_category_name), title="Done")

except:
    forms.alert("Selection cancelled or no elements selected.", title="Cancelled")
    script.exit()
