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
        param = App.ActiveDocument.getObject("GearBoxParameters")
        obj.addProperty("App::PropertyInteger", "disk_hole_count", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("APP::Property", "Number of driving holes of the cycloid disk")).disk_hole_count = param.disk_hole_count
        obj.addProperty("App::PropertyLength", "shaft_diameter", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Shaft Diameter")).shaft_diameter = param.shaft_diameter
        obj.addProperty("App::PropertyLength", "slot_height", "CycloidGearBox",
                        QT_TRANSLATE_NOOP("App::Property", "Slot Height")).slot_height = param.slot_height
        self.Type = 'output_shaft'

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        gear_box_parameters = App.ActiveDocument.getObject("GearBoxParameters")
        output_shaft = fp.Document.getObject("output_shaft")
        if prop == "disk_hole_count":
            gear_box_parameters.disk_hole_count = output_shaft.disk_hole_count
        if prop == 'shaft_diameter':
            gear_box_parameters.shaft_diameter = output_shaft.shaft_diameter
        if prop == 'slot_height':
            gear_box_parameters.slot_height = output_shaft.slot_height

    def recompute_gearbox(self, H):
        print("recomputing output shaft")
        self.Object.Shape = cycloidFun.generate_output_shaft(H)
        print("done recomputing output shaft")
