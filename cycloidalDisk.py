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
        obj.addProperty("App::PropertyInteger", "disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).disk_hole_count = param.disk_hole_count
        obj.addProperty("App::PropertyInteger", "tooth_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).tooth_count = param.tooth_count
        obj.addProperty("App::PropertyLength", "cycloidal_disk_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "Cycloidal Disk Height")).cycloidal_disk_height = param.cycloidal_disk_height
        self.gear_box = gear_box
        self.ShapeColor = (0.12, 0.02, 0.63)
        self.Type = 'CyclockalDisk'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        print("cycloiddisk onchanged", fp, prop)
        p = App.ActiveDocument.getObject("GearBoxParameters")
        s = fp.Document.getObject('cycloidal_disk')
        if prop == 'disk_hole_count':
            p.disk_hole_count = s.disk_hole_count
        if prop == 'cycloidal_disk_height':
            p.cycloidal_disk_height = s.cycloidal_disk_height
        if prop == 'tooth_count':
            p.tooth_count = s.tooth_count

    def execute(self, obj):
        # obj.Shape = self.gear_box.generate_pin_base()
        print('cycloidgearbox execute', obj)

    def recompute_gearbox(self, H):
        print("recomputing cycloidal disk")
        self.Object.Shape = cycloidFun.generate_cycloidal_disk(H)
