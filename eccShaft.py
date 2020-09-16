import FreeCAD as App
import cycloidFun

def QT_TRANSLATE_NOOP(scope, text):
    return text

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
