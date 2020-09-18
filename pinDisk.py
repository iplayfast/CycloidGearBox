import FreeCAD as App
import cycloidFun

def QT_TRANSLATE_NOOP(scope, text):
    return text

class pindiskClass():
    def __init__(self, obj, gear_box):
        self.ShapeColor = (0.67, 0.68, 0.88)
        print("Adding parameters")
        param = App.ActiveDocument.getObject("GearBoxParameters")
        #print(param.roller_diameter)
        obj.addProperty("App::PropertyLength", "roller_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).roller_diameter = param.roller_diameter
        # obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyInteger", "tooth_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Number of teeth of the cycloidal disk")).tooth_count = param.tooth_count
        obj.addProperty("App::PropertyLength", "base_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Base Height")).base_height = param.base_height
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyLength","pin_disk_diameter","CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property","pin_disk")).pin_disk_diameter= param.pin_disk_diameter
        self.Type = 'pin_disk'
        self.Object = obj
        self.gear_box = gear_box
        obj.Proxy = self
        print("Done Adding parameters")

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        # App.ActiveDocument.getObject("GearBoxParameters").onChanged(fp,prop)
        pin_disk = fp.Document.getObject('pin_disk')
        gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
        if prop == 'Proxy':
            pass
        if prop == 'tooth_count':
            gear_box_parameters.tooth_count = pin_disk.tooth_count
        if prop == 'pin_disk_diameter':
            gear_box_parameters.pin_disk_diameter = pin_disk.pin_disk_diameter
            print(pin_disk.pin_disk_diameter)
            print(gear_box_parameters.pin_disk_diameter)

        if prop == 'roller_diameter':
            gear_box_parameters.roller_diameter = pin_disk.roller_diameter
        # if prop=='RollerHeight':
        #    gear_box_parameters.RollerHeight = pin_disk.RollerHeight
        if prop == 'base_height':
            gear_box_parameters.base_height = pin_disk.base_height
        if prop == 'shaft_diameter':
            gear_box_parameters.shaft_diameter = pin_disk.shaft_diameter
        gear_box_parameters.recompute()

    def recompute_gearbox(self, H):
        print("recomputing pin disk", H)
        self.Object.Shape = cycloidFun.generate_pin_base(H)
        min_radius,max_radius = cycloidFun.calculate_min_max_radii(H)
        gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
        gear_box_parameters.Min_Diameter = min_radius*2
        gear_box_parameters.Max_Diameter = max_radius*2
        # self.gear_box_parameters.gear_box_parameters.generate_pin_base()
