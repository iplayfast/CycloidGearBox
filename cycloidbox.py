#!/usr/bin/python

"""Hypocycloid gear boxgenerator
Code to create a hypocycloidal gear_box
https://en.wikipedia.org/wiki/Cycloidal_drive

Copyright 	2019, Chris Bruner
Version 	v0.1
License 	LGPL V2.1
Homepage

Credit to:
        Alex Lait http://www.zincland.com/hypocycloid/ 
        who credits the following:
	Formulas to describe a hypocycloid cam
	http://gears.ru/transmis/zaprogramata/2.0.139.pdf

	Insperational thread on CNCzone
	http://www.cnczone.com/forums/showthread.php?t=72.02.061

	Documenting and updating the sdxf library
	http://www.kellbot.com/sdxf-python-library-for-dxf/

	Formulas for calculating the pressure angle and finding the limit circles
	http://imtuoradea.ro/auo.fmte/files-2.07/MECATRONICA_files/Anamaria_Dascalescu_1.pdf

Notes:
	Does not currently do ANY checking for sane input values and it
	is possible to create un-machinable cams, use at your own risk

	Suggestions:
	- eccentricity should not be more than the roller radius
	- Has not been tested with negative values, may have interesting results :)

 style guide
def functions_are_lowercase(variables_as_well):

class ClassesArePascalCase:

SomeClass.some_variable
"""
from __future__ import division

import os, random
import FreeCADGui
import FreeCAD as App
import cycloidFun
# for animation
from PySide import QtCore
import math

smWBpath = os.path.dirname(cycloidFun.__file__)
smWB_icons_path = os.path.join(smWBpath, 'icons')
global mainIcon
mainIcon = os.path.join(smWB_icons_path, 'cycloidgearbox.svg')
global pinIcon
pinIcon = os.path.join(smWB_icons_path, 'cycloidpin.svg')
__dir__ = os.path.dirname(__file__)
global eccentricIcon
eccentricIcon = os.path.join(smWB_icons_path, 'eccentric.svg')
# iconPath = os.path.join( __dir__, 'Resources', 'icons' )
global animation_busy
animation_busy = False
keepToolbar = False
version = 0.01


def QT_TRANSLATE_NOOP(scope, text):
    return text


"""
todo:
    Driver Pin Height doesn't update
    Driver Disk Height should be Driver Disk Offset
    Driver Disk Height should refer to depth of driver disk
"""


