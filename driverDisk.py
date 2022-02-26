import FreeCAD as App
import cycloidFun

def QT_TRANSLATE_NOOP(scope, text):
    return text

class driver_diskClass():
    def __init__(self, obj, gear_box):
        self.Object = obj
        obj.Proxy = self
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "driver_disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).driver_disk_hole_count = param.driver_disk_hole_count
        obj.addProperty("App::PropertyLength", "eccentricity", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "eccentricity")).eccentricity = param.eccentricity
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        self.Type = 'pin_disk'
        self.Type = 'driver_disk'
        self.gear_box = gear_box
        self.sketch = 0

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
    
    def assign_sketch(self, sobj):
        self.sketch = sobj

    def execute(self, obj):
        self.checkset('driver_disk_hole_count')
        self.checkset('eccentricity')
        self.checkset('shaft_diameter')
        #self.gear_box.Object.force_Recompute()

    def checkset(self, prop):
        if (hasattr(self.gear_box, 'Proxy') and hasattr(self.gear_box, prop)):
            if (getattr(self.gear_box, prop) != getattr(self.Object, prop)):
                print('setting gearbox prop')
                setattr(self.gear_box, prop, getattr(self.Object, prop))
                return True
        return False

    def recompute_gearbox(self, H):
        self.Object.Shape = cycloidFun.generate_driver_disk(H)
        if (self.sketch!=0):
            cycloidFun.generate_driver_disk_sketch(H,self.sketch)
