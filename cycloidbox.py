#!/usr/bin/python

"""Hypocycloid gear boxgenerator
Code to create a hypocycloidal gearBox
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
global animationBusy
animationBusy = False
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
                'ToolTip': "Create default gearBox"}

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
        body.Label = "gearBox"
        # FreeCADGui.ActiveDocument.ActiveView.setActiveObject("Body", body)
        # feature = App.ActiveDocument.addObject('PartDesign::AdditiveBox', 'Box')
        # obj.addObject(feature)
        # App.ActiveDocument.recompute()

        obj = doc.addObject("Part::FeaturePython", "GearBoxParameters")
        gearBox = CycloidalGearBox(obj)
        doc.recompute()
        obj.Proxy = gearBox
        random.seed(444)
        pindiskobj = doc.addObject("Part::FeaturePython", "pinDisk")
        obj.addProperty("App::PropertyString","IconFilename","","",8).IconFilename = pinIcon;
        #print(gearBox.GetHyperParameters())
        pinDisk = pindiskClass(pindiskobj, gearBox)
        pindiskobj.Proxy = pinDisk
        gearBox.recomputeList.append(pinDisk)
        ViewProviderCGBox(pindiskobj.ViewObject, pinIcon)
        pindiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        cycdiskobj = doc.addObject("Part::FeaturePython", "CycloidalDisk")
        cycdisk = cycdiskClass(cycdiskobj, gearBox)
        cycdiskobj.Proxy = cycdisk
        gearBox.recomputeList.append(cycdisk)
        ViewProviderCGBox(cycdiskobj.ViewObject, mainIcon)
        cycdiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        driverDiskobj = doc.addObject("Part::FeaturePython", "driverDisk")
        driverDisk = driverDiskClass(driverDiskobj, gearBox)
        driverDiskobj.Proxy = driverDisk
        gearBox.recomputeList.append(driverDisk)
        ViewProviderCGBox(driverDiskobj.ViewObject, pinIcon)
        driverDiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        eccentricShaftObj = doc.addObject("Part::FeaturePython", "eccentricShaft")
        escShaft = EccShaft(eccentricShaftObj, gearBox)
        eccentricShaftObj.Proxy = escShaft
        gearBox.recomputeList.append(escShaft)
        ViewProviderCGBox(eccentricShaftObj.ViewObject, eccentricIcon)
        eccentricShaftObj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        ekobj = doc.addObject("Part::FeaturePython", "eccentricKey")
        escKey = EccKey(ekobj, gearBox)
        ekobj.Proxy = escKey
        gearBox.recomputeList.append(escKey)
        ViewProviderCGBox(ekobj.ViewObject, eccentricIcon)
        ekobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        oShaftObj = doc.addObject("Part::FeaturePython", "outputShaft")
        oshaft = OutShaft(oShaftObj, gearBox)
        oshaft.Proxy = oshaft
        gearBox.recomputeList.append(oshaft)
        ViewProviderCGBox(oShaftObj.ViewObject, pinIcon)
        oShaftObj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        gearBox.busy = False
        gearBox.onChanged('', 'Refresh')
        gearBox.recompute()
        doc.recompute()
        gearBox.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
        # timer.start(timeout)
        return gearBox

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
        #print(param.rollerDiameter)
        obj.addProperty("App::PropertyLength", "rollerDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).rollerDiameter = param.rollerDiameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyInteger", "toothCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).toothCount = param.toothCount
        obj.addProperty("App::PropertyLength", "baseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).baseHeight = param.baseHeight
        obj.addProperty("App::PropertyLength", "shaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaftDiameter = param.shaftDiameter
        obj.addProperty("App::PropertyLength","pinDiskDiameter","CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","pinDisk Diameter")).pinDiskDiameter = param.pinDiskDiameter
        self.Type = 'pinDisk'
        print("Done Adding parameters")

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        # App.ActiveDocument.getObject("GearBoxParameters").onChanged(fp,prop)
        pinDisk = fp.Document.getObject('pinDisk')
        gearBox = App.ActiveDocument.getObject("GearBoxParameters")
        if prop == 'Proxy':
            pass
        if prop == 'toothCount':
            gearBox.toothCount = pinDisk.toothCount
        if prop == 'pinDiskDiameter':
            gearBox.pinDiskDiameter = pinDisk.pinDiskDiameter
        if prop == 'rollerDiameter':
            gearBox.rollerDiameter = pinDisk.rollerDiameter
        # if prop=='RollerHeight':
        #    gearBox.RollerHeight = pinDisk.RollerHeight
        if prop == 'baseHeight':
            gearBox.baseHeight = pinDisk.baseHeight
        if prop == 'shaftDiameter':
            gearBox.shaftDiameter = pinDisk.shaftDiameter

    def recomputeGB(self, H):
        print("recomputing pin disk", H)
        self.Object.Shape = cycloidFun.generatePinBase(H)
        # self.gearBox.gearBox.generatePinBase()


class driverDiskClass():
    def __init__(self, obj, gearBox):
        self.Object = obj
        obj.Proxy = self
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "diskHoleCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).diskHoleCount = param.diskHoleCount
        obj.addProperty("App::PropertyLength", "driverDiskHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Cycloidal Disk Height")).driverDiskHeight = param.cycloidalDiskHeight
        obj.addProperty("App::PropertyLength", "driverPinHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Driver Pin Height")).driverPinHeight = param.driverPinHeight
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = param.eccentricity
        obj.addProperty("App::PropertyLength", "shaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaftDiameter = param.shaftDiameter
        self.Type = 'driverDisk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("Driver Disk onchanged", fp, prop)
        gbp = App.ActiveDocument.getObject("GearBoxParameters")
        dd = fp.Document.getObject('driverDisk')
        if prop == 'diskHoleCount':
            gbp.diskHoleCount = dd.diskHoleCount
        if prop == 'driverDiskHeight':
            gbp.driverDiskHeight = dd.driverDiskHeight
        if prop == 'driverPinHeight':
            gbp.driverPinHeight = dd.driverPinHeight
        if prop == 'eccentricity':
            gbp.eccentricity = dd.eccentricity
        if prop == 'shaftDiameter':
            gbp.shaftDiameter = dd.shaftDiameter

    def execute(selfself, obj):
        print('driverDisk execute', obj)

    def recomputeGB(self, H):
        print('recomputing driverDisk')
        self.Object.Shape = cycloidFun.generateDriverDisk(H)


class cycdiskClass():
    def __init__(self, obj, gearBox):
        self.Object = obj
        obj.Proxy = self
        # obj.addProperty("App::PropertyString", "Parent","Parameter","Parent").Parent = App.ActiveDocument.GearBoxParameters
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "diskHoleCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).diskHoleCount = param.diskHoleCount
        obj.addProperty("App::PropertyInteger", "toothCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).toothCount = param.toothCount
        obj.addProperty("App::PropertyLength", "cycloidalDiskHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "Cycloidal Disk Height")).cycloidalDiskHeight = param.cycloidalDiskHeight
        self.gearBox = gearBox
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
        s = fp.Document.getObject('CycloidalDisk')
        if prop == 'diskHoleCount':
            p.diskHoleCount = s.diskHoleCount
        if prop == 'cycloidalDiskHeight':
            p.cycloidalDiskHeight = s.cycloidalDiskHeight
        if prop == 'toothCount':
            p.toothCount = s.toothCount

    def execute(self, obj):
        # obj.Shape = self.gearBox.generatePinBase()
        print('cycloidgearbox execute', obj)

    def recomputeGB(self, H):
        print("recomputing cycloidal disk")
        self.Object.Shape = cycloidFun.generateCycloidalDisk(H)


class EccShaft():
    def __init__(self, obj, gearBox):
        self.Object = obj
        self.gearBox = gearBox
        obj.Proxy = self
        self.Type = 'EccShaft'
        self.ShapeColor = (0.42, 0.42, 0.63)
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = param.eccentricity
        obj.addProperty("App::PropertyLength", "rollerDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).rollerDiameter = param.rollerDiameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyLength", "baseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).baseHeight = param.baseHeight
        obj.addProperty("App::PropertyLength", "shaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaftDiameter = param.shaftDiameter

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gbp = App.ActiveDocument.getObject("GearBoxParameters")
        eccentricShaftObj = fp.Document.getObject("eccentricShaft")
        if prop == "eccentricity":
            gbp.eccentricity = eccentricShaftObj.eccentricity
            gbp.rollerDiameter = eccentricShaftObj.eccentricity * 2.0
        if prop == 'rollerDiameter':
            gbp.rollerDiameter = eccentricShaftObj.rollerDiameter
        # if prop == 'RollerHeight':
        #    gbp.RollerHeight = eccentricShaftObj.RollerHeight
        if prop == 'baseHeight':
            gbp.baseHeight = eccentricShaftObj.baseHeight
        if prop == 'shaftDiameter':
            gbp.shaftDiameter = eccentricShaftObj.shaftDiameter

    def recomputeGB(self, H):
        print("recomputing Eccentric Shaft")
        self.Object.Shape = cycloidFun.generateEccentricShaft(H)


class EccKey():
    def __init__(self, obj, gearBox):
        self.Object = obj
        self.gearBox = gearBox
        obj.Proxy = self
        self.Type = 'EccKey'
        self.ShapeColor = (0.62, 0.42, 0.63)
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = param.eccentricity
        obj.addProperty("App::PropertyLength", "rollerDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).rollerDiameter = param.rollerDiameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyLength", "baseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).baseHeight = param.baseHeight
        obj.addProperty("App::PropertyLength", "shaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaftDiameter = param.shaftDiameter

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gbp = App.ActiveDocument.getObject("GearBoxParameters")
        ek = fp.Document.getObject("eccentricKey")
        if prop == "eccentricity":
            gbp.eccentricity = ek.eccentricity
            gbp.rollerDiameter = ek.eccentricity * 2.0
        if prop == 'rollerDiameter':
            gbp.rollerDiameter = ek.rollerDiameter
        # if prop == 'RollerHeight':
        #    gbp.RollerHeight = ek.RollerHeight
        if prop == 'baseHeight':
            gbp.baseHeight = ek.baseHeight
        if prop == 'shaftDiameter':
            gbp.shaftDiameter = ek.shaftDiameter

    def recomputeGB(self, H):
        self.Object.Shape = cycloidFun.generateEccentricKey(H)


class OutShaft():
    def __init__(self, obj, gearBox):
        self.Object = obj
        self.gearBox = gearBox
        obj.Proxy = self
        self.Type = 'Output Shaft'
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "diskHoleCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).diskHoleCount = param.diskHoleCount
        obj.addProperty("App::PropertyLength", "shaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaftDiameter = param.shaftDiameter
        self.Type = 'outputShaft'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gbp = App.ActiveDocument.getObject("GearBoxParameters")
        os = fp.Document.getObject("outputShaft")
        if prop == "diskHoleCount":
            gbp.diskHoleCount = os.diskHoleCount
        if prop == 'shaftDiameter':
            gbp.shaftDiameter = os.shaftDiameter

    def recomputeGB(self, H):
        print("recomputing output shaft")
        self.Object.Shape = cycloidFun.generateOutputShaft(H)
        print("done recomputing output shaft")


class CycloidalGearBox():
    def __init__(self, obj):
        print("CycloidalGearBox __init__")
        self.busy = True
        H = cycloidFun.generateDefaultHyperParam()
        obj.addProperty("App::PropertyFloat", "Version", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "The version of CycloidGearBox Workbench used to create this object")).Version = version
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = H["eccentricity"]
        obj.addProperty("App::PropertyInteger", "toothCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).toothCount = H["toothCount"]
        obj.addProperty("App::PropertyLength","pinDiskDiameter",
                        QT_TRANSLATE_NOOP("App::Property","pinDisk Diameter")).pinDiskDiameter = 40
        obj.addProperty("App::PropertyInteger", "diskHoleCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).diskHoleCount = \
        H["diskHoleCount"]
        obj.addProperty("App::PropertyInteger", "lineSegmentCount", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of line segments to make up the cycloidal disk")).lineSegmentCount = \
        H["lineSegmentCount"]
        obj.addProperty("App::PropertyAngle", "toothPitch", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Tooth Pitch")).toothPitch = H["toothPitch"]
        obj.addProperty("App::PropertyLength", "rollerDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).rollerDiameter = H["rollerDiameter"]
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = H["RollerHeight"]
        obj.addProperty("App::PropertyLength", "centerDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Center Diameter")).centerDiameter = H["centerDiameter"]
        obj.addProperty("App::PropertyLength", "pressureAngleLimit", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Limit")).pressureAngleLimit = H["pressureAngleLimit"]
        obj.addProperty("App::PropertyAngle", "pressureAngleOffset", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Offset")).pressureAngleOffset = H["pressureAngleOffset"]
        obj.addProperty("App::PropertyLength", "baseHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).baseHeight = H["baseHeight"]
        obj.addProperty("App::PropertyLength", "driverPinHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Driver Pin Height")).driverPinHeight = H["driverPinHeight"]
        obj.addProperty("App::PropertyLength", "driverDiskHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).driverDiskHeight = H["driverDiskHeight"]
        obj.addProperty("App::PropertyLength", "cycloidalDiskHeight", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Cycloidal Disk Height")).cycloidalDiskHeight = H["cycloidalDiskHeight"]
        obj.addProperty("App::PropertyLength", "shaftDiameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaftDiameter = H["shaftDiameter"]
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

        print('gearBox created')

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
        global animationBusy
        if animationBusy:
            return
        print("GearBox_Paramenter onchanged", fp, prop)
        if hasattr(self, "busy"):
            if self.busy:
                return
        dirty = False
        obj = App.ActiveDocument.getObject("GearBoxParameters")
        pinDisk = App.ActiveDocument.getObject('pinDisk')
        eccentricShaftObj = App.ActiveDocument.getObject('eccentricShaft')
        dd = App.ActiveDocument.getObject('driverDisk')
        if prop == 'animate':
            if hasattr(obj, "animate"):
                obj.animate = not obj.animate
                if obj.animate:
                    timer.start(timeout)
                else:
                    timer.stop()
        if prop == 'pinDiskDiameter':
            if (pinDisk.pinDiskDiameter!=obj.pinDiskDiameter):
                pinDisk.pinDiskDiameter = obj.pinDiskDiameter
                dirty = True
        if prop == 'shaftDiameter':
            if obj.shaftDiameter < 1:
                obj.shaftDiameter = 1
            if eccentricShaftObj.shaftDiameter != obj.shaftDiameter:
                eccentricShaftObj.shaftDiameter = obj.shaftDiameter
                pinDisk.shaftDiameter = obj.shaftDiameter
                dd.shaftDiameter = obj.shaftDiameter
            dirty = True
        if prop == 'rollerDiameter' and hasattr(eccentricShaftObj, "eccentricity") and hasattr(obj, "eccentricity"):
            if (obj.eccentricity < 1):
                obj.eccentricity = 1
            if eccentricShaftObj.eccentricity != obj.eccentricity:
                eccentricShaftObj.eccentricity = obj.eccentricity
            dirty = True
        if prop == 'toothCount':
            if obj.toothCount < 3:
                obj.toothCount = 3
            if pinDisk.toothCount != obj.toothCount:
                pinDisk.toothCount = obj.toothCount
            dirty = True
        if prop == 'lineSegmentCount':
            dirty = True
        if prop == 'rollerDiameter':
            if hasattr(obj, "eccentricity"):
                if obj.rollerDiameter < 1:
                    obj.rollerDiameter = 1
                if obj.eccentricity != obj.rollerDiameter / 2:
                    obj.eccentricity = obj.rollerDiameter / 2
                if hasattr(eccentricShaftObj, "eccentricity") and eccentricShaftObj.eccentricity != obj.eccentricity:
                    eccentricShaftObj.eccentricity = obj.eccentricity
            if pinDisk.rollerDiameter != obj.rollerDiameter:
                pinDisk.rollerDiameter = obj.rollerDiameter
            dirty = True
        # if prop=='RollerHeight':
        #    if pinDisk.RollerHeight != obj.RollerHeight:
        #        pinDisk.RollerHeight = obj.RollerHeight
        #    dirty = True
        if prop == 'toothPitch':
            if pinDisk.toothCount != obj.toothCount:
                pinDisk.toothCount = obj.toothCount
            dirty = True
        if prop == 'eccentricity':
            if (obj.rollerDiameter < obj.eccentricity * 2):
                obj.rollerDiameter = obj.eccentricity * 2
            if hasattr(eccentricShaftObj, "eccentricity") and eccentricShaftObj.eccentricity != obj.eccentricity:
                eccentricShaftObj.eccentricity = obj.eccentricity
            dirty = True
        if prop == 'centerDiameter':
            dirty = True
        if prop == 'pressureAngleLimit':
            dirty = True
        if prop == 'pressureAngleOffset':
            dirty = True
        if prop == 'baseHeight':
            if pinDisk.baseHeight != obj.baseHeight:
                pinDisk.baseHeight = obj.baseHeight
            dirty = True
        if prop == 'driverDiskHeight':
            dirty = True
        if prop == 'cycloidalDiskHeight':
            dirty = True
        if prop == 'diskHoleCount':
            dirty = True
        if prop == 'Refresh':
            dirty = True
        if prop == 'clearance':
            diry = True
        if dirty:
            print("recomputing")
            self.recompute()

    def GetHyperParameters(self):
        hyperparameters = {"toothCount": int(self.Object.__getattribute__("toothCount")),
                           "lineSegmentCount": int(self.Object.__getattribute__("lineSegmentCount")),
                           "rollerDiameter": float(self.Object.__getattribute__("rollerDiameter").Value),
                           "pinDiskDiameter": float(self.Object.__getattribute__("pinDiskDiameter").Value),
                           # "RollerHeight" : float(self.Object.__getattribute__("RollerHeight").Value),
                           "toothPitch": float(self.Object.__getattribute__("toothPitch").Value),
                           "eccentricity": float(self.Object.__getattribute__("eccentricity").Value),
                           "centerDiameter": float(self.Object.__getattribute__("centerDiameter").Value),
                           "pressureAngleLimit": float(self.Object.__getattribute__("pressureAngleLimit").Value),
                           "pressureAngleOffset": float(self.Object.__getattribute__("pressureAngleOffset").Value),
                           "baseHeight": float(self.Object.__getattribute__("baseHeight").Value),
                           "driverPinHeight": float(self.Object.__getattribute__("driverPinHeight").Value),
                           "driverDiskHeight": float(self.Object.__getattribute__("driverDiskHeight").Value),
                           "cycloidalDiskHeight": float(self.Object.__getattribute__("cycloidalDiskHeight").Value),
                           "diskHoleCount": int(self.Object.__getattribute__("diskHoleCount")),
                           "shaftDiameter": float(self.Object.__getattribute__("shaftDiameter")),
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


def rotatepoint(cx, cy, a, v):
    s = math.sin(a)
    c = math.cos(a)
    # translate back to origin
    v = v - App.Vector(cx, cy, 0)
    x = float(v[0])
    y = float(v[1])
    return App.Vector(x * c - y * s + cx, x * s + y * c + cy, 0)


def turnES(a):
    global animationBusy
    if (animationBusy):
        return
    else:
        animationBusy = True
    constraintNr = 4
    # save global value in case this function is called from the console
    eccentricShaftObj = App.ActiveDocument.getObject('eccentricShaft')
    gbp = App.ActiveDocument.getObject("GearBoxParameters")
    # print("Turning ",a)
    rot = App.Rotation(App.Vector(0, 0, 1), a)
    es_out = rotatepoint(eccentricShaftObj.eccentricity,0,a,App.Vector(0,0,0))
    pos = eccentricShaftObj.Placement.Base
    NewPlace = App.Placement(pos, rot)
    eccentricShaftObj.Placement = NewPlace
    cd = App.ActiveDocument.getObject('CycloidalDisk')
    cdpos = es_out
    #cd.Placement.Base
    cdrot = App.Rotation(App.Vector(0, 0, 1), -a)
    cd.Placement = App.Placement(cdpos, cdrot)

    animationBusy = False
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