class CycloidGearBoxCreateObject():
    """
    The part that holds the parameters used to make the phsyical parts
    """

    def GetResources(self):
        print(os.path.join('icons', 'cycloidgearbox.svg'))
        return {'Pixmap': mainIcon,
                'MenuText': "&Create hypoCycloidalGear",
                'ToolTip': "Create default gear_box"}

    def __init__(self):
        pass

    def Activated(self):
        print("cycloidbox Activated")
        if not App.ActiveDocument:
            App.newDocument()
        doc = App.ActiveDocument
        """# test code
        sketch = doc.Body.newObject('Sketcher::SketchObject','Sketch') 
        sketch.Support = (App.activeDocument().XY_Plane, [''])
        sketch.MapMode = 'FlatFace'
        """
        body = doc.addObject('PartDesign::Body', 'Body')
        body.Label = "gear_box"
        # FreeCADGui.ActiveDocument.ActiveView.setActiveObject("Body", body)
        # feature = App.ActiveDocument.addObject('PartDesign::AdditiveBox', 'Box')
        # obj.addObject(feature)
        # App.ActiveDocument.recompute()

        obj = doc.addObject("Part::FeaturePython", "GearBoxParameters")
        gear_box = CycloidalGearBox(obj)
        doc.recompute()
        obj.Proxy = gear_box
        random.seed(444)
        pindiskobj = doc.addObject("Part::FeaturePython", "pin_disk")
        obj.addProperty("App::PropertyString","IconFilename","","",8).IconFilename = pinIcon;
        #print(gear_box.GetHyperParameters())
        pin_disk = pindiskClass(pindiskobj, gear_box)
        pindiskobj.Proxy = pin_disk
        gear_box.recomputeList.append(pin_disk)
        ViewProviderCGBox(pindiskobj.ViewObject, pinIcon)
        pindiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        cycdiskobj = doc.addObject("Part::FeaturePython", "cycloidal_disk")
        cycdisk = cycdiskClass(cycdiskobj, gear_box)
        cycdiskobj.Proxy = cycdisk
        gear_box.recomputeList.append(cycdisk)
        ViewProviderCGBox(cycdiskobj.ViewObject, mainIcon)
        cycdiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        driver_diskobj = doc.addObject("Part::FeaturePython", "driver_disk")
        driver_disk = driver_diskClass(driver_diskobj, gear_box)
        driver_diskobj.Proxy = driver_disk
        gear_box.recomputeList.append(driver_disk)
        ViewProviderCGBox(driver_diskobj.ViewObject, pinIcon)
        driver_diskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        eccentric_shaft_obj = doc.addObject("Part::FeaturePython", "eccentric_shaft")
        escShaft = EccShaft(eccentric_shaft_obj, gear_box)
        eccentric_shaft_obj.Proxy = escShaft
        gear_box.recomputeList.append(escShaft)
        ViewProviderCGBox(eccentric_shaft_obj.ViewObject, eccentricIcon)
        eccentric_shaft_obj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        ekobj = doc.addObject("Part::FeaturePython", "eccentricKey")
        escKey = EccKey(ekobj, gear_box)
        ekobj.Proxy = escKey
        gear_box.recomputeList.append(escKey)
        ViewProviderCGBox(ekobj.ViewObject, eccentricIcon)
        ekobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        oShaftObj = doc.addObject("Part::FeaturePython", "output_shaft")
        oshaft = OutShaft(oShaftObj, gear_box)
        oshaft.Proxy = oshaft
        gear_box.recomputeList.append(oshaft)
        ViewProviderCGBox(oShaftObj.ViewObject, pinIcon)
        oShaftObj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        gear_box.busy = False
        gear_box.onChanged('', 'Refresh')
        gear_box.recompute()
        doc.recompute()
        gear_box.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
        # timer.start(timeout)
        return gear_box

    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        print("CycloidalGearBox.Deactivated()\n")

    def execute(self, obj):
        print('cycloidgearboxCreateObject execute')


