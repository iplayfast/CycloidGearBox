#!/usr/bin/python

"""Hypocycloid gear boxgenerator
Code to create a hypocycloidal gearbox
https://en.wikipedia.org/wiki/Cycloidal_drive

Copyright 	2019, Chris Bruner
Version 	v0.1
License 	GPL
Homepage

Credit to:
        Alex Lait http://www.zincland.com/hypocycloid/ 
        who credits the following:
	Formulas to describe a hypocycloid cam
	http://gears.ru/transmis/zaprogramata/2.0.139.pdf

	Insperational thread on CNCzone
	http://www.cnczone.com/forums/showthread.php?t=72.02.061

	Documenting and updating the sdxf library
	http://www.kellbot.com/sdxf-python-library-for-dxf/

	Formulas for calculating the pressure angle and finding the limit circles
	http://imtuoradea.ro/auo.fmte/files-2.07/MECATRONICA_files/Anamaria_Dascalescu_1.pdf

Notes:
	Does not currently do ANY checking for sane input values and it
	is possible to create un-machinable cams, use at your own risk

	Suggestions:
	- Eccentricity should not be more than the roller radius
	- Has not been tested with negative values, may have interesting results :)
"""
from __future__ import division
import time
import getopt
import math
import sys
from PySide import QtCore,QtGui
import FreeCAD
from FreeCAD import Base
import FreeCADGui        
import Part
import Draft
import os,re
import cycloidpath_locator

smWBpath = os.path.dirname(cycloidpath_locator.__file__)
smWB_icons_path =  os.path.join( smWBpath, 'icons')
global main_CGB_Icon
main_CGB_Icon = os.path.join( smWB_icons_path , 'cycloidgearbox.svg')

__dir__ = os.path.dirname(__file__)
#iconPath = os.path.join( __dir__, 'Resources', 'icons' )
keepToolbar = False
version = 0.01


"""
def create(obj_name):
   """
#   Object creation method
"""
   print("cgb create")
   obj = App.ActiveDocument.addObject('Part::FeaturePython', obj_name)
   fpo = CycloidalGearBox(obj)
   ViewProviderCGBox(obj.ViewObject)
"""

def QT_TRANSLATE_NOOP(scope, text):
    return text
    
def toPolar(x, y):
    return (x ** 2.0 + y ** 2.0) ** 0.5, math.atan2(y, x)

def toRect(r, a):
    return r * math.cos(a), r * math.sin(a)

class hypoCycloidalGear:
    """ Create Object command"""
    def __init__(self,ToothPitch = 0.08, RollerDiameter = 0.15,RollerHeight=4, Eccentricity =
                 0.05, ToothCount = 10, LineSegmentCount = 400,
                 CenterDiameter = -1.00, PressureAngleLimit = 50.0,
                 PressureAngleOffset = 0.01, baseHeight = 2.0,DriverPinDiameter = 0.25):
        self.ToothPitch = ToothPitch
        self.RollerDiameter = RollerDiameter
        self.RollerHeight = RollerHeight
        self.Eccentricity = Eccentricity
        self.ToothCount = ToothCount
        self.LineSegmentCount = LineSegmentCount
        self.CenterDiameter = CenterDiameter
        self.PressureAngleLimit = PressureAngleLimit
        self.PressureAngleOffset = PressureAngleOffset
        self.DriverPinDiameter = DriverPinDiameter
        self.baseHeight = baseHeight
        if CenterDiameter > 0:
            self.ToothPitch = CenterDiameter / ToothCount
        self.minmaxRadius();



    def calcyp(self,a):
        return math.atan(math.sin(self.ToothCount * a) /
                         (math.cos(self.ToothCount * a) +
                          (self.ToothCount * self.ToothPitch) /
                          (self.Eccentricity * (self.ToothCount + 1))))

    def calcX(self,a):
        return (self.ToothCount * self.ToothPitch) * math.cos(a) + \
            self.Eccentricity * math.cos((self.ToothCount + 1) * a) -    \
            float(self.RollerDiameter) / 2.0 * math.cos(self.calcyp(a) + a)

    def calcY(self,a):
        return (self.ToothCount * self.ToothPitch) * math.sin(a) +   \
            self.Eccentricity * math.sin((self.ToothCount + 1) * a) -    \
                float(self.RollerDiameter) / 2.0 * math.sin(self.calcyp(a) + a)

    def clean1(self,a):
        """ return -1 < a < 1 """
        return min(1, max(a, -1))

    def calcPressureAngle(self, angle):
        """ calculate the angle of the cycloidalDisk teeth at the angle """
        ex = 2.0 ** 0.5
        r3 = self.ToothPitch * self.ToothCount 
