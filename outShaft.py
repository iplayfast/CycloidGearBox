import FreeCAD as App
import cycloidFun

def QT_TRANSLATE_NOOP(scope, text):
    return text

class OutShaft():
    def __init__(self, obj, gear_box):
        self.Object = obj
        self.gear_box = gear_box
        obj.Proxy = self
        self.Type = 'Output Shaft'
        self.sketch = 0
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "driver_disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).driver_disk_hole_count = param.driver_disk_hole_count
        obj.addProperty("App::PropertyLength", "driver_hole_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Diameter of driving holes")).driver_hole_diameter = param.driver_hole_diameter
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyLength", "Height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Slot Height")).Height = param.Height
        self.Type = 'output_shaft'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
            
    def assign_sketch(self, sobj):
        self.sketch = sobj

    def execute(self, obj):
        self.checkset('driver_disk_hole_count')
        self.checkset('driver_hole_diameter')
        self.checkset('Height')
        self.checkset('shaft_diameter')
        #    self.gear_box.Proxy.force_Recompute()

    def checkset(self, prop):
        if (self.gear_box and hasattr(self.gear_box, 'Proxy') and hasattr(self.gear_box, prop)):
            if (getattr(self.gear_box, prop) != getattr(self.Object, prop)):
                setattr(self.gear_box, prop, getattr(self.Object, prop))
                return True
        return False

    def recompute_gearbox(self, H):
        self.Object.Shape = cycloidFun.generate_output_shaft(H)
        if (self.sketch!=0):
            cycloidFun.generate_output_shaft_sketch(H,self.sketch)