class pindiskClass():
    def __init__(self, obj, cgb):
        self.Object = obj
        self.cgb = cgb
        obj.Proxy = self
        self.ShapeColor = (0.67, 0.68, 0.88)
        print("Adding parameters")
        param = App.ActiveDocument.getObject("GearBoxParameters")
        #print(param.roller_diameter)
        obj.addProperty("App::PropertyLength", "roller_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).roller_diameter = param.roller_diameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyInteger", "tooth_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).tooth_count = param.tooth_count
        obj.addProperty("App::PropertyLength", "base_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).base_height = param.base_height
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyBool", "pin_disk_scale", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "pin_disk_scale")).pin_disk_scale = param.pin_disk_scale
        obj.addProperty("App::PropertyLength","pin_disk_diameter","CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","pin_disk Diameter")).pin_disk_diameter = param.pin_disk_diameter
        self.Type = 'pin_disk'
        print("Done Adding parameters")

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        # App.ActiveDocument.getObject("GearBoxParameters").onChanged(fp,prop)
        pin_disk = fp.Document.getObject('pin_disk')
        gear_box = App.ActiveDocument.getObject("GearBoxParameters")
        if prop == 'Proxy':
            pass
        if prop == 'tooth_count':
            gear_box.tooth_count = pin_disk.tooth_count
        if prop == 'pin_disk_diameter':
            gear_box.pin_disk_diameter = pin_disk.pin_disk_diameter
        if prop == 'roller_diameter':
            gear_box.roller_diameter = pin_disk.roller_diameter
        # if prop=='RollerHeight':
        #    gear_box.RollerHeight = pin_disk.RollerHeight
        if prop == 'base_height':
            gear_box.base_height = pin_disk.base_height
        if prop == 'shaft_diameter':
            gear_box.shaft_diameter = pin_disk.shaft_diameter

    def recompute_gearbox(self, H):
        print("recomputing pin disk", H)
        self.Object.Shape = cycloidFun.generate_pin_base(H)
        # self.gear_box.gear_box.generate_pin_base()


class driver_diskClass():
    def __init__(self, obj, gear_box):
        self.Object = obj
        obj.Proxy = self
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).disk_hole_count = param.disk_hole_count
        obj.addProperty("App::PropertyLength", "driver_disk_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Cycloidal Disk Height")).driver_disk_height = param.cycloidal_disk_height
        obj.addProperty("App::PropertyLength", "driver_pin_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Driver Pin Height")).driver_pin_height = param.driver_pin_height
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = param.eccentricity
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        self.Type = 'driver_disk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("Driver Disk onchanged", fp, prop)
        gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
        dd = fp.Document.getObject('driver_disk')
        if prop == 'disk_hole_count':
            gear_box_parameters.disk_hole_count = dd.disk_hole_count
        if prop == 'driver_disk_height':
            gear_box_parameters.driver_disk_height = dd.driver_disk_height
        if prop == 'driver_pin_height':
            gear_box_parameters.driver_pin_height = dd.driver_pin_height
        if prop == 'eccentricity':
            gear_box_parameters.eccentricity = dd.eccentricity
        if prop == 'shaft_diameter':
            gear_box_parameters.shaft_diameter = dd.shaft_diameter

    def execute(selfself, obj):
        print('driver_disk execute', obj)

    def recompute_gearbox(self, H):
        print('recomputing driver_disk')
        self.Object.Shape = cycloidFun.generate_driver_disk(H)


