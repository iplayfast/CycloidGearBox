import FreeCAD as App
import cycloidFun

def QT_TRANSLATE_NOOP(scope, text):
    return text

class cycdiskClass():
    def __init__(self, obj, gear_box):
        self.Object = obj
        obj.Proxy = self
        # obj.addProperty("App::PropertyString", "Parent","Parameter","Parent").Parent = App.ActiveDocument.GearBoxParameters
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "driver_disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).driver_disk_hole_count = param.driver_disk_hole_count
        obj.addProperty("App::PropertyInteger", "tooth_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).tooth_count = param.tooth_count
        self.gear_box = gear_box
        self.ShapeColor = (0.12, 0.02, 0.63)
        self.sketch = 0
        self.Type = 'CycloidalDisk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
            
    def assign_sketch(self, sobj):
        self.sketch = sobj

    def execute(self,obj):
        self.checkset('driver_disk_hole_count')
        self.checkset('tooth_count')
        #    self.gear_box.Proxy.force_Recompute()

    def checkset(self, prop):
        if (hasattr(self.gear_box,'Proxy') and hasattr(self.gear_box, prop)):
            if (getattr(self.gear_box, prop) != getattr(self.Object, prop)):
                setattr(self.gear_box, prop, getattr(self.Object, prop))
                return True
        return False

    def recompute_gearbox(self, H):
        self.Object.Shape = cycloidFun.generate_cycloidal_disk(H)
        if (self.sketch!=0):
            cycloidFun.generate_cycloidal_disk_sketch(H,self.sketch)