#        p * n
        rg = r3 / ex
        pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - float(self.RollerDiameter) / 2.0
        ppd2 = pp + float(self.RollerDiameter) / 2.0
        r3cos = r3 * math.cos(angle) - rg
        return math.asin(self.clean1(((r3 * math.cos(angle) - rg) / (pp + float(self.RollerDiameter) / 2.0)))) * 180 / math.pi

    def calcPressureLimit(self,a):
        ex = 2.0 ** 0.5
        r3 = self.ToothPitch * self.ToothCount
        rg = r3 / ex
        q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
        x = rg - self.Eccentricity + (q - float(self.RollerDiameter) / 2.0) * (r3 * math.cos(a) - rg) / q
        y = (q - float(self.RollerDiameter) / 2.0) * r3 * math.sin(a) / q
        return (x ** 2.0 + y ** 2.0) ** 0.5

    def checkLimit(self,v,maxrad,minrad):
        """ if x,y outside limit return x,y as at limit, else return x,y """
        r, a = toPolar(v.x, v.y)
        if (r > maxrad) or (r < minrad):
            r = r - self.PressureAngleOffset
            v.x, v.y = toRect(r, a)
        return v



    def minmaxRadius(self):
        """ Find the pressure angle limit circles """
        minAngle = -1.0
        maxAngle = -1.0
        for i in range(0, 180):
            x = self.calcPressureAngle(float(i)*math.pi / 180)
            if (x < self.PressureAngleLimit) and (minAngle < 0):
                minAngle = float(i)
            if (x < -self.PressureAngleLimit) and (maxAngle < 0):
                maxAngle = float(i - 1)
        self.minRadius = self.calcPressureLimit(minAngle * math.pi / 180)
        self.maxRadius = self.calcPressureLimit(maxAngle * math.pi / 180)

    def generatePinBase(self):
        """ create the base that the fixedRingPins will be attached to """        
        pinBase = Part.makeCylinder(self.maxRadius+float(self.RollerDiameter),self.baseHeight);
        # generate the pin locations
        for i in range(0, self.ToothCount + 1):
            x = self.ToothPitch * self.ToothCount * math.cos(2.0 * math.pi /
                                                           (self.ToothCount + 1) * i)
            y = self.ToothPitch * self.ToothCount * math.sin(2.0 * math.pi /
                                                           (self.ToothCount + 1) * i)
            fixedRingPin = Part.makeCylinder(float(self.RollerDiameter)/2.0,self.RollerHeight,Base.Vector(x,y,0))
            pinBase = pinBase.fuse(fixedRingPin)
        accesshole = Part.makeCylinder(self.DriverPinDiameter/2.0,10000);
        pinBase.cut(accesshole);
        return pinBase

    def generateEccentricShaft(self):
    # add a circle in the center of the cam
        eccentricShaft = Part.makeCylinder(float(self.RollerDiameter) / 2.0,self.RollerHeight,Base.Vector(-self.Eccentricity,0,0))
        return eccentricShaft

    def points(self, num=10):
        pts = self.involute_points(num=num)
        rot = rotation3D(-pi / self.z / 2.0)
        pts = rot(pts)
        ref = reflection3D(pi / 2.0)
        pts1 = ref(pts)[::-1]
        rot = rotation3D(2.0 * pi / self.z)
        if self.add_foot:
            return (array([
                array([pts[0], pts[1]]),
                pts[1:],
                array([pts[-1], pts1[0]]),
                pts1[:-1],
                array([pts1[-2.0], pts1[-1]])
            ]))
        else:
            return (array([pts, array([pts[-1], pts1[0]]), pts1]))
        
    def generateCycloidalDiskArray(self):
        """ make the array to be used in the bspline 
            that is the cycloidalDisk
        """
        self.minmaxRadius()
        q = 2.0 * math.pi / float(self.LineSegmentCount)
        i = 0

        v1 = Base.Vector(self.calcX(q*i),self.calcY(q*i),0)
        v1 = self.checkLimit(v1,self.maxRadius,self.minRadius)

        cycloidalDiskArray = []
        cycloidalDiskArray.append(v1)
        for i in range(0, self.LineSegmentCount):
            v2 = Base.Vector(self.calcX(q*(i+1)),self.calcY(q*(i+1)),0)
            v2 = self.checkLimit(v2,self.maxRadius,self.minRadius)
            cycloidalDiskArray.append(v2)
        return cycloidalDiskArray
    
    def generateCycloidalDisk(self):
        """
        make the complete cycloidal disk
        """
        a = Part.BSplineCurve(self.generateCycloidalDiskArray()).toShape()
        w = Part.Wire([a])
        f = Part.Face(w)
        e = f.extrude(FreeCAD.Vector(0,0,self.RollerHeight/2))
        e.translate(Base.Vector(-self.Eccentricity, 0, self.baseHeight+0.1))
        return e
        
    def _update(self):
        self.__init__(ToothPitch = self.ToothPitch,
                      RollerDiameter=self.RollerDiameter,
                      RollerHeight = self.RollerHeight,
                      Eccentricity=self.Eccentricity,
                      ToothCount=self.ToothCount,
                      LineSegmentCount=self.LineSegmentCount,
                      CenterDiameter=self.CenterDiameter,
                      PressureAngleLimit=self.PressureAngleLimit,
                      PressureAngleOffset=self.PressureAngleOffset,
                      DriverPinDiameter=self.DriverPinDiameter)



