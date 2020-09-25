"""Hypocycloid gear boxgenerator
Code to create a hypocycloidal gear_box
https://en.wikipedia.org/wiki/Cycloidal_drive

Copyright   2019, Chris Bruner
Version    v0.1
License    LGPL V2.1
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
import pinDisk
import driverDisk
import eccShaft
import eccKey
import outShaft
import cycloidalDisk

smWBpath = os.path.dirname(cycloidFun.__file__)
smWB_icons_path = os.path.join(smWBpath, 'icons')
global mainIcon
mainIcon = os.path.join(smWB_icons_path, 'cycloidgearbox.svg')
global pinIcon
pinIcon = os.path.join(smWB_icons_path, 'cycloidpin.svg')
# __dir__ = os.path.dirname(__file__)
global eccentricIcon
eccentricIcon = os.path.join(smWB_icons_path, 'eccentric.svg')
# # iconPath = os.path.join( __dir__, 'Resources', 'icons' )
# keepToolbar = False
version ='Sep 24,2020'


def QT_TRANSLATE_NOOP(scope, text):
   return text


"""
todo:
Driver Pin Height doesn't update
Driver Disk Height should be Driver Disk Offset
Driver Disk Height should refer to depth of driver disk
"""


class CycloidGearBoxCreateObject():
    # """
    # The part that holds the parameters used to make the phsyical parts
    # """

    def GetResources(self):
        return {'Pixmap': mainIcon,
           'MenuText': "&Create CycloidalGear",
           'ToolTip': "Create default gear_box"}

    def __init__(self):
        pass

    # @property
    def Activated(self):
        if not App.ActiveDocument:
           App.newDocument()
        doc = App.ActiveDocument
        body = doc.addObject('PartDesign::Body', 'Body')
        body.Label = "gear_box"
        #doc.RecomputesFrozen = True
        obj = doc.addObject("Part::FeaturePython", "GearBoxParameters")
        gear_box = CycloidalGearBox(obj)
        doc.recompute()
        random.seed(444)
        pindiskobj = doc.addObject("Part::FeaturePython", "pin_disk")
        obj.addProperty("App::PropertyString", "IconFilename", "", "", 8).IconFilename = pinIcon
        # print(gear_box.GetHyperParameters())
        pin_disk = pinDisk.pindiskClass(pindiskobj, gear_box)

        pindiskobj.Proxy = pin_disk
        gear_box.recomputeList.append(pin_disk)
        ViewProviderCGBox(pindiskobj.ViewObject, pinIcon)
        pindiskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        cycloidal_diskobj = doc.addObject("Part::FeaturePython", "cycloidal_disk")
        cycloidal_disk = cycloidalDisk.cycdiskClass(cycloidal_diskobj, gear_box)
        cycloidal_diskobj.Proxy = cycloidal_disk
        gear_box.recomputeList.append(cycloidal_disk)
        ViewProviderCGBox(cycloidal_diskobj.ViewObject, mainIcon)
        cycloidal_diskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        driver_diskobj = doc.addObject("Part::FeaturePython", "driver_disk")
        driver_disk = driverDisk.driver_diskClass(driver_diskobj, gear_box)
        driver_diskobj.Proxy = driver_disk
        gear_box.recomputeList.append(driver_disk)
        ViewProviderCGBox(driver_diskobj.ViewObject, pinIcon)
        driver_diskobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        eccentric_shaft_obj = doc.addObject("Part::FeaturePython", "eccentric_shaft")
        escShaft = eccShaft.EccShaft(eccentric_shaft_obj, gear_box)
        eccentric_shaft_obj.Proxy = escShaft
        gear_box.recomputeList.append(escShaft)
        ViewProviderCGBox(eccentric_shaft_obj.ViewObject, eccentricIcon)
        eccentric_shaft_obj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        ekobj = doc.addObject("Part::FeaturePython", "eccentricKey")
        escKey = eccKey.EccKey(ekobj, gear_box)
        ekobj.Proxy = escKey
        gear_box.recomputeList.append(escKey)
        ViewProviderCGBox(ekobj.ViewObject, eccentricIcon)
        ekobj.ViewObject.ShapeColor = (random.random(), random.random(), random.random(), 0.0)

        oShaftObj = doc.addObject("Part::FeaturePython", "output_shaft")
        oshaft = outShaft.OutShaft(oShaftObj, gear_box)
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
        return gear_box

    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        print("CycloidalGearBox.Deactivated()\n")

    def execute(self, obj):
        print('cycloidgearboxCreateObject execute')


