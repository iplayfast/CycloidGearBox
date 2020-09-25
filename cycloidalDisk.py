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
        self.Type = 'CycloidalDisk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("cycloiddisk onchanged", fp, prop)
        gearbox = App.ActiveDocument.getObject("GearBoxParameters")
        cycloidal = fp.Document.getObject('cycloidal_disk')
        if prop == 'driver_disk_hole_count':
            gearbox.driver_disk_hole_count = cycloidal.driver_disk_hole_count
        if prop == 'tooth_count':
            gearbox.tooth_count = cycloidal.tooth_count

    def execute(self, obj):
        # obj.Shape = self.gear_box.generate_pin_base()
        print('cycloidgearbox execute', obj)

    def recompute_gearbox(self, H):
        print("recomputing cycloidal disk")
        self.Object.Shape = cycloidFun.generate_cycloidal_disk(H)
