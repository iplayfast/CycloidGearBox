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

import os
import random
import FreeCADGui
import FreeCAD as App
import cycloidFun
from PySide import QtCore
smWBpath = os.path.dirname(cycloidFun.__file__)
smWB_icons_path = os.path.join(smWBpath, 'icons')
global mainIcon
mainIcon = os.path.join(smWB_icons_path, 'cycloidgearbox.svg')
global SketchIcon
SketchIcon = os.path.join(smWB_icons_path, 'cycloidgearbox.svg')
global pinIcon
pinIcon = os.path.join(smWB_icons_path, 'cycloidpin.svg')
# __dir__ = os.path.dirname(__file__)
global eccentricIcon
eccentricIcon = os.path.join(smWB_icons_path, 'eccentric.svg')
global sketchIcon
sketchIcon = os.path.join(smWB_icons_path,'SketcherWorkbench.svg')
# # iconPath = os.path.join( __dir__, 'Resources', 'icons' )
# keepToolbar = False
version = 'Mar 5,2022'


def QT_TRANSLATE_NOOP(scope, text):
    return text


"""
todo:

"""
"""class CycloidCreateSketch():

    def __init__(self):
        pass

    def Activated(selfself):
        doc = App.ActiveDocument
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
        body = doc.addObject('PartDesign::Body', 'gear_box')
        gear_box_obj = doc.addObject("Part::FeaturePython", "GearBoxParameters")
        gear_box = CycloidalGearBox(gear_box_obj)
        doc.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
        return gear_box

    def IsActive(self):
        return True

    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        pass

    def execute(self, obj):
        pass


class CycloidalGearBox():
    def __init__(self, obj):        
        self.Dirty = False
        H = cycloidFun.generate_default_parameters()
        # read only properites
        obj.addProperty("App::PropertyString", "Version", "read only", QT_TRANSLATE_NOOP(
            "App::Property", "The version of CycloidGearBox Workbench used to create this object"), 1).Version = version
        obj.addProperty("App::PropertyLength",
                        "Min_Diameter", "read only", "", 1)
        obj.addProperty("App::PropertyLength",
                        "Max_Diameter", "read only", "", 1)
        # pin_disk
        obj.addProperty("App::PropertyLength",  "roller_diameter",  "pin_disk,input_shaft,eccentric_key", QT_TRANSLATE_NOOP(
            "App::Property", "roller_diameter")).roller_diameter = H["roller_diameter"]
        obj.addProperty("App::PropertyLength",  "roller_circle_diameter",  "pin_disk", QT_TRANSLATE_NOOP(
            "App::Property", "roller_circle_diameter")).roller_circle_diameter = H["roller_circle_diameter"]
        
        obj.addProperty("App::PropertyLength",  "disk_height",      "pin_disk,input_shaft,eccentric_key,driver_disk,input_shaft,eccentric_key,cycloidal_disk,input_shaft,eccentric_key",
                        QT_TRANSLATE_NOOP("App::Property", "base_height")).disk_height = H["disk_height"]
    
        obj.addProperty("App::PropertyLength",  "shaft_diameter",   "pin_disk,driver_disk,input_shaft,eccentric_key",
                        QT_TRANSLATE_NOOP("App::Property", "shaft_diameter")).shaft_diameter = H["shaft_diameter"]
        
        obj.addProperty("App::PropertyLength",  "key_diameter",   "input_shaft,eccentric_key",
                        QT_TRANSLATE_NOOP("App::Property", "key_diameter")).key_diameter = H["key_diameter"]
        obj.addProperty("App::PropertyLength",  "key_flat_diameter",   "input_shaft,eccentric_key",
                        QT_TRANSLATE_NOOP("App::Property", "key_diameter")).key_flat_diameter = H["key_flat_diameter"]

        #cycloidal disks
        obj.addProperty("App::PropertyInteger", "tooth_count",      "pin_disk,cycloidal_disk", QT_TRANSLATE_NOOP(
            "App::Property", "number of cycloidal teeth, ratio = 1/(tooth_count - 1)")).tooth_count = H["tooth_count"]
        obj.addProperty("App::PropertyAngle", "tooth_pitch",        "pin_disk,cycloidal_disk",
                        QT_TRANSLATE_NOOP("App::Property", "Cycloidal Disk")).tooth_pitch = H["tooth_pitch"]
        obj.addProperty("App::PropertyLength",  "base_height",      "pin_disk",
                        QT_TRANSLATE_NOOP("App::Property", "base_height")).base_height = H["base_height"]
        
        # driver_disk
        obj.addProperty("App::PropertyLength", "driver_circle_diameter",       "driver_disk,pin_disk",
                        QT_TRANSLATE_NOOP("APP::Property", "Driver Disk")).driver_circle_diameter = H["driver_circle_diameter"]
        obj.addProperty("App::PropertyInteger", "driver_disk_hole_count",       "driver_disk,output_shaft,cycloidal_disk",
                        QT_TRANSLATE_NOOP("APP::Property", "Output Shaft")).driver_disk_hole_count = H["driver_disk_hole_count"]
        obj.addProperty("App::PropertyLength", "driver_hole_diameter",       "driver_disk,output_shaft,cycloidal_disk",
                        QT_TRANSLATE_NOOP("APP::Property", "Output Shaft")).driver_hole_diameter = H["driver_hole_diameter"]
        obj.addProperty("App::PropertyLength", "eccentricity",          "driver_disk,input_shaft,eccentric_key",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = H["eccentricity"]
        
        # input_shaft all properties in other classes

        obj.addProperty("App::PropertyLength", "Height",           "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "gearbox")).Height = H["Height"]
        obj.addProperty("App::PropertyLength",  "Diameter",       "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter")).Diameter = H["Diameter"]
        obj.addProperty("App::PropertyInteger", "line_segment_count", "CycloidGearBox", QT_TRANSLATE_NOOP(
            "App::Property", "Number of line segments to make up the cycloidal disk")).line_segment_count = H["line_segment_count"]

        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = H["RollerHeight"]
        obj.addProperty("App::PropertyLength", "pressure_angle_limit", "CycloidGearBox", QT_TRANSLATE_NOOP(
            "App::Property", "Pressure Angle Limit")).pressure_angle_limit = H["pressure_angle_limit"]
        obj.addProperty("App::PropertyAngle", "pressure_angle_offset", "CycloidGearBox", QT_TRANSLATE_NOOP(
            "App::Property", "Pressure Angle Offset")).pressure_angle_offset = H["pressure_angle_offset"]
        obj.addProperty("App::PropertyLength", "clearance", "CycloidGearBox", QT_TRANSLATE_NOOP(
            "App::Property", "clearance between parts")).clearance = H["clearance"]
        # input Shaft
        # shaft diameter also in output shaft
        # driver_disk_hole_count (also in output shaft)              
        self.Type = 'CycloidalGearBox'
        self.Object = obj
        self.doc = App.ActiveDocument
        obj.Proxy = self
        attrs = vars(self)

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        """Called when a property changes.

        Args:
            fp: Feature Python object
            prop: Property name that changed
        """
        # Mark for recompute when any property changes
        self.Dirty = True        

    def checksetProp(self,part, prop):
        """Check if part has property and update if different.

        Args:
            part: Part object to check
            prop: Property name to check and update

        Returns:
            True if property was updated, False otherwise
        """
        if (hasattr(part.Object, prop)):
            if (getattr(part.Object, prop) != getattr(self.Object, prop)):
                setattr(part.Object, prop, getattr(self.Object, prop))
                return True
        return False

    def GetParameters(self):
        parameters = {"tooth_count": int(self.Object.__getattribute__("tooth_count")),
                           "line_segment_count": int(self.Object.__getattribute__("line_segment_count")),
                           "roller_diameter": float(self.Object.__getattribute__("roller_diameter").Value),
                           "roller_circle_diameter": float(self.Object.__getattribute__("roller_circle_diameter").Value),
                           "driver_circle_diameter" : float(self.Object.__getattribute__("driver_circle_diameter").Value),
                           "Diameter": float(self.Object.__getattribute__("Diameter").Value),
                           "tooth_pitch": float(self.Object.__getattribute__("tooth_pitch").Value),
                           "eccentricity": float(self.Object.__getattribute__("eccentricity").Value),
                           "pressure_angle_limit": float(self.Object.__getattribute__("pressure_angle_limit").Value),
                           "pressure_angle_offset": float(self.Object.__getattribute__("pressure_angle_offset").Value),
                           "base_height": float(self.Object.__getattribute__("base_height").Value),
                           "disk_height": float(self.Object.__getattribute__("disk_height").Value),
                           "driver_disk_hole_count": int(self.Object.__getattribute__("driver_disk_hole_count")),
                           "driver_hole_diameter" : float(self.Object.__getattribute__("driver_hole_diameter").Value),
                           "Height": int(self.Object.__getattribute__("Height")),
                           "shaft_diameter": float(self.Object.__getattribute__("shaft_diameter")),
                           "key_diameter" : float(self.Object.__getattribute__("key_diameter")),
                           "key_flat_diameter" : float(self.Object.__getattribute__("key_flat_diameter")),
                           "clearance": float(self.Object.__getattribute__("clearance"))
                           }
        minr,maxr = cycloidFun.calculate_min_max_radii(parameters)
            
        if (self.Object.__getattribute__("Max_Diameter")!=maxr*2):
            self.Object.__setattr__("Max_Diameter",maxr*2)    
        if (self.Object.__getattribute__("Min_Diameter")!=minr*2):
                self.Object.__setattr__("Min_Diameter",minr*2)    
        parameters["min_rad"] = minr
        parameters["max_rad"] = maxr        
        return parameters

    def force_Recompute(self):
        self.Dirty = True
        self.recompute()

    def recompute(self):
        """Recompute all gearbox parts if parameters changed."""
        if self.Dirty:
            try:
                cycloidFun.generate_parts(App.ActiveDocument, self.GetParameters())
                self.Dirty = False
                App.ActiveDocument.recompute()
            except cycloidFun.ParameterValidationError as e:
                # Show error to user in FreeCAD console
                App.Console.PrintError(f"Cycloidal Gearbox Parameter Error: {str(e)}\n")
                App.Console.PrintError("Please adjust the parameters and try again.\n")
                raise
            except ValueError as e:
                App.Console.PrintError(f"Cycloidal Gearbox Math Error: {str(e)}\n")
                App.Console.PrintError("The current parameters may cause mathematical issues.\n")
                raise
            except Exception as e:
                App.Console.PrintError(f"Cycloidal Gearbox Error: {str(e)}\n")
                import traceback
                App.Console.PrintError(traceback.format_exc())
                raise
        
    """    def recompute(self):        
        print("gearbox recompute started")
        H = self.GetHyperParameters()        
        minDia = cycloidFun.calc_min_dia(H)
        if minDia > getattr(self.Object,'Diameter'):
            print('updating Diameter attribute, was too small')
            setattr(self.Object, 'Diameter', minDia)
            self.Diameter = minDia
        hyperparameters = self.GetHyperParameters()        
        cycloidFun.parts(App.ActiveDocument, hyperparameters)
        return
