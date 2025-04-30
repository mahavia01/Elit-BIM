# -*- coding: utf-8 -*-
import math
from pyrevit import forms

# Function to round value
def round_value(value, unit_system):
    if unit_system == "Inches":
        return round(value * 2) / 2.0  # nearest 0.5 inch
    elif unit_system == "Millimeters":
        return round(value / 5) * 5     # nearest 5 mm

# Unit selection
unit_choice = forms.SelectFromList.show(
    ["Inches", "Millimeters"],
    title="Select Unit System",
    multiselect=False
)

if not unit_choice:
    forms.alert("No units selected. Exiting.")
    exit()


# Flow Rate input (CFM)
flow_input = forms.ask_for_string(
    prompt="Enter Flow Rate (CFM):",
    title="Duct Sizer - Flow Input",
)

if not flow_input:
    forms.alert("No flow rate entered. Exiting.")
    exit()

# Friction loss input (inches of water gauge per 100 ft)
friction_input = forms.ask_for_string(
    prompt="Enter Friction Loss (in.wg / 100 ft):",
    title="Duct Sizer - Friction Loss Input",
    default="0.00"
)

if not friction_input:
    forms.alert("No friction loss entered. Exiting.")
    friction_input.exit()

# Process inputs
try:
    cfm = float(flow_input)
    friction = float(friction_input)
except:
    forms.alert("Invalid input. Please enter numeric values.")
    exit()

# Duct sizing formula based on ASHRAE / McQuay
equiv_diameter_in = 1.3 * ((cfm / (friction**0.5))**0.38)

# Convert to mm if needed
if unit_choice == "Millimeters":
    equiv_diameter_mm = equiv_diameter_in * 25.4
    rounded_diameter = round_value(equiv_diameter_mm, "Millimeters")
else:
    rounded_diameter = round_value(equiv_diameter_in, "Inches")

# Assuming equivalent rectangular duct with 2:1 ratio
if unit_choice == "Millimeters":
    height_mm = math.sqrt((equiv_diameter_mm ** 2) / 2)
    width_mm = 2 * height_mm
    height = round_value(height_mm, "Millimeters")
    width = round_value(width_mm, "Millimeters")
else:
    height_in = math.sqrt((equiv_diameter_in ** 2) / 2)
    width_in = 2 * height_in
    height = round_value(height_in, "Inches")
    width = round_value(width_in, "Inches")

# Result display (use .format instead of f-strings)
result = (
    "Duct Sizing\n\n"
    "Flow Rate: {0:.1f} CFM\n"
    "Friction Loss: {1:.3f} in.wg / 100ft\n"
    "Unit System: {2}\n\n"
    "Equivalent Round Diameter: {3} {4}\n"
    "Rectangular Duct Size (2:1): {5} x {6} {4}"
).format(
    cfm,
    friction,
    unit_choice,
    rounded_diameter,
    "mm" if unit_choice == "Millimeters" else "inches",
    width,
    height
)

forms.alert(result, title="Duct Sizing Completed")