class cycdiskClass():
    def __init__(self, obj, gear_box):
        self.Object = obj
        obj.Proxy = self
        # obj.addProperty("App::PropertyString", "Parent","Parameter","Parent").Parent = App.ActiveDocument.GearBoxParameters
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).disk_hole_count = param.disk_hole_count
        obj.addProperty("App::PropertyInteger", "tooth_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).tooth_count = param.tooth_count
        obj.addProperty("App::PropertyLength", "cycloidal_disk_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "Cycloidal Disk Height")).cycloidal_disk_height = param.cycloidal_disk_height
        self.gear_box = gear_box
        self.ShapeColor = (0.12, 0.02, 0.63)
        self.Type = 'CyclockalDisk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("cycloiddisk onchanged", fp, prop)
        p = App.ActiveDocument.getObject("GearBoxParameters")
        s = fp.Document.getObject('cycloidal_disk')
        if prop == 'disk_hole_count':
            p.disk_hole_count = s.disk_hole_count
        if prop == 'cycloidal_disk_height':
            p.cycloidal_disk_height = s.cycloidal_disk_height
        if prop == 'tooth_count':
            p.tooth_count = s.tooth_count

    def execute(self, obj):
        # obj.Shape = self.gear_box.generate_pin_base()
        print('cycloidgearbox execute', obj)

    def recompute_gearbox(self, H):
        print("recomputing cycloidal disk")
        self.Object.Shape = cycloidFun.generate_cycloidal_disk(H)


class EccShaft():
    def __init__(self, obj, gear_box):
        self.Object = obj
        self.gear_box = gear_box
        obj.Proxy = self
        self.Type = 'EccShaft'
        self.ShapeColor = (0.42, 0.42, 0.63)
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = param.eccentricity
        obj.addProperty("App::PropertyLength", "roller_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).roller_diameter = param.roller_diameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyLength", "base_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).base_height = param.base_height
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyLength", "slot_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Slot Height")).slot_height = param.slot_height

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
        eccentric_shaft_obj = fp.Document.getObject("eccentric_shaft")
        if prop == "eccentricity":
            gear_box_parameters.eccentricity = eccentric_shaft_obj.eccentricity
            gear_box_parameters.roller_diameter = eccentric_shaft_obj.eccentricity * 2.0
        if prop == 'roller_diameter':
            gear_box_parameters.roller_diameter = eccentric_shaft_obj.roller_diameter
        # if prop == 'RollerHeight':
        #    gear_box_parameters.RollerHeight = eccentric_shaft_obj.RollerHeight
        if prop == 'base_height':
            gear_box_parameters.base_height = eccentric_shaft_obj.base_height
        if prop == 'shaft_diameter':
            gear_box_parameters.shaft_diameter = eccentric_shaft_obj.shaft_diameter
        if prop == 'slot_height':
            gear_box_parameters.slot_height = eccentric_shaft_obj.slot_height

    def recompute_gearbox(self, H):
        print("recomputing Eccentric Shaft")
        self.Object.Shape = cycloidFun.generate_eccentric_shaft(H)


class EccKey():
    def __init__(self, obj, gear_box):
        self.Object = obj
        self.gear_box = gear_box
        obj.Proxy = self
        self.Type = 'EccKey'
        self.ShapeColor = (0.62, 0.42, 0.63)
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = param.eccentricity
        obj.addProperty("App::PropertyLength", "roller_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).roller_diameter = param.roller_diameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyLength", "base_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).base_height = param.base_height
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
        eccentric_key = fp.Document.getObject("eccentricKey")
        if prop == "eccentricity":
            gear_box_parameters.eccentricity = eccentric_key.eccentricity
            gear_box_parameters.roller_diameter = eccentric_key.eccentricity * 2.0
        if prop == 'roller_diameter':
            gear_box_parameters.roller_diameter = eccentric_key.roller_diameter
        # if prop == 'RollerHeight':
        #    gear_box_parameters.RollerHeight = eccentric_key.RollerHeight
        if prop == 'base_height':
            gear_box_parameters.base_height = eccentric_key.base_height
        if prop == 'shaft_diameter':
            gear_box_parameters.shaft_diameter = eccentric_key.shaft_diameter

    def recompute_gearbox(self, H):
        self.Object.Shape = cycloidFun.generate_eccentric_key(H)


class OutShaft():
    def __init__(self, obj, gear_box):
        self.Object = obj
        self.gear_box = gear_box
        obj.Proxy = self
        self.Type = 'Output Shaft'
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).disk_hole_count = param.disk_hole_count
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyLength", "slot_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Slot Height")).slot_height = param.slot_height
        self.Type = 'output_shaft'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
        output_shaft = fp.Document.getObject("output_shaft")
        if prop == "disk_hole_count":
            gear_box_parameters.disk_hole_count = output_shaft.disk_hole_count
        if prop == 'shaft_diameter':
            gear_box_parameters.shaft_diameter = output_shaft.shaft_diameter
        if prop == 'slot_height':
            gear_box_parameters.slot_height = output_shaft.slot_height

    def recompute_gearbox(self, H):
        print("recomputing output shaft")
        self.Object.Shape = cycloidFun.generate_output_shaft(H)
        print("done recomputing output shaft")


class CycloidalGearBox():
    def __init__(self, obj):
        print("CycloidalGearBox __init__")
        self.busy = True
        H = cycloidFun.generate_default_hyperparam()
        obj.addProperty("App::PropertyFloat", "Version", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "The version of CycloidGearBox Workbench used to create this object")).Version = version
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = H["eccentricity"]
        obj.addProperty("App::PropertyInteger", "tooth_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).tooth_count = H["tooth_count"]
        obj.addProperty("App::PropertyBool", "pin_disk_scale", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "pin_disk_scale")).pin_disk_scale = H["pin_disk_scale"]
        obj.addProperty("App::PropertyLength","pin_disk_diameter",
                        QT_TRANSLATE_NOOP("App::Property","pin_disk Diameter")).pin_disk_diameter = H["pin_disk_diameter"]
        obj.addProperty("App::PropertyInteger", "disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).disk_hole_count = H["disk_hole_count"]
        obj.addProperty("App::PropertyInteger", "line_segment_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of line segments to make up the cycloidal disk")).line_segment_count = H["line_segment_count"]
        obj.addProperty("App::PropertyAngle", "tooth_pitch", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Tooth Pitch")).tooth_pitch = H["tooth_pitch"]

        obj.addProperty("App::PropertyLength", "roller_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).roller_diameter = H["roller_diameter"]

        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = H["RollerHeight"]
        obj.addProperty("App::PropertyLength", "center_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Center Diameter")).center_diameter = H["center_diameter"]
        obj.addProperty("App::PropertyLength", "pressure_angle_limit", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Limit")).pressure_angle_limit = H["pressure_angle_limit"]
        obj.addProperty("App::PropertyAngle", "pressure_angle_offset", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Offset")).pressure_angle_offset = H["pressure_angle_offset"]
        obj.addProperty("App::PropertyLength", "base_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).base_height = H["base_height"]
        obj.addProperty("App::PropertyLength", "driver_pin_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Driver Pin Height")).driver_pin_height = H["driver_pin_height"]
        obj.addProperty("App::PropertyLength", "driver_disk_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).driver_disk_height = H["driver_disk_height"]
        obj.addProperty("App::PropertyLength", "cycloidal_disk_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Cycloidal Disk Height")).cycloidal_disk_height = H["cycloidal_disk_height"]
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = H["shaft_diameter"]
        obj.addProperty("App::PropertyLength", "slot_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Slot Height")).slot_height = H["slot_height"]
        obj.addProperty("App::PropertyLength", "clearance", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "clearance between parts")).clearance = H["clearance"]
        obj.addProperty("App::PropertyBool", "animate", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "animate")).animate = False
        # obj.Proxy = self
        self.recomputeList = []
        print("Properties added")
        self.Object = obj
        self.Type = 'CycloidalGearBox'
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))

        print('gear_box created')

    def parameterization(self, pts, a, closed):
        print("parameterization")
        return 0

    def makePoints(selfself, obj):
        print("makepoints")
        return []

    def Activated(self):
        print("Cycloidal.Activated()\n")

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        global animation_busy
        if animation_busy:
            return
        print("GearBox_Paramenter onchanged", fp, prop)
        if hasattr(self, "busy"):
            if self.busy:
                return
        dirty = False
        obj = App.ActiveDocument.getObject("GearBoxParameters")
        pin_disk = App.ActiveDocument.getObject('pin_disk')
        eccentric_shaft_obj = App.ActiveDocument.getObject('eccentricShaft')
        dd = App.ActiveDocument.getObject('driver_disk')
        output_shaft = App.ActiveDocument.getObject('output_shaft')
        if prop == 'animate':
            if hasattr(obj, "animate"):
                obj.animate = not obj.animate
                if obj.animate:
                    timer.start(timeout)
                else:
                    timer.stop()
        if prop == 'scale':
            if (pin_disk.scale != obj.scale):
                pin_disk.scale = obj.scale
                dirty = True
        if prop == 'slot_height':
            if (eccentric_shaft_obj.slot_height != obj.slot_height):
                eccentric_shaft_obj.slot_height = obj.slot_height
                dirty = True
            if (output_shaft.slot_height != obj.slot_height):
                output_shaft.slot_height = obj.slot_height
                dirty = True
        if prop == 'pin_disk_diameter':
            if (pin_disk.pin_disk_diameter!=obj.pin_disk_diameter):
                pin_disk.pin_disk_diameter = obj.pin_disk_diameter
                dirty = True
        if prop == 'shaft_diameter':
            if obj.shaft_diameter < 1:
                obj.shaft_diameter = 1
            if eccentric_shaft_obj.shaft_diameter != obj.shaft_diameter:
                eccentric_shaft_obj.shaft_diameter = obj.shaft_diameter
                pin_disk.shaft_diameter = obj.shaft_diameter
                dd.shaft_diameter = obj.shaft_diameter
            dirty = True
        if prop == 'roller_diameter' and hasattr(eccentric_shaft_obj, "eccentricity") and hasattr(obj, "eccentricity"):
            if (obj.eccentricity < 1):
                obj.eccentricity = 1
            if eccentric_shaft_obj.eccentricity != obj.eccentricity:
                eccentric_shaft_obj.eccentricity = obj.eccentricity
            dirty = True
        if prop == 'tooth_count':
            if obj.tooth_count < 3:
                obj.tooth_count = 3
            if pin_disk.tooth_count != obj.tooth_count:
                pin_disk.tooth_count = obj.tooth_count
            dirty = True
        if prop == 'line_segment_count':
            dirty = True
        if prop == 'roller_diameter':
            if hasattr(obj, "eccentricity"):
                if obj.roller_diameter < 1:
                    obj.roller_diameter = 1
                if obj.eccentricity != obj.roller_diameter / 2:
                    obj.eccentricity = obj.roller_diameter / 2
                if hasattr(eccentric_shaft_obj, "eccentricity") and eccentric_shaft_obj.eccentricity != obj.eccentricity:
                    eccentric_shaft_obj.eccentricity = obj.eccentricity
            if pin_disk.roller_diameter != obj.roller_diameter:
                pin_disk.roller_diameter = obj.roller_diameter
            dirty = True
        # if prop=='RollerHeight':
        #    if pin_disk.RollerHeight != obj.RollerHeight:
        #        pin_disk.RollerHeight = obj.RollerHeight
        #    dirty = True
        if prop == 'tooth_pitch':
            if pin_disk.tooth_count != obj.tooth_count:
                pin_disk.tooth_count = obj.tooth_count
            dirty = True
        if prop == 'eccentricity':
            if (obj.roller_diameter < obj.eccentricity * 2):
                obj.roller_diameter = obj.eccentricity * 2
            if hasattr(eccentric_shaft_obj, "eccentricity") and eccentric_shaft_obj.eccentricity != obj.eccentricity:
                eccentric_shaft_obj.eccentricity = obj.eccentricity
            dirty = True
        if prop == 'center_diameter':
            dirty = True
        if prop == 'pressure_angle_limit':
            dirty = True
        if prop == 'pressure_angle_offset':
            dirty = True
        if prop == 'base_height':
            if pin_disk.base_height != obj.base_height:
                pin_disk.base_height = obj.base_height
            dirty = True
        if prop == 'driver_disk_height':
            dirty = True
        if prop == 'cycloidal_disk_height':
            dirty = True
        if prop == 'disk_hole_count':
            dirty = True
        if prop == 'Refresh':
            dirty = True
        if prop == 'clearance':
            diry = True
        if dirty:
            print("recomputing")
            self.recompute()

    def GetHyperParameters(self):
        hyperparameters = {"tooth_count": int(self.Object.__getattribute__("tooth_count")),
                           "line_segment_count": int(self.Object.__getattribute__("line_segment_count")),
                           "roller_diameter": float(self.Object.__getattribute__("roller_diameter").Value),
                           "pin_disk_diameter": float(self.Object.__getattribute__("pin_disk_diameter").Value),
                           "pin_disk_scale": bool(self.Object.__getattribute__("pin_disk_scale")),
                           "tooth_pitch": float(self.Object.__getattribute__("tooth_pitch").Value),
                           "eccentricity": float(self.Object.__getattribute__("eccentricity").Value),
                           "center_diameter": float(self.Object.__getattribute__("center_diameter").Value),
                           "pressure_angle_limit": float(self.Object.__getattribute__("pressure_angle_limit").Value),
                           "pressure_angle_offset": float(self.Object.__getattribute__("pressure_angle_offset").Value),
                           "base_height": float(self.Object.__getattribute__("base_height").Value),
                           "driver_pin_height": float(self.Object.__getattribute__("driver_pin_height").Value),
                           "driver_disk_height": float(self.Object.__getattribute__("driver_disk_height").Value),
                           "cycloidal_disk_height": float(self.Object.__getattribute__("cycloidal_disk_height").Value),
                           "disk_hole_count": int(self.Object.__getattribute__("disk_hole_count")),
                           "slot_height": int(self.Object.__getattribute__("slot_height")),
                           "shaft_diameter": float(self.Object.__getattribute__("shaft_diameter")),
                           "clearance": float(self.Object.__getattribute__("clearance"))
                           }
        return hyperparameters

    def recompute(self):
        print("Recomputing all")
        hyperparameters = self.GetHyperParameters()
        for a in self.recomputeList:
            print(".")
            a.recompute_gearbox(hyperparameters)

    def execute(self, obj):
        # obj.Shape = self.gear_box.generate_pin_base()
        print('cycloidgearbox execute', obj)


