# -*- coding: utf-8 -*-
import math
from pyrevit import forms

# Function to round pipe size
def round_pipe_size(diameter, unit_system):
    # For simplicity, round to nearest 5mm or nearest 0.5 inch
    if unit_system == "Millimeters":
        return round(diameter / 5.0) * 5
    elif unit_system == "Inches":
        return round(diameter * 2) / 2.0

# Ask unit system
unit_choice = forms.SelectFromList.show(
    ["Inches", "Millimeters"],
    title="Select Unit System",
    multiselect=False
)

if not unit_choice:
    forms.alert("No units selected. Exiting.")
    exit()

# Ask flow rate input
flowrate_input = forms.ask_for_string(
    prompt="Enter Flow Rate (GPM):",
    title="Pipe Sizer - Flow Rate Input",
)

if not flowrate_input:
    forms.alert("No flow rate provided. Exiting.")
    exit()

# Ask design velocity
velocity_input = forms.ask_for_string(
    prompt="Enter Design Velocity (ft/sec):",
    title="Pipe Sizer - Velocity Input",
    default="6.0"
)

if not velocity_input:
    forms.alert("No velocity provided. Exiting.")
    exit()

# Ask optional cooling load (not required, just like zone area in duct sizer)
cooling_load_input = forms.ask_for_string(
    prompt="Enter Cooling Load (Optional, Tons):",
    title="Pipe Sizer - Cooling Load Input",
    default=""
)

# Process inputs
try:
    flow_gpm = float(flowrate_input)
    design_velocity_fps = float(velocity_input)
    if cooling_load_input:
        cooling_load_tons = float(cooling_load_input)
    else:
        cooling_load_tons = None
except:
    forms.alert("Invalid input. Please enter numeric values.")
    exit()

# Formula for pipe internal diameter
# Q = A * V
# A = Q / V
# A = area in square feet
# Flow (Q) in GPM --> Convert to CFS (cubic feet per second)
# 1 CFS = 448.831 GPM
flow_cfs = flow_gpm / 448.831
area_sqft = flow_cfs / design_velocity_fps

# Diameter = sqrt(4 * A / pi)
diameter_ft = math.sqrt(4 * area_sqft / math.pi)

# Convert diameter to inches
diameter_inch = diameter_ft * 12.0

# If millimeters, convert
if unit_choice == "Millimeters":
    diameter_mm = diameter_inch * 25.4
    rounded_diameter = round_pipe_size(diameter_mm, "Millimeters")
else:
    rounded_diameter = round_pipe_size(diameter_inch, "Inches")

# Show Result
result_message = (
    "Chilled Water Pipe Sizing Result:\n\n"
    "Flow Rate Provided: {0:.1f} GPM\n"
    "Design Velocity: {1:.1f} ft/sec\n"
    "Selected Units: {2}\n\n"
).format(
    flow_gpm,
    design_velocity_fps,
    unit_choice
)

if cooling_load_tons:
    result_message += "Cooling Load Provided: {0:.2f} Tons\n\n".format(cooling_load_tons)

result_message += (
    "Calculated Pipe Size (Internal Diameter): {0} {1}\n"
).format(
    rounded_diameter,
    "mm" if unit_choice == "Millimeters" else "inches"
)

forms.alert(result_message, title="Pipe Sizing Completed")
