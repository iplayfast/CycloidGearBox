#!/usr/bin/python

"""Hypocycloid gear boxgenerator
Code to create a hypocycloidal gearbox
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
	- Eccentricity should not be more than the roller radius
	- Has not been tested with negative values, may have interesting results :)
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
global main_Icon
main_Icon = os.path.join(smWB_icons_path, 'cycloidgearbox.svg')
global pin_Icon
pin_Icon = os.path.join(smWB_icons_path, 'cycloidpin.svg')
__dir__ = os.path.dirname(__file__)
global eccentric_Icon
eccentric_Icon = os.path.join(smWB_icons_path, 'eccentric.svg')
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
        return {'Pixmap': main_Icon,
                'MenuText': "&Create hypoCycloidalGear",
                'ToolTip': "Create default gearbox"}

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
        body.Label = "GearBox"
        # FreeCADGui.ActiveDocument.ActiveView.setActiveObject("Body", body)
        # feature = App.ActiveDocument.addObject('PartDesign::AdditiveBox', 'Box')
        # obj.addObject(feature)
        # App.ActiveDocument.recompute()

        obj = doc.addObject("Part::FeaturePython", "GearBox Parameters")
        gearbox = CycloidalGearBox(obj)
        doc.recompute()
        obj.Proxy = gearbox
        random.seed(444)
        pindiskobj = doc.addObject("Part::FeaturePython", "pinDisk")
        obj.addProperty("App::PropertyString","IconFilename","","",8).IconFilename = pin_Icon;
        pindisk = pindiskClass(pindiskobj, gearbox)
        pindiskobj.Proxy = pindisk
        gearbox.recomputeList.append(pindisk)
        ViewProviderCGBox(pindiskobj.ViewObject, pin_Icon)
        pindiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        cycdiskobj = doc.addObject("Part::FeaturePython", "CycloidalDisk")
        cycdisk = cycdiskClass(cycdiskobj, gearbox)
        cycdiskobj.Proxy = cycdisk
        gearbox.recomputeList.append(cycdisk)
        ViewProviderCGBox(cycdiskobj.ViewObject, main_Icon)
        cycdiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        driverDiskobj = doc.addObject("Part::FeaturePython", "DriverDisk")
        driverDisk = driverDiskClass(driverDiskobj, gearbox)
        driverDiskobj.Proxy = driverDisk
        gearbox.recomputeList.append(driverDisk)
        ViewProviderCGBox(driverDiskobj.ViewObject, pin_Icon)
        driverDiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        esobj = doc.addObject("Part::FeaturePython", "EccentricShaft")
        escShaft = EccShaft(esobj, gearbox)
        esobj.Proxy = escShaft
        gearbox.recomputeList.append(escShaft)
        ViewProviderCGBox(esobj.ViewObject, eccentric_Icon)
        esobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        ekobj = doc.addObject("Part::FeaturePython", "EccentricKey")
        escKey = EccKey(ekobj, gearbox)
        ekobj.Proxy = escKey
        gearbox.recomputeList.append(escKey)
        ViewProviderCGBox(ekobj.ViewObject, eccentric_Icon)
        ekobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        oShaftObj = doc.addObject("Part::FeaturePython", "OutputShaft")
        oshaft = OutShaft(oShaftObj, gearbox)
        oshaft.Proxy = oshaft
        gearbox.recomputeList.append(oshaft)
        ViewProviderCGBox(oShaftObj.ViewObject, pin_Icon)
        oShaftObj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        gearbox.busy = False
        gearbox.onChanged('', 'Refresh')
        gearbox.recompute()
        doc.recompute()
        gearbox.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
        # timer.start(timeout)
        return gearbox

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
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property",
                                                                                                     "Diameter of the rollers")).RollerDiameter = param.RollerDiameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property",
                                                                                                  "Number of teeth of the cycloidal disk")).ToothCount = param.ToothCount
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).BaseHeight = param.BaseHeight
        obj.addProperty("App::PropertyLength", "ShaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).ShaftDiameter = param.ShaftDiameter
        obj.addProperty("App::PropertyLength","PinDiskDiameter","CycloidGearBox",QT_TRANSLATE_NOOP("App::Property","PinDisk Diameter")).PinDiskDiameter = param.PinDiskDiameter
        self.Type = 'pinDisk'
        print("Done Adding parameters")

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        # App.ActiveDocument.getObject("GearBox_Parameters").onChanged(fp,prop)
        pindisk = fp.Document.getObject('pinDisk')
        gearbox = App.ActiveDocument.getObject("GearBox_Parameters")
        if prop == 'Proxy':
            pass
        if prop == 'ToothCount':
            gearbox.ToothCount = pindisk.ToothCount
        if prop == 'PinDiskDiameter':
            gearbox.PinDiskDiameter = pindisk.PinDiskDiameter
        if prop == 'RollerDiameter':
            gearbox.RollerDiameter = pindisk.RollerDiameter
        # if prop=='RollerHeight':
        #    gearbox.RollerHeight = pindisk.RollerHeight
        if prop == 'BaseHeight':
            gearbox.BaseHeight = pindisk.BaseHeight
        if prop == 'ShaftDiameter':
            gearbox.ShaftDiameter = pindisk.ShaftDiameter

    def recomputeGB(self, H):
        print("recomputing pin disk", H)
        self.Object.Shape = cycloidFun.generatePinBase(H)
        # self.GearBox.gearBox.generatePinBase()


class driverDiskClass():
    def __init__(self, obj, gearbox):
        self.Object = obj
        obj.Proxy = self
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyInteger", "DiskHoleCount", "CycloidGearBox", QT_TRANSLATE_NOOP("APP::Property",
                                                                                                     "Number of driving holes of the cycloid disk")).DiskHoleCount = param.DiskHoleCount
        obj.addProperty("App::PropertyLength", "DriverDiskHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property",
                                                                                                       "Cycloidal Disk Height")).DriverDiskHeight = param.CycloidalDiskHeight
        obj.addProperty("App::PropertyLength", "DriverPinHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Driver Pin Height")).DriverPinHeight = param.DriverPinHeight
        obj.addProperty("App::PropertyLength", "Eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Eccentricity")).Eccentricity = param.Eccentricity
        obj.addProperty("App::PropertyLength", "ShaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).ShaftDiameter = param.ShaftDiameter
        self.Type = 'DriverDisk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("Driver Disk onchanged", fp, prop)
        gbp = App.ActiveDocument.getObject("GearBox_Parameters")
        dd = fp.Document.getObject('DriverDisk')
        if prop == 'DiskHoleCount':
            gbp.DiskHoleCount = dd.DiskHoleCount
        if prop == 'DriverDiskHeight':
            gbp.DriverDiskHeight = dd.DriverDiskHeight
        if prop == 'DriverPinHeight':
            gbp.DriverPinHeight = dd.DriverPinHeight
        if prop == 'Eccentricity':
            gbp.Eccentricity = dd.Eccentricity
        if prop == 'ShaftDiameter':
            gbp.ShaftDiameter = dd.ShaftDiameter

    def execute(selfself, obj):
        print('DriverDisk execute', obj)

    def recomputeGB(self, H):
        print('recomputing DriverDisk')
        self.Object.Shape = cycloidFun.generateDriverDisk(H)


class cycdiskClass():
    def __init__(self, obj, gearbox):
        self.Object = obj
        obj.Proxy = self
        # obj.addProperty("App::PropertyString", "Parent","Parameter","Parent").Parent = App.ActiveDocument.GearBox_Parameters
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyInteger", "DiskHoleCount", "CycloidGearBox", QT_TRANSLATE_NOOP("APP::Property",
                                                                                                     "Number of driving holes of the cycloid disk")).DiskHoleCount = param.DiskHoleCount
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).ToothCount = param.ToothCount
        obj.addProperty("App::PropertyLength", "CycloidalDiskHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "Cycloidal Disk Height")).CycloidalDiskHeight = param.CycloidalDiskHeight
        self.GearBox = gearbox
        self.ShapeColor = (0.12, 0.02, 0.63)
        self.Type = 'CyclockalDisk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("cycloiddisk onchanged", fp, prop)
        p = App.ActiveDocument.getObject("GearBox_Parameters")
        s = fp.Document.getObject('CycloidalDisk')
        if prop == 'DiskHoleCount':
            p.DiskHoleCount = s.DiskHoleCount
        if prop == 'CycloidalDiskHeight':
            p.CycloidalDiskHeight = s.CycloidalDiskHeight
        if prop == 'ToothCount':
            p.ToothCount = s.ToothCount

    def execute(self, obj):
        # obj.Shape = self.gearBox.generatePinBase()
        print('cycloidgearbox execute', obj)

    def recomputeGB(self, H):
        print("recomputing cycloidal disk")
        self.Object.Shape = cycloidFun.generateCycloidalDisk(H)


class EccShaft():
    def __init__(self, obj, gearbox):
        self.Object = obj
        self.gearbox = gearbox
        obj.Proxy = self
        self.Type = 'EccShaft'
        self.ShapeColor = (0.42, 0.42, 0.63)
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyLength", "Eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Eccentricity")).Eccentricity = param.Eccentricity
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property",
                                                                                                     "Diameter of the rollers")).RollerDiameter = param.RollerDiameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).BaseHeight = param.BaseHeight
        obj.addProperty("App::PropertyLength", "ShaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).ShaftDiameter = param.ShaftDiameter

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gbp = App.ActiveDocument.getObject("GearBox_Parameters")
        es = fp.Document.getObject("EccentricShaft")
        if prop == "Eccentricity":
            gbp.Eccentricity = es.Eccentricity
            gbp.RollerDiameter = es.Eccentricity * 2.0
        if prop == 'RollerDiameter':
            gbp.RollerDiameter = es.RollerDiameter
        # if prop == 'RollerHeight':
        #    gbp.RollerHeight = es.RollerHeight
        if prop == 'BaseHeight':
            gbp.BaseHeight = es.BaseHeight
        if prop == 'ShaftDiameter':
            gbp.ShaftDiameter = es.ShaftDiameter

    def recomputeGB(self, H):
        print("recomputing Eccentric Shaft")
        self.Object.Shape = cycloidFun.generateEccentricShaft(H)


class EccKey():
    def __init__(self, obj, gearbox):
        self.Object = obj
        self.gearbox = gearbox
        obj.Proxy = self
        self.Type = 'EccKey'
        self.ShapeColor = (0.62, 0.42, 0.63)
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyLength", "Eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Eccentricity")).Eccentricity = param.Eccentricity
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property",
                                                                                                     "Diameter of the rollers")).RollerDiameter = param.RollerDiameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).BaseHeight = param.BaseHeight
        obj.addProperty("App::PropertyLength", "ShaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).ShaftDiameter = param.ShaftDiameter

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gbp = App.ActiveDocument.getObject("GearBox_Parameters")
        ek = fp.Document.getObject("EccentricKey")
        if prop == "Eccentricity":
            gbp.Eccentricity = ek.Eccentricity
            gbp.RollerDiameter = ek.Eccentricity * 2.0
        if prop == 'RollerDiameter':
            gbp.RollerDiameter = ek.RollerDiameter
        # if prop == 'RollerHeight':
        #    gbp.RollerHeight = ek.RollerHeight
        if prop == 'BaseHeight':
            gbp.BaseHeight = ek.BaseHeight
        if prop == 'ShaftDiameter':
            gbp.ShaftDiameter = ek.ShaftDiameter

    def recomputeGB(self, H):
        self.Object.Shape = cycloidFun.generateEccentricKey(H)


class OutShaft():
    def __init__(self, obj, gearbox):
        self.Object = obj
        self.gearbox = gearbox
        obj.Proxy = self
        self.Type = 'Output Shaft'
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyInteger", "DiskHoleCount", "CycloidGearBox", QT_TRANSLATE_NOOP("APP::Property",
                                                                                                     "Number of driving holes of the cycloid disk")).DiskHoleCount = param.DiskHoleCount
        obj.addProperty("App::PropertyLength", "ShaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).ShaftDiameter = param.ShaftDiameter
        self.Type = 'OutputShaft'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gbp = App.ActiveDocument.getObject("GearBox_Parameters")
        os = fp.Document.getObject("OutputShaft")
        if prop == "DiskHoleCount":
            gbp.DiskHoleCount = os.DiskHoleCount
        if prop == 'ShaftDiameter':
            gbp.ShaftDiameter = os.ShaftDiameter

    def recomputeGB(self, H):
        print("recomputing output shaft")
        self.Object.Shape = cycloidFun.generateOutputShaft(H)
        print("done recomputing output shaft")


class CycloidalGearBox():
    def __init__(self, obj):
        print("CycloidalGearBox __init__")
        self.busy = True
        H = cycloidFun.generateDefaultHyperParam()
        obj.addProperty("App::PropertyFloat", "Version", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property",
                                                                                             "The version of CycloidGearBox Workbench used to create this object")).Version = version
        obj.addProperty("App::PropertyLength", "Eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Eccentricity")).Eccentricity = H["Eccentricity"]
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).ToothCount = \
                        H["ToothCount"]
        obj.addProperty("App::PropertyLength","PinDiskDiameter",QT_TRANSLATE_NOOP("App::Property","PinDisk Diameter")).PinDiskDiameter = 40
        obj.addProperty("App::PropertyInteger", "DiskHoleCount", "CycloidGearBox", QT_TRANSLATE_NOOP("APP::Property",
                                                                                                     "Number of driving holes of the cycloid disk")).DiskHoleCount = \
        H["DiskHoleCount"]
        obj.addProperty("App::PropertyInteger", "LineSegmentCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property",
                                                                                                        "Number of line segments to make up the cycloidal disk")).LineSegmentCount = \
        H["LineSegmentCount"]
        obj.addProperty("App::PropertyAngle", "ToothPitch", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Tooth Pitch")).ToothPitch = H["ToothPitch"]
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).RollerDiameter = H[
            "RollerDiameter"]
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = H["RollerHeight"]
        obj.addProperty("App::PropertyLength", "CenterDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Center Diameter")).CenterDiameter = H["CenterDiameter"]
        obj.addProperty("App::PropertyLength", "PressureAngleLimit", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Limit")).PressureAngleLimit = H[
            "PressureAngleLimit"]
        obj.addProperty("App::PropertyAngle", "PressureAngleOffset", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Offset")).PressureAngleOffset = H[
            "PressureAngleOffset"]
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).BaseHeight = H["BaseHeight"]
        obj.addProperty("App::PropertyLength", "DriverPinHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Driver Pin Height")).DriverPinHeight = H["DriverPinHeight"]
        obj.addProperty("App::PropertyLength", "DriverDiskHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).DriverDiskHeight = H["DriverDiskHeight"]
        obj.addProperty("App::PropertyLength", "CycloidalDiskHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Cycloidal Disk Height")).CycloidalDiskHeight = H[
            "CycloidalDiskHeight"]
        obj.addProperty("App::PropertyLength", "ShaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).ShaftDiameter = H["ShaftDiameter"]
        obj.addProperty("App::PropertyLength", "clearance", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "clearance between parts")).clearance = H["clearance"]
        obj.addProperty("App::PropertyBool", "Animate", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Animate")).Animate = False
        # obj.Proxy = self
        self.recomputeList = []
        print("Properties added")
        self.Object = obj
        self.Type = 'CycloidalGearBox'
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))

        print('gearbox created')

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
        obj = App.ActiveDocument.getObject("GearBox_Parameters")
        pinDisk = App.ActiveDocument.getObject('pinDisk')
        es = App.ActiveDocument.getObject('EccentricShaft')
        dd = App.ActiveDocument.getObject('DriverDisk')
        if prop == 'Animate':
            if hasattr(obj, "Animate"):
                obj.Animate = not obj.Animate
                if obj.Animate:
                    timer.start(timeout)
                else:
                    timer.stop()
        if prop == 'PinDiskDiameter':
            pinDisk.PinDiskDiameter = obj.PinDiskDiameter
            dirty = True
        if prop == 'ShaftDiameter':
            if obj.ShaftDiameter < 1:
                obj.ShaftDiameter = 1
            if es.ShaftDiameter != obj.ShaftDiameter:
                es.ShaftDiameter = obj.ShaftDiameter
                pinDisk.ShaftDiameter = obj.ShaftDiameter
                dd.ShaftDiameter = obj.ShaftDiameter
            dirty = True
        if prop == 'RollerDiameter' and hasattr(es, "Eccentricity") and hasattr(obj, "Eccentricity"):
            if (obj.Eccentricity < 1):
                obj.Eccentricity = 1
            if es.Eccentricity != obj.Eccentricity:
                es.Eccentricity = obj.Eccentricity
            dirty = True
        if prop == 'ToothCount':
            if obj.ToothCount < 3:
                obj.ToothCount = 3
            if pinDisk.ToothCount != obj.ToothCount:
                pinDisk.ToothCount = obj.ToothCount
            dirty = True
        if prop == 'LineSegmentCount':
            dirty = True
        if prop == 'RollerDiameter':
            if hasattr(obj, "Eccentricity"):
                if obj.RollerDiameter < 1:
                    obj.RollerDiameter = 1
                if obj.Eccentricity != obj.RollerDiameter / 2:
                    obj.Eccentricity = obj.RollerDiameter / 2
                if hasattr(es, "Eccentricity") and es.Eccentricity != obj.Eccentricity:
                    es.Eccentricity = obj.Eccentricity
            if pinDisk.RollerDiameter != obj.RollerDiameter:
                pinDisk.RollerDiameter = obj.RollerDiameter
            dirty = True
        # if prop=='RollerHeight':
        #    if pinDisk.RollerHeight != obj.RollerHeight:
        #        pinDisk.RollerHeight = obj.RollerHeight
        #    dirty = True
        if prop == 'ToothPitch':
            if pinDisk.ToothCount != obj.ToothCount:
                pinDisk.ToothCount = obj.ToothCount
            dirty = True
        if prop == 'Eccentricity':
            if (obj.RollerDiameter < obj.Eccentricity * 2):
                obj.RollerDiameter = obj.Eccentricity * 2
            if hasattr(es, "Eccentricity") and es.Eccentricity != obj.Eccentricity:
                es.Eccentricity = obj.Eccentricity
            dirty = True
        if prop == 'CenterDiameter':
            dirty = True
        if prop == 'PressureAngleLimit':
            dirty = True
        if prop == 'PressureAngleOffset':
            dirty = True
        if prop == 'BaseHeight':
            if pinDisk.BaseHeight != obj.BaseHeight:
                pinDisk.BaseHeight = obj.BaseHeight
            dirty = True
        if prop == 'DriverDiskHeight':
            dirty = True
        if prop == 'CycloidalDiskHeight':
            dirty = True
        if prop == 'DiskHoleCount':
            dirty = True
        if prop == 'Refresh':
            dirty = True
        if prop == 'clearance':
            diry = True
        if dirty:
            print("recomputing")
            self.recompute()

    def GetHyperParameters(self):
        hyperparameters = {"ToothCount": int(self.Object.__getattribute__("ToothCount")),
                           "LineSegmentCount": int(self.Object.__getattribute__("LineSegmentCount")),
                           "RollerDiameter": float(self.Object.__getattribute__("RollerDiameter").Value),
                           "PinDiskDiameter": float(self.Object.__getattribute__("PinDiskDiameter").Value),
                           # "RollerHeight" : float(self.Object.__getattribute__("RollerHeight").Value),
                           "ToothPitch": float(self.Object.__getattribute__("ToothPitch").Value),
                           "Eccentricity": float(self.Object.__getattribute__("Eccentricity").Value),
                           "CenterDiameter": float(self.Object.__getattribute__("CenterDiameter").Value),
                           "PressureAngleLimit": float(self.Object.__getattribute__("PressureAngleLimit").Value),
                           "PressureAngleOffset": float(self.Object.__getattribute__("PressureAngleOffset").Value),
                           "BaseHeight": float(self.Object.__getattribute__("BaseHeight").Value),
                           "DriverPinHeight": float(self.Object.__getattribute__("DriverPinHeight").Value),
                           "DriverDiskHeight": float(self.Object.__getattribute__("DriverDiskHeight").Value),
                           "CycloidalDiskHeight": float(self.Object.__getattribute__("CycloidalDiskHeight").Value),
                           "DiskHoleCount": int(self.Object.__getattribute__("DiskHoleCount")),
                           "ShaftDiameter": float(self.Object.__getattribute__("ShaftDiameter")),
                           "clearance": float(self.Object.__getattribute__("clearance"))
                           }
        return hyperparameters

    def recompute(self):
        print("Recomputing all")
        hyperparameters = self.GetHyperParameters()
        for a in self.recomputeList:
            print(".")
            a.recomputeGB(hyperparameters)

    def execute(self, obj):
        # obj.Shape = self.gearBox.generatePinBase()
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
       if prop.name=='EccentricShaft':
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


def rotatepoint(cx, cy, a, v):
    s = math.sin(a)
    c = math.cos(a)
    # translate back to origin
    v = v - App.Vector(cx, cy, 0)
    x = float(v[0])
    y = float(v[1])
    return App.Vector(x * c - y * s + cx, x * s + y * c + cy, 0)


def turnES(a):
    global animation_busy
    if (animation_busy):
        return
    else:
        animation_busy = True
    constraintNr = 4
    # save global value in case this function is called from the console
    es = App.ActiveDocument.getObject('EccentricShaft')
    gbp = App.ActiveDocument.getObject("GearBox_Parameters")
    # print("Turning ",a)
    rot = App.Rotation(App.Vector(0, 0, 1), a)
    es_out = rotatepoint(es.Eccentricity,0,a,App.Vector(0,0,0))
    pos = es.Placement.Base
    NewPlace = App.Placement(pos, rot)
    es.Placement = NewPlace
    cd = App.ActiveDocument.getObject('CycloidalDisk')
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
    turnES(kwAngle)


#    genframe() # Bild erzeugen
timer.timeout.connect(update)
# timer.start(timeout)


FreeCADGui.addCommand('CycloidGearBoxCreateObject', CycloidGearBoxCreateObject())