"""        

    def set_dirty(self):
        self.Dirty = True

    def execute(self, obj):                       
        t = QtCore.QTimer()
        t.singleShot(50, self.recompute)

class ViewProviderCGBox:
    """View provider for CycloidalGearBox object."""

    def __init__(self, obj, iconfile=None):
        """Set this object to the proxy object of the actual view provider.

        Args:
            obj: View provider object
            iconfile: Optional path to icon file
        """
        obj.Proxy = self
        self.part = obj
        self.iconfile = iconfile if iconfile else mainIcon

    def attach(self, obj):
        """Setup the scene sub-graph of the view provider.

        This method is mandatory for view providers.

        Args:
            obj: View provider object
        """
        self.ViewObject = obj
        self.Object = obj.Object
        return

    def updateData(self, fp, prop):
        """Called when a property of the handled feature has changed.

        Args:
            fp: Feature Python object
            prop: Property name that changed
        """
        return

    def getDisplayModes(self, obj):
        """Return a list of display modes.

        Args:
            obj: View provider object

        Returns:
            List of mode names
        """
        modes = ["Shaded", "Wireframe", "Flat Lines"]
        return modes

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode.

        Must be defined in getDisplayModes.

        Returns:
            Mode name string
        """
        return "Shaded"

    def setDisplayMode(self, mode):
        """Set the display mode.

        Map the display mode defined in attach with those defined in getDisplayModes.

        Args:
            mode: Display mode name

        Returns:
            Actual mode to use
        """
        return mode

    def onChanged(self, vobj, prop):
        """Called when a view property has changed.

        Args:
            vobj: View provider object
            prop: Property name that changed
        """
        return

    def getIcon(self):
        """Return the icon in XPM format which will appear in the tree view.

        Returns:
            Path to icon file or XPM data
        """
        return self.iconfile

    def doubleClicked(self, vobj):
        """Called when the object is double-clicked in the tree view.

        Args:
            vobj: View provider object

        Returns:
            True if handled, False otherwise
        """
        # Could open a custom dialog or switch to parameters tab
        return True

    def setupContextMenu(self, vobj, menu):
        """Setup custom context menu for the object.

        Args:
            vobj: View provider object
            menu: QMenu object to add items to
        """
        from PySide import QtGui, QtCore

        action = QtGui.QAction("Regenerate Gearbox", menu)
        action.triggered.connect(lambda: self.regenerate())
        menu.addAction(action)

    def regenerate(self):
        """Force regeneration of the gearbox."""
        if hasattr(self.Object, 'Proxy'):
            self.Object.Proxy.force_Recompute()

    def __getstate__(self):
        """Return object state for serialization.

        Returns:
            Icon file path
        """
        return self.iconfile

    def __setstate__(self, state):
        """Restore object state from serialization.

        Args:
            state: Previously saved state
        """
        if state:
            self.iconfile = state
        else:
            self.iconfile = mainIcon
        return None


#    #  App.ActiveDocument.Sketch.setDatum(constraintNr,App.Units.Quantity(str(-kwAngle)+'  deg'))
#    App.ActiveDocument.recompute()


FreeCADGui.addCommand('CycloidGearBoxCreateObject',
                      CycloidGearBoxCreateObject())