class CycloidGearBoxCreateObject():
    def GetResources(self):
        print(os.path.join( 'icons','cycloidgearbox.svg'))
        return {'Pixmap' : main_CGB_Icon,             
            'MenuText': "&Create hypoCycloidalGear", 
            'ToolTip' : "Create default gearbox" }
    
    def __init__(self):
        pass
        
        #ViewProviderBox(a.ViewObject)
    def Activated(self):            
        print("cycloidbox Activated")
        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument()
        doc = FreeCAD.ActiveDocument
        gbobj=doc.addObject("Part::FeaturePython","GearBox")   
        cbg = CycloidalGearBox(gbobj,doc)          
        ViewProviderCGBox(gbobj.ViewObject)
        #Part.show(cbg.Shape)
        Part.show(cbg.pinobj.Shape)
        Part.show(cbg.cycdiskobj.Shape)
        Part.show(cbg.esobj.Shape)
        
        
        
    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        print ("CycloidalGearBox.Deactivated()\n") 

    def execute(self, obj):
        print('cycloidgearboxCreateObject execute')
        

class   CycloidalGearBox():
    def __init__(self, obj,doc):        
        print("CycloidalGearBox __init__")       
        obj.addProperty("App::PropertyFloat","Version","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","The version of CycloidGearBox Workbench used to create this object")).Version = version
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of teeth of the cycloidal disk")).ToothCount=10
        obj.addProperty("App::PropertyInteger", "LineSegmentCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of line segments to make up the cycloidal disk")).LineSegmentCount= 400
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).RollerDiameter = 0.15
        obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = 4.0        
        obj.addProperty("App::PropertyFloat", "ToothPitch","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Tooth Pitch")).ToothPitch = 0.08
        obj.addProperty("App::PropertyFloat", "Eccentricity","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Eccentricity")).Eccentricity = 0.05
        obj.addProperty("App::PropertyFloat", "CenterDiameter","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Center Diameter")).CenterDiameter = -1.0
        obj.addProperty("App::PropertyFloat", "PressureAngleLimit","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Limit")).PressureAngleLimit= 50.0
        obj.addProperty("App::PropertyFloat", "PressureAngleOffset","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Offset")).PressureAngleOffset= 0.01        
        obj.addProperty("App::PropertyFloat", "BaseHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Base Height")).BaseHeight = 2.0
        obj.addProperty("App::PropertyFloat", "DriverPinDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Driver Pin Diameter")).DriverPinDiameter = 0.25
        self.pinobj = doc.addObject("Part::FeaturePython", "PinBase")
        self.cycdiskobj = doc.addObject("Part::FeaturePython", "cycloidalDisk")
        self.esobj  = doc.addObject("Part::FeaturePython", "EccentricShaft")
        
        print("Properties added")
        obj.Proxy = self    
        self.Object = obj
        self.onChanged(obj,"refresh")         
        print('gearbox created')
       
    def parameterization(self, pts, a,  closed):
        print("parameterization")
        return 0
        
    def makePoints(selfself, obj):
        print("makepoints")
        return []

    def Activated(self):            
        print ("Cycloidal.Activated()\n")               
            
        
    
    def onChanged(self, fp, prop):
        print("onchanged", fp, prop)        
        self.gearBox = hypoCycloidalGear()
        self.gearBox.ToothCount = fp.getPropertyByName("ToothCount")
        self.gearBox.LineSegmentCount = fp.getPropertyByName("LineSegmentCount")
        self.gearBox.RollerDiameter = fp.getPropertyByName("RollerDiameter")
        self.gearBox.RollerHeight = fp.getPropertyByName("RollerHeight")
        self.gearBox.ToothPitch = fp.getPropertyByName("ToothPitch")
        self.gearBox.Eccentricity = fp.getPropertyByName("Eccentricity")
        self.gearBox.CenterDiameter = fp.getPropertyByName("CenterDiameter")
        self.gearBox.PressureAngleLimit = fp.getPropertyByName("PressureAngleLimit")
        self.gearBox.BaseHeight = fp.getPropertyByName("BaseHeight")
        self.gearBox.DriverPinDiameter = fp.getPropertyByName("DriverPinDiameter")
        print("done onChanged")
        
    def execute(self, obj):
        print('cycloidgearbox execute',obj)
        #print("creating pinbase")
        self.pinobj.Shape = self.gearBox.generatePinBase()
        #print("creating cycloidaldisk")
        self.cycdiskobj.Shape = self.gearBox.generateCycloidalDisk()
        #print("creating eccentricshaft")
        self.esobj.Shape = self.gearBox.generateEccentricShaft()

        

class ViewProviderCGBox:
   def __init__(self, obj):
       """
       Set this object to the proxy object of the actual view provider
       """
       print("ViewProviderCGBox init start")
       print(self)
       print(obj)
       obj.Proxy = self
       self.part = obj
       print("ViewProviderCGBox init end")
       

   def attach(self, obj):
       """
       Setup the scene sub-graph of the view provider, this method is mandatory
       """       
       return

   def updateData(self, fp, prop):
       """
       If a property of the handled feature has changed we have the chance to handle this here
       """
       #print("viewProviderCGBox updateData",fp,prop)
       return

   def getDisplayModes(self,obj):
       """
       Return a list of display modes.
       """
       modes=[]
       modes.append("Shaded")
       modes.append("Wireframe")
       return modes

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
       print("viewProviderCGBox setDisplayMode",mode)
       return mode

   def onChanged(self, vobj, prop):
       """
       Print the name of the property that has changed
       """
       print("viewProviderCGBox onChanged",vobj,prop)

   def getIcon(self):
       """
       Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
       """

       return main_CGB_Icon
       """
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
       print("__setstate__",state)
       return None


FreeCADGui.addCommand('CycloidGearBoxCreateObject',CycloidGearBoxCreateObject())
    
