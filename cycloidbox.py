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
    # Preset configurations for common gearbox sizes
    PRESETS = {
        'Small_10to1': {
            'tooth_count': 10, 'Diameter': 70, 'roller_diameter': 6.0,
            'roller_circle_diameter': 50, 'base_height': 8.0, 'disk_height': 4.0,
            'shaft_diameter': 10.0, 'eccentricity': 1.5,
            'driver_circle_diameter': 30.0, 'driver_disk_hole_count': 4,
            'driver_hole_diameter': 6.0,
        },
        'Medium_20to1': {
            'tooth_count': 20, 'Diameter': 120, 'roller_diameter': 8.0,
            'roller_circle_diameter': 90, 'base_height': 12.0, 'disk_height': 6.0,
            'shaft_diameter': 15.0, 'eccentricity': 2.0,
            'driver_circle_diameter': 50.0, 'driver_disk_hole_count': 6,
            'driver_hole_diameter': 8.0,
        },
        'Large_40to1': {
            'tooth_count': 40, 'Diameter': 200, 'roller_diameter': 10.0,
            'roller_circle_diameter': 150, 'base_height': 15.0, 'disk_height': 8.0,
            'shaft_diameter': 20.0, 'eccentricity': 2.5,
            'driver_circle_diameter': 80.0, 'driver_disk_hole_count': 8,
            'driver_hole_diameter': 10.0,
        },
    }

    # Mapping of parameters to parts they affect (for smart regeneration)
    PARAM_TO_PARTS = {
        'tooth_count': ['pinDisk', 'cycloidalDisk1', 'cycloidalDisk2'],
        'roller_diameter': ['pinDisk', 'cycloidalDisk1', 'cycloidalDisk2'],
        'roller_circle_diameter': ['pinDisk', 'cycloidalDisk1', 'cycloidalDisk2'],
        'pressure_angle_limit': ['cycloidalDisk1', 'cycloidalDisk2'],
        'pressure_angle_offset': ['cycloidalDisk1', 'cycloidalDisk2'],
        'line_segment_count': ['cycloidalDisk1', 'cycloidalDisk2'],
        'tooth_pitch': ['cycloidalDisk1', 'cycloidalDisk2'],

        'shaft_diameter': ['pinDisk', 'driverDisk', 'inputShaft', 'cycloidalDisk1', 'cycloidalDisk2', 'eccentricKey', 'outputShaft'],
        'eccentricity': ['driverDisk', 'inputShaft', 'cycloidalDisk1', 'cycloidalDisk2', 'eccentricKey'],

        'driver_circle_diameter': ['pinDisk', 'driverDisk', 'cycloidalDisk1', 'cycloidalDisk2', 'outputShaft'],
        'driver_disk_hole_count': ['driverDisk', 'cycloidalDisk1', 'cycloidalDisk2', 'outputShaft'],
        'driver_hole_diameter': ['driverDisk', 'cycloidalDisk1', 'cycloidalDisk2', 'outputShaft'],

        'base_height': ['pinDisk', 'inputShaft', 'eccentricKey', 'outputShaft'],
        'disk_height': ['pinDisk', 'driverDisk', 'inputShaft', 'cycloidalDisk1', 'cycloidalDisk2', 'eccentricKey', 'outputShaft'],

        'key_diameter': ['inputShaft', 'eccentricKey', 'outputShaft'],
        'key_flat_diameter': ['inputShaft', 'eccentricKey', 'outputShaft'],

        'Diameter': ['pinDisk'],
        'Height': ['inputShaft'],
        'clearance': ['pinDisk', 'driverDisk', 'inputShaft', 'cycloidalDisk1', 'cycloidalDisk2', 'outputShaft'],
    }

    def __init__(self, obj):
        self.Dirty = False
        self.changed_properties = set()  # Track which properties changed
        self.validation_warnings = []

        H = cycloidFun.generate_default_parameters()

        # Read-only properties
        obj.addProperty("App::PropertyString", "Version", "0_Info", QT_TRANSLATE_NOOP(
            "App::Property", "Workbench version"), 1).Version = version
        obj.addProperty("App::PropertyString", "ValidationWarnings", "0_Info", QT_TRANSLATE_NOOP(
            "App::Property", "Parameter validation warnings"), 1).ValidationWarnings = ""
        obj.addProperty("App::PropertyLength", "Min_Diameter", "0_Info",
            QT_TRANSLATE_NOOP("App::Property", "Minimum diameter (pressure angle limit)"), 1)
        obj.addProperty("App::PropertyLength", "Max_Diameter", "0_Info",
            QT_TRANSLATE_NOOP("App::Property", "Maximum diameter (pressure angle limit)"), 1)

        # 1. Roller Assembly (Pin Disk)
        obj.addProperty("App::PropertyLength", "roller_diameter", "1_Roller_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Diameter of roller pins")).roller_diameter = H["roller_diameter"]
        obj.addProperty("App::PropertyLength", "roller_circle_diameter", "1_Roller_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Circle diameter where rollers are positioned")).roller_circle_diameter = H["roller_circle_diameter"]
        obj.addProperty("App::PropertyInteger", "tooth_count", "1_Roller_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Number of cycloidal teeth (gear ratio = 1/tooth_count)")).tooth_count = H["tooth_count"]
        obj.addProperty("App::PropertyAngle", "tooth_pitch", "1_Roller_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Pitch between teeth")).tooth_pitch = H["tooth_pitch"]
        obj.addProperty("App::PropertyLength", "base_height", "1_Roller_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Height of base plate")).base_height = H["base_height"]
        obj.addProperty("App::PropertyLength", "Diameter", "1_Roller_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Outer diameter of gearbox")).Diameter = H["Diameter"]

        # 2. Drive System
        obj.addProperty("App::PropertyLength", "driver_circle_diameter", "2_Drive_System", QT_TRANSLATE_NOOP(
            "App::Property", "Circle diameter for driver pins")).driver_circle_diameter = H["driver_circle_diameter"]
        obj.addProperty("App::PropertyInteger", "driver_disk_hole_count", "2_Drive_System", QT_TRANSLATE_NOOP(
            "App::Property", "Number of driver pins")).driver_disk_hole_count = H["driver_disk_hole_count"]
        obj.addProperty("App::PropertyLength", "driver_hole_diameter", "2_Drive_System", QT_TRANSLATE_NOOP(
            "App::Property", "Diameter of driver pin holes")).driver_hole_diameter = H["driver_hole_diameter"]
        obj.addProperty("App::PropertyLength", "disk_height", "2_Drive_System", QT_TRANSLATE_NOOP(
            "App::Property", "Height of cycloidal disks and driver disk")).disk_height = H["disk_height"]

        # 3. Shaft Assembly
        obj.addProperty("App::PropertyLength", "shaft_diameter", "3_Shaft_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Diameter of input/output shafts")).shaft_diameter = H["shaft_diameter"]
        obj.addProperty("App::PropertyLength", "eccentricity", "3_Shaft_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Eccentricity of input shaft (determines output wobble)")).eccentricity = H["eccentricity"]
        obj.addProperty("App::PropertyLength", "key_diameter", "3_Shaft_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Diameter of shaft key")).key_diameter = H["key_diameter"]
        obj.addProperty("App::PropertyLength", "key_flat_diameter", "3_Shaft_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Flat diameter of shaft key")).key_flat_diameter = H["key_flat_diameter"]
        obj.addProperty("App::PropertyLength", "Height", "3_Shaft_Assembly", QT_TRANSLATE_NOOP(
            "App::Property", "Total height of gearbox")).Height = H["Height"]

        # 4. Advanced Settings
        obj.addProperty("App::PropertyInteger", "line_segment_count", "4_Advanced", QT_TRANSLATE_NOOP(
            "App::Property", "Number of line segments for cycloidal disk curve (higher = smoother)")).line_segment_count = H["line_segment_count"]
        obj.addProperty("App::PropertyLength", "pressure_angle_limit", "4_Advanced", QT_TRANSLATE_NOOP(
            "App::Property", "Maximum pressure angle (degrees) - affects min/max diameters")).pressure_angle_limit = H["pressure_angle_limit"]
        obj.addProperty("App::PropertyAngle", "pressure_angle_offset", "4_Advanced", QT_TRANSLATE_NOOP(
            "App::Property", "Pressure angle offset for fine-tuning")).pressure_angle_offset = H["pressure_angle_offset"]
        obj.addProperty("App::PropertyLength", "clearance", "4_Advanced", QT_TRANSLATE_NOOP(
            "App::Property", "Clearance between parts (for manufacturing)")).clearance = H["clearance"]

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
        # Track which property changed for smart regeneration
        if prop in self.PARAM_TO_PARTS:
            self.changed_properties.add(prop)        

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

    def validate_and_warn(self, parameters):
        """Validate parameters and generate user-friendly warnings.

        Args:
            parameters: Dictionary of gearbox parameters

        Returns:
            List of warning strings
        """
        warnings = []

        # Check eccentricity vs roller diameter
        if parameters['eccentricity'] > parameters['roller_diameter'] / 2:
            warnings.append("⚠ Eccentricity > roller radius - may cause manufacturing issues")

        # Check if driver circle fits
        min_rad = parameters.get('min_rad', 0)
        if min_rad > 0 and parameters['driver_circle_diameter'] > min_rad * 2 - parameters['roller_diameter']:
            warnings.append("⚠ Driver circle may interfere with rollers")

        # Check tooth count for reasonable ratio
        tooth_count = parameters['tooth_count']
        if tooth_count < 5:
            warnings.append("ℹ Very low tooth count - gear ratio 1:{} may be impractical".format(tooth_count))
        elif tooth_count > 30:
            warnings.append("ℹ High tooth count - manufacturing may be difficult")

        # Check clearance
        if parameters['clearance'] < 0.1:
            warnings.append("⚠ Very small clearance - parts may bind")
        elif parameters['clearance'] > 2.0:
            warnings.append("ℹ Large clearance - may cause backlash")

        # Check if outer diameter is sufficient
        if parameters['Diameter'] <= parameters['roller_circle_diameter']:
            warnings.append("⚠ Outer diameter too small for roller circle")

        return warnings

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
                parameters = self.GetParameters()

                # Validate and show warnings
                warnings = self.validate_and_warn(parameters)
                if warnings:
                    warning_text = '\n'.join(warnings)
                    self.Object.ValidationWarnings = warning_text
                    # Also print to console for visibility
                    App.Console.PrintWarning("Gearbox Parameter Warnings:\n")
                    for warning in warnings:
                        App.Console.PrintWarning(f"  {warning}\n")
                else:
                    self.Object.ValidationWarnings = "✓ All parameters OK"

                # Generate parts
                cycloidFun.generate_parts(App.ActiveDocument, parameters)

                # Clear changed properties tracking after successful generation
                self.changed_properties.clear()

                self.Dirty = False
                App.ActiveDocument.recompute()

            except cycloidFun.ParameterValidationError as e:
                # Show error to user in FreeCAD console
                App.Console.PrintError(f"Cycloidal Gearbox Parameter Error: {str(e)}\n")
                App.Console.PrintError("Please adjust the parameters and try again.\n")
                self.Object.ValidationWarnings = f"❌ ERROR: {str(e)}"
                raise
            except ValueError as e:
                App.Console.PrintError(f"Cycloidal Gearbox Math Error: {str(e)}\n")
                App.Console.PrintError("The current parameters may cause mathematical issues.\n")
                self.Object.ValidationWarnings = f"❌ ERROR: {str(e)}"
                raise
            except Exception as e:
                App.Console.PrintError(f"Cycloidal Gearbox Error: {str(e)}\n")
                import traceback
                App.Console.PrintError(traceback.format_exc())
                self.Object.ValidationWarnings = f"❌ ERROR: {str(e)}"
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
