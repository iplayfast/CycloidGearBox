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
        obj.addProperty("App::PropertyLength", "pin_disk_pin_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter of the rollers")).pin_disk_pin_diameter = param.pin_disk_pin_diameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyLength", "base_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).base_height = param.base_height
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyLength", "Height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Slot Height")).Height = param.Height

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def execute(self,obj):
        print("eccshart start", float(self.Object.__getattribute__("pin_disk_pin_diameter").Value))
        self.checkset('eccentricity')
        self.checkset('pin_disk_pin_diameter')
        self.checkset('base_height')
        self.checkset('shaft_diameter')
        self.checkset('Height')
        print("eccshart ex ", float(self.Object.__getattribute__("pin_disk_pin_diameter").Value))
        #    self.gear_box.Proxy.force_Recompute()

    def checkset(self, prop):
        if (hasattr(self.gear_box, 'Proxy') and hasattr(self.gear_box, prop)):
            if (getattr(self.gear_box, prop) != getattr(self.Object, prop)):
                print("eccshar chset ",prop, float(self.Object.__getattribute__("pin_disk_pin_diameter").Value))
                setattr(self.gear_box, prop, getattr(self.Object, prop))
                return True
        return False

    def recompute_gearbox(self, H):
        print("recomputing Eccentric Shaft")
        self.Object.Shape = cycloidFun.generate_eccentric_shaft(H)