class ViewProviderCGBox:
    def __init__(self, obj,iconfile):
        """
       Set this object to the proxy object of the actual view provider
       """
        obj.Proxy = self
        self.part = obj

    def attach(self, obj):
        """
       Setup the scene sub-graph of the view provider, this method is mandatory
       """
        return

    def updateData(self, fp, prop):
        """
       If a property of the handled feature has changed we have the chance to handle this here
       """
        print("viewProviderCGBox updateData", fp, prop)
        """
       if prop.name=='eccentricShaft':
           pos = prop.Placement.Base
           global kwAngle
           rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,1),kwAngle)
           c = FreeCAD.Vector(0,0,0)
           prop.Placement = FreeCAD.Placement(pos,rot,c)
       """
        return

    def getDisplayModes(self, obj):
        """
       Return a list of display modes.
       """
        modes = []
        modes.append("Shaded")
        modes.append("Wireframe")
        return modes

    def getDefaultDisplayMode(self):
        """
       Return the name of the default display mode. It must be defined in getDisplayModes.
       """
        return "Shaded"

    def setDisplayMode(self, mode):
        """
       Map the display mode defined in attach with those defined in getDisplayModes.
       Since they have the same names nothing needs to be done.
       This method is optional.
       """
        #print("viewProviderCGBox setDisplayMode", mode)
        return mode

    def onChanged(self, vobj, prop):
        """
       Print the name of the property that has changed
       """

    #def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """
        #return self.icon
        # return main_CGB_Icon

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


