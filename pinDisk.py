import FreeCAD as App
import cycloidFun

def QT_TRANSLATE_NOOP(scope, text):
    return text

class pindiskClass():
    def __init__(self, obj,gear_box):
        self.ShapeColor = (0.67, 0.68, 0.88)
        self.Dirty = False
        self.busy = False
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyLength", "pin_disk_pin_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).pin_disk_pin_diameter = param.pin_disk_pin_diameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyInteger", "tooth_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).tooth_count = param.tooth_count
        obj.addProperty("App::PropertyAngle", "tooth_pitch",        "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Tooth Pitch")).tooth_pitch = param.tooth_pitch
        # driver_disk
        obj.addProperty("App::PropertyLength", "base_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).base_height = param.base_height
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyLength","Diameter","CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","pin_disk")).Diameter= param.Diameter
        obj.addProperty("App::PropertyLength","Height","CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","pin_disk")).Height = param.Height
        self.Type = 'pin_disk'
        self.Object = obj
        self.gear_box = gear_box
        obj.Proxy = self

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state


    def recompute_gearbox(self, H):
        print("recomputing pin disk")
        self.Object.Shape = cycloidFun.generate_pin_base(H)

    def checkset(self, prop):
        if (hasattr(self.gear_box, 'Proxy') and hasattr(self.gear_box, prop)):
            if (getattr(self.gear_box, prop) != getattr(self.Object, prop)):
                setattr(self.gear_box, prop, getattr(self.Object, prop))
                return True
        return False
    def execute(self,obj):
        print("pindiskex",getattr(self.Object,'pin_disk_pin_diameter'))
        dirty = self.checkset('Diameter')
        dirty |= self.checkset('pin_disk_pin_diameter')
        dirty |= self.checkset('tooth_count')
        dirty |= self.checkset('tooth_pitch')
        dirty |= self.checkset('base_height')
        dirty |= self.checkset('shaft_diameter')
        dirty |= self.checkset('Height')
        print("pindiskex",getattr(self.Object,'pin_disk_pin_diameter'))
        return
        H = self.gear_box.Proxy.GetHyperParameters()
        minDia= cycloidFun.calc_min_dia(H)
        if minDia > H['Diameter']:
            print('mindia reseting')
            setattr(self, 'Diameter', minDia)
            self.checkset('Diameter')
            return
            dirty = True
        if (dirty):
            print('forcing recompute')
            self.gear_box.Proxy.force_Recompute()
        return