class CycloidalGearBox():
    def __init__(self, obj):
        print("CycloidalGearBox __init__")
        self.busy = True
        H = cycloidFun.generate_default_hyperparam()
        #read only properites
        obj.addProperty("App::PropertyString", "Version", "read only", QT_TRANSLATE_NOOP("App::Property", "The version of CycloidGearBox Workbench used to create this object"),1).Version = version
        obj.addProperty("App::PropertyLength", "Min_Diameter", "read only", "", 1)
        obj.addProperty("App::PropertyLength", "Max_Diameter", "read only", "", 1)
        # pin_disk
        obj.addProperty("App::PropertyLength",  "pin_disk_pin_diameter",  "pin_disk,eccentric_shaft,eccentric_key", QT_TRANSLATE_NOOP("App::Property", "pin_disk_pin_diameter")).pin_disk_pin_diameter = H[ "pin_disk_pin_diameter"]
        obj.addProperty("App::PropertyLength",  "base_height",      "pin_disk,eccentric_shaft,eccentric_key", QT_TRANSLATE_NOOP("App::Property", "base_height")).base_height = H["base_height"]
        obj.addProperty("App::PropertyLength",  "shaft_diameter",   "pin_disk,driver_disk,eccentric_shaft,eccentric_key", QT_TRANSLATE_NOOP("App::Property", "shaft_diameter")).shaft_diameter = H["shaft_diameter"]
        obj.addProperty("App::PropertyInteger", "tooth_count",      "pin_disk,cycloidal_disk", QT_TRANSLATE_NOOP("App::Property", "number of cycloidal teeth, ratio = 1/(tooth_count - 1)")).tooth_count = H[ "tooth_count"]
        obj.addProperty("App::PropertyAngle", "tooth_pitch",        "pin_disk,cycloidal_disk", QT_TRANSLATE_NOOP("App::Property", "Cycloidal Disk")).tooth_pitch = H["tooth_pitch"]
        # driver_disk
        obj.addProperty("App::PropertyInteger","driver_disk_hole_count",       "driver_disk,output_shaft,cycloidal_disk", QT_TRANSLATE_NOOP("APP::Property", "Output Shaft")).driver_disk_hole_count = H["driver_disk_hole_count"]
        obj.addProperty("App::PropertyLength", "eccentricity",          "driver_disk,eccentric_shaft,eccentric_key", QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = H["eccentricity"]
        # eccentric_shaft all properties in other classes


        obj.addProperty("App::PropertyLength", "Height",           "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property", "gearbox")).Height = H["Height"]
        obj.addProperty("App::PropertyLength",  "Diameter",       "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property", "Diameter")).Diameter = H[ "Diameter"]
        obj.addProperty("App::PropertyInteger", "line_segment_count", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property", "Number of line segments to make up the cycloidal disk")).line_segment_count = H["line_segment_count"]

        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = H["RollerHeight"]
        obj.addProperty("App::PropertyLength", "pressure_angle_limit", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Limit")).pressure_angle_limit = H[ "pressure_angle_limit"]
        obj.addProperty("App::PropertyAngle", "pressure_angle_offset", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property", "Pressure Angle Offset")).pressure_angle_offset = H[ "pressure_angle_offset"]
        obj.addProperty("App::PropertyLength", "clearance", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property", "clearance between parts")).clearance = H["clearance"]
        # eccentric Shaft
        # shaft diameter also in output shaft
        # driver_disk_hole_count (also in output shaft)


        self.recomputeList = []
        print("Properties added")
        self.Type = 'CycloidalGearBox'
        self.Object = obj
        obj.Proxy = self
        attrs = vars(self)
#        print(', '.join("%s: %s" % item for item in attrs.items()))

#        print('gear_box created')

#    def parameterization(self, pts, a, closed):
#        print("parameterization")
#        return 0

#    def makePoints(selfself, obj):
#        print("makepoints")
#        return []

#    def activated(self):
#        print("Cycloidal.Activated()\n")

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("GearBox_Paramenter onchanged", fp, prop)
        if hasattr(self, "busy"):
           if self.busy:
              return
        else:
           return
        dirty = False
        obj = App.ActiveDocument.getObject("GearBoxParameters")
        pin_disk = App.ActiveDocument.getObject('pin_disk')
        driver_disk = App.ActiveDocument.getObject('driver_disk')
        cycloidal_disk = App.ActiveDocument.getObject('cycloidal_disk')
        eccentric_shaft_obj = App.ActiveDocument.getObject('eccentricShaft')
        dd = App.ActiveDocument.getObject('driver_disk')
        output_shaft = App.ActiveDocument.getObject('output_shaft')
        if prop == 'Height':
              dirty = True
        if prop == 'Diameter':
           if (pin_disk.Diameter != obj.Diameter):
              pin_disk.Diameter = obj.Diameter
              dirty = True
        if prop == 'shaft_diameter':
           if obj.shaft_diameter < 1:
              obj.shaft_diameter = 1
           if eccentric_shaft_obj.shaft_diameter != obj.shaft_diameter:
              eccentric_shaft_obj.shaft_diameter = obj.shaft_diameter
              pin_disk.shaft_diameter = obj.shaft_diameter
              dd.shaft_diameter = obj.shaft_diameter
           dirty = True
        if prop == 'pin_disk_pin_diameter' and hasattr(eccentric_shaft_obj, "eccentricity") and hasattr(obj, "eccentricity"):
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
           if cycloidal_disk.tooth_count != obj.tooth_count:
               cycloidal_disk.tooth_count = obj.tooth_count
           dirty = True
        if prop == 'line_segment_count':
           dirty = True
        if prop == 'pin_disk_pin_diameter':
           if hasattr(obj, "eccentricity"):
              if obj.pin_disk_pin_diameter < 1:
                  obj.pin_disk_pin_diameter = 1
              if obj.eccentricity != obj.pin_disk_pin_diameter / 2:
                  obj.eccentricity = obj.pin_disk_pin_diameter / 2
              if hasattr(eccentric_shaft_obj,
                        "eccentricity") and eccentric_shaft_obj.eccentricity != obj.eccentricity:
                  eccentric_shaft_obj.eccentricity = obj.eccentricity
           if pin_disk.pin_disk_pin_diameter != obj.pin_disk_pin_diameter:
              pin_disk.pin_disk_pin_diameter = obj.pin_disk_pin_diameter
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
           if (obj.pin_disk_pin_diameter < obj.eccentricity * 2):
              obj.pin_disk_pin_diameter = obj.eccentricity * 2
           if hasattr(eccentric_shaft_obj, "eccentricity") and eccentric_shaft_obj.eccentricity != obj.eccentricity:
              eccentric_shaft_obj.eccentricity = obj.eccentricity
           dirty = True
        if prop == 'pressure_angle_limit':
           dirty = True
        if prop == 'pressure_angle_offset':
           dirty = True
        if prop == 'base_height':
           if pin_disk.base_height != obj.base_height:
              pin_disk.base_height = obj.base_height
           dirty = True
        if prop == 'driver_disk_hole_count':
           if (driver_disk.driver_disk_hole_count != obj.driver_disk_hole_count):
              driver_disk.driver_disk_hole_count = obj.driver_disk_hole_count
              dirty = True
        if prop == 'Refresh':
           dirty = True
        if prop == 'clearance':
           dirty = True
        if dirty:
           print("recomputing")
           self.recompute()

    def GetHyperParameters(self):
        hyperparameters = {"tooth_count": int(self.Object.__getattribute__("tooth_count")),
                        "line_segment_count": int(self.Object.__getattribute__("line_segment_count")),
                        "pin_disk_pin_diameter": float(self.Object.__getattribute__("pin_disk_pin_diameter").Value),
                        "Diameter": float(self.Object.__getattribute__("Diameter").Value),
                        "tooth_pitch": float(self.Object.__getattribute__("tooth_pitch").Value),
                        "eccentricity": float(self.Object.__getattribute__("eccentricity").Value),
                        "pressure_angle_limit": float(self.Object.__getattribute__("pressure_angle_limit").Value),
                        "pressure_angle_offset": float(self.Object.__getattribute__("pressure_angle_offset").Value),
                        "base_height": float(self.Object.__getattribute__("base_height").Value),
                        "driver_disk_hole_count": int(self.Object.__getattribute__("driver_disk_hole_count")),
                        "Height": int(self.Object.__getattribute__("Height")),
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
    def __init__(self, obj, iconfile):
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
        # print("viewProviderCGBox setDisplayMode", mode)
        return mode

    def onChanged(self, vobj, prop):
        """
      Print the name of the property that has changed
      """

        # def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """
        # return self.icon
        # return main_CGB_Icon

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


#    #  App.ActiveDocument.Sketch.setDatum(constraintNr,App.Units.Quantity(str(-kwAngle)+'  deg'))
#    App.ActiveDocument.recompute()




FreeCADGui.addCommand('CycloidGearBoxCreateObject', CycloidGearBoxCreateObject())
