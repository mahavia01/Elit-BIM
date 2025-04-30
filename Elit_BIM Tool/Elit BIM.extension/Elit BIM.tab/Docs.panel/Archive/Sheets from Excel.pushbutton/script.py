# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.UI import TaskDialog
from pyrevit import revit, forms, script
import math

doc = revit.doc
uidoc = revit.uidoc

def get_clearance_ft():
    value = forms.ask_for_string(
        prompt="Enter clearance (in mm):",
        title="Builder's Work Opening"
    )
    if not value:
        forms.alert("Clearance not provided.")
        script.exit()
    try:
        return float(value) / 304.8  # mm to ft
    except:
        forms.alert("Invalid number format.")
        script.exit()

def get_element_selection(prompt_msg):
    forms.alert(prompt_msg)
    return [doc.GetElement(r) for r in uidoc.Selection.PickObjects(ObjectType.Element)]

def get_bbox_center(bbox):
    return XYZ(
        (bbox.Min.X + bbox.Max.X) / 2,
        (bbox.Min.Y + bbox.Max.Y) / 2,
        (bbox.Min.Z + bbox.Max.Z) / 2
    )

def create_opening_at(doc, host, center, width, height, depth):
    sketch_plane = SketchPlane.Create(doc, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, center))
    
    pt1 = XYZ(center.X - width/2, center.Y - height/2, center.Z)
    pt2 = XYZ(center.X + width/2, center.Y - height/2, center.Z)
    pt3 = XYZ(center.X + width/2, center.Y + height/2, center.Z)
    pt4 = XYZ(center.X - width/2, center.Y + height/2, center.Z)

    # Create profile loop
    line1 = Line.CreateBound(pt1, pt2)
    line2 = Line.CreateBound(pt2, pt3)
    line3 = Line.CreateBound(pt3, pt4)
    line4 = Line.CreateBound(pt4, pt1)

    profile = CurveArray()
    profile.Append(line1)
    profile.Append(line2)
    profile.Append(line3)
    profile.Append(line4)

    # Create void extrusion
    extrusion = doc.FamilyCreate.NewExtrusion(
        True,  # isSolid
        profile,
        sketch_plane,
        depth
    )
    extrusion.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).Set(center.Z - depth/2)

# Main logic
clearance_ft = get_clearance_ft()
mep_elements = get_element_selection("Select MEP elements (ducts/pipes)")
arch_elements = get_element_selection("Select walls/floors/structural elements")

t = Transaction(doc, "Create In-Place Builder's Work Openings")
t.Start()

for mep in mep_elements:
    mep_bb = mep.get_BoundingBox(doc.ActiveView)
    if not mep_bb:
        continue

    for arch in arch_elements:
        arch_bb = arch.get_BoundingBox(doc.ActiveView)
        if not arch_bb:
            continue

        # Clash Check
        if (mep_bb.Max.X < arch_bb.Min.X or mep_bb.Min.X > arch_bb.Max.X or
            mep_bb.Max.Y < arch_bb.Min.Y or mep_bb.Min.Y > arch_bb.Max.Y or
            mep_bb.Max.Z < arch_bb.Min.Z or mep_bb.Min.Z > arch_bb.Max.Z):
            continue

        center = get_bbox_center(mep_bb)

        # Try to get dimensions
        try:
            width_param = mep.LookupParameter("Width") or mep.LookupParameter("Diameter")
            height_param = mep.LookupParameter("Height") or mep.LookupParameter("Diameter")
            width = width_param.AsDouble() if width_param else 0.2
            height = height_param.AsDouble() if height_param else 0.2
        except:
            width = 0.2
            height = 0.2

        width += clearance_ft
        height += clearance_ft
        depth = 1.0  # 1 ft thick extrusion (can be adjusted)

        create_opening_at(doc, arch, center, width, height, depth)

t.Commit()
forms.alert("Builder's Work Openings created successfully.")
