import FreeCAD as App
import Part
import cycloidbox


def QT_TRANSLATE_NOOP(scope, text):
    return text


def create(obj_name):
   """
   Object creation method
   """

   obj = App.ActiveDocument.addObject('Part::FeaturePython', obj_name)

   fpo = box(obj)

   ViewProviderBox(obj.ViewObject)

   App.ActiveDocument.recompute()

   return fpo


class box():

   def __init__(self, obj):
        """
        Default Constructor
        """
        
        self.Type = 'box'
        self.ratios = None
        
        obj.addProperty('App::PropertyString', 'Description', 'Base', 'Box description').Description = 'Hello World!'
        obj.addProperty('App::PropertyLength', 'Length', 'Dimensions', 'Box length').Length = 10.0
        obj.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'Box width'). Width = '10 mm'
        obj.addProperty('App::PropertyLength', 'Height', 'Dimensions', 'Box Height').Height = '1 cm'
        obj.addProperty('App::PropertyBool', 'Aspect Ratio', 'Dimensions', 'Lock the box aspect ratio').Aspect_Ratio = False
        obj.addProperty("App::PropertyFloat","Version","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","The version of CycloidGearBox Workbench used to create this object")).Version = cycloidbox.version
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of teeth of the cycloidal disk")).ToothCount=10
        obj.addProperty("App::PropertyInteger", "LineSegmentCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of line segments to make up the cycloidal disk")).LineSegmentCount= 400
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).RollerDiameter = 0.15
        obj.addProperty("App::PropertyFloat","ToothPitch","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Tooth Pitch")).ToothPitch = 0.08
        obj.addProperty("App::PropertyFloat","Eccentricity","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Eccentricity")).Eccentricity = 0.05
        obj.addProperty("App::PropertyFloat","CenterDiameter","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Center Diameter")).CenterDiameter = -1.0
        obj.addProperty("App::PropertyFloat","PressureAngleLimit","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Limit")).PressureAngleLimit= 50.0
        obj.addProperty("App::PropertyFloat","PressureAngleOffset","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Offset")).PressureAngleOffset= 0.01
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Base Height")).BaseHeight = 10        
        self.gearBox = cycloidbox.hypoCycloidalGear()
        obj.Proxy = self        
        self.Object = obj

   def __getstate__(self):
       return self.Type

   def __setstate__(self, state):
       if state:
           self.Type = state
 
   def execute(self, obj):
       """
       Called on document recompute
       """

       obj.Shape = Part.makeBox(obj.Length, obj.Width, obj.Height) 
       #obj.Shape = Part.BSplineCurve(self.gearBox.generateCycloidalDiskArray()).toShape()


class ViewProviderBox:
   def __init__(self, obj):
       """
       Set this object to the proxy object of the actual view provider
       """
       obj.Proxy = self

   def attach(self, obj):
       """
       Setup the scene sub-graph of the view provider, this method is mandatory
       """
       return

   def updateData(self, fp, prop):
       """
       If a property of the handled feature has changed we have the chance to handle this here
       """

       return

   def getDisplayModes(self,obj):
       """
       Return a list of display modes.
       """
       return None

   def getDefaultDisplayMode(self):
       """
       Return the name of the default display mode. It must be defined in getDisplayModes.
       """
       return "Shaded"

   def setDisplayMode(self,mode):
       """
       Map the display mode defined in attach with those defined in getDisplayModes.
       Since they have the same names nothing needs to be done.
       This method is optional.
       """
       return mode

   def onChanged(self, vobj, prop):
       """
       Print the name of the property that has changed
       """

       App.Console.PrintMessage("Change property: " + str(prop) + "\n")

   def getIcon(self):
       """
       Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
       """

       return """
           /* XPM */
           static const char * ViewProviderBox_xpm[] = {
           "16 16 6 1",
           " 	c None",
           ".	c #141010",
           "+	c #615BD2",
           "@	c #C39D55",
           "#	c #000000",
           "$	c #57C355",
           "        ........",
           "   ......++..+..",
           "   .@@@@.++..++.",
           "   .@@@@.++..++.",
           "   .@@  .++++++.",
           "  ..@@  .++..++.",
           "###@@@@ .++..++.",
           "##$.@@$#.++++++.",
           "#$#$.$$$........",
           "#$$#######      ",
           "#$$#$$$$$#      ",
           "#$$#$$$$$#      ",
           "#$$#$$$$$#      ",
           " #$#$$$$$#      ",
           "  ##$$$$$#      ",
           "   #######      "};
           """

   def __getstate__(self):
       return None

   def __setstate__(self,state):
       return None
