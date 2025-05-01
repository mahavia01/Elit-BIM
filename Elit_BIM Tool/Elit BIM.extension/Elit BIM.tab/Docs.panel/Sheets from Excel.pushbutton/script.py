# -*- coding: utf-8 -*-
from pyrevit import revit, forms
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, ViewFamilyType, Transaction, ElementId, BuiltInCategory
import clr
clr.AddReference('Microsoft.Office.Interop.Excel')
import Microsoft.Office.Interop.Excel as Excel

doc = revit.doc
uidoc = revit.uidoc

if not doc:
    forms.alert("No Revit document is open. Please open a project first.", title="Error")
    script.exit()

# Ask user to select Excel file
excel_path = forms.pick_file(file_ext='xlsx', title='Select Excel File with Sheet Info')

if not excel_path:
    forms.alert("No file selected. Exiting.")
    script.exit()  # Exit the script if no file is selected

try:
    # Open Excel
    excel_app = Excel.ApplicationClass()
    workbook = excel_app.Workbooks.Open(excel_path)
    sheet = workbook.Sheets.Item[1]

    # Start reading data (assume headers in row 1, data starts at row 2)
    row = 2
    sheet_number_col = 1  # Column A
    sheet_name_col = 2    # Column B

    sheet_data = []

    while True:
        number = sheet.Cells(row, sheet_number_col).Value2
        name = sheet.Cells(row, sheet_name_col).Value2

        if number is None or name is None:
            break

        sheet_data.append((str(number), str(name)))
        row += 1

    # Close Excel
    workbook.Close(False)
    excel_app.Quit()

except Exception as e:
    forms.alert("Failed to read Excel file: {}".format(str(e)))
    script.exit()

# Create sheets in Revit
view_family_type = FilteredElementCollector(doc)\
    .OfClass(ViewFamilyType)\
    .ToElements()[0]  # Pick the first one (placeholder)

created_count = 0

t = Transaction(doc, "Create Sheets from Excel")
t.Start()
for number, name in sheet_data:
    try:
        new_sheet = ViewSheet.CreatePlaceholder(doc)
        new_sheet.SheetNumber = number
        new_sheet.Name = name
        created_count += 1
    except:
        continue
t.Commit()

forms.alert("Created {} sheets from Excel.".format(created_count), title="Success")