step = 1.0
end = 360
timeout = 10
kwStartAngle = 0
kwAngle = 0

timer = QtCore.QTimer()


def rotate_point(cx, cy, a, v):
    s = math.sin(a)
    c = math.cos(a)
    # translate back to origin
    v = v - App.Vector(cx, cy, 0)
    x = float(v[0])
    y = float(v[1])
    return App.Vector(x * c - y * s + cx, x * s + y * c + cy, 0)


def turn_ES(a):
    global animation_busy
    if (animation_busy):
        return
    else:
        animation_busy = True
    constraintNr = 4
    # save global value in case this function is called from the console
    eccentric_shaft_obj = App.ActiveDocument.getObject('eccentricShaft')
    gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
    # print("Turning ",a)
    rot = App.Rotation(App.Vector(0, 0, 1), a)
    es_out = rotate_point(eccentric_shaft_obj.eccentricity,0,a,App.Vector(0,0,0))
    pos = eccentric_shaft_obj.Placement.Base
    NewPlace = App.Placement(pos, rot)
    eccentric_shaft_obj.Placement = NewPlace
    cd = App.ActiveDocument.getObject('cycloidal_disk')
    cdpos = es_out
    #cd.Placement.Base
    cdrot = App.Rotation(App.Vector(0, 0, 1), -a)
    cd.Placement = App.Placement(cdpos, cdrot)

    animation_busy = False
    #  App.ActiveDocument.Sketch.setDatum(constraintNr,App.Units.Quantity(str(-kwAngle)+'  deg'))
    App.ActiveDocument.recompute()

def update():
    global kwAngle
    # print(kwAngle)
    if kwAngle >= end:
        kwAngle -= 360
        if kwAngle < kwStartAngle:
            kwAngle = kwStartAngle
        #    timer.stop()
    else:
        kwAngle += step
    turn_ES(kwAngle)


#    genframe() # Bild erzeugen
timer.timeout.connect(update)
# timer.start(timeout)


FreeCADGui.addCommand('CycloidGearBoxCreateObject', CycloidGearBoxCreateObject())
