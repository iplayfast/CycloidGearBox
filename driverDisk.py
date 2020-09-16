import FreeCAD as App
import cycloidFun

def QT_TRANSLATE_NOOP(scope, text):
    return text

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
        obj.addProperty("App::PropertyLength","driver_disk_diameter","CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","Diameter")).driver_disk_diameter = param.driver_disk_diameter
        self.Type = 'pin_disk'
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
