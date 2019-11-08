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

import os

import FreeCADGui
import FreeCAD as App
import cycloidFun
import cycloidpath_locator

smWBpath = os.path.dirname(cycloidpath_locator.__file__)
smWB_icons_path =  os.path.join( smWBpath, 'icons')
global main_Icon
main_Icon = os.path.join( smWB_icons_path , 'cycloidgearbox.svg')
global pin_Icon
pin_Icon = os.path.join(smWB_icons_path,'cycloidpin.svg')
__dir__ = os.path.dirname(__file__)
global eccentric_Icon
eccentric_Icon = os.path.join(smWB_icons_path,'eccentric.svg')
#iconPath = os.path.join( __dir__, 'Resources', 'icons' )
keepToolbar = False
version = 0.01

def QT_TRANSLATE_NOOP(scope, text):
    return text

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


class CycloidGearBoxCreateObject():
    """
    The part that holds the parameters used to make the phsyical parts
    """
    def GetResources(self):
        print(os.path.join( 'icons','cycloidgearbox.svg'))
        return {'Pixmap' : main_Icon,             
            'MenuText': "&Create hypoCycloidalGear", 
            'ToolTip' : "Create default gearbox" }
    
    def __init__(self):
        pass
        
        #ViewProviderBox(a.ViewObject)
    def Activated(self):            
        print("cycloidbox Activated")
        if not App.ActiveDocument:
            App.newDocument()
        doc = App.ActiveDocument
        """# test code
        sketch = doc.Body.newObject('Sketcher::SketchObject','Sketch') 
        sketch.Support = (App.activeDocument().XY_Plane, [''])
        sketch.MapMode = 'FlatFace'
        """
        obj=doc.addObject("Part::FeaturePython","GearBox Parameters")   
        gearbox = CycloidalGearBox(obj)

        pindiskobj = doc.addObject("Part::FeaturePython","pinDisk")
        pindisk = pindiskClass(pindiskobj,gearbox)
        pindiskobj.Proxy= pindisk
        gearbox.recomputeList.append(pindisk)
        ViewProviderCGBox(pindiskobj.ViewObject,pin_Icon)
        
        cycdiskobj = doc.addObject("Part::FeaturePython","CycloidalDisk")        
        cycdisk = cycdiskClass(cycdiskobj,gearbox)
        cycdiskobj.Proxy = cycdisk
        gearbox.recomputeList.append(cycdisk)
        ViewProviderCGBox(cycdiskobj.ViewObject, main_Icon)
        
        
        esobj = doc.addObject("Part::FeaturePython","EccentricShaft")
        escShaft = EccShaft(esobj,gearbox)
        esobj.Proxy = esobj
        gearbox.recomputeList.append(escShaft)
        ViewProviderCGBox(esobj.ViewObject,eccentric_Icon)
        
        gearbox.onChanged('','Refresh')
        gearbox.recompute()
        doc.recompute()
        gearbox.recompute()
        return gearbox
        
        
    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        print ("CycloidalGearBox.Deactivated()\n") 

    def execute(self, obj):
        print('cycloidgearboxCreateObject execute')


class   pindiskClass():
    def __init__(self,obj,cgb):
        self.Object = obj
        self.cgb = cgb
        obj.Proxy = self        
        self.ShapeColor=(0.67,0.68,0.88)
        print("Adding parameters")
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).RollerDiameter = param.RollerDiameter
        obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = param.RollerHeight
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of teeth of the cycloidal disk")).ToothCount = param.ToothCount
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Base Height")).BaseHeight = param.BaseHeight
        obj.addProperty("App::PropertyLength", "DriverPinDiameter", "CycloidGearBox",QT_TRANSLATE_NOOP("App::Property", "Driver Pin Diameter")).DriverPinDiameter = param.DriverPinDiameter\

        print("Done Adding parameters")

    def onChanged(self, fp, prop):
        print("pindisk onchanged", fp, prop)                        
        #App.ActiveDocument.getObject("GearBox_Parameters").onChanged(fp,prop)
        if prop=='Proxy':
            pass
        if prop=='ToothCount':
            App.ActiveDocument.getObject("GearBox_Parameters").ToothCount = \
                App.ActiveDocument.getObject('pinDisk').ToothCount
        if prop=='RollerDiameter':
            App.ActiveDocument.getObject("GearBox_Parameters").RollerDiameter = \
                App.ActiveDocument.getObject('pinDisk').RollerDiameter
        if prop=='RollerHeight':
            App.ActiveDocument.getObject("GearBox_Parameters").RollerHeight = \
                App.ActiveDocument.getObject("pinDisk").RollerHeight
        if prop=='BaseHeight':
            App.ActiveDocument.getObject("GearBox_Parameters").BaseHeight = \
                App.ActiveDocument.getObject('pinDisk').BaseHeight
        if prop=='DriverPinDiameter':
            App.ActiveDocument.getObject("GearBox_Parameters").DriverPinDiameter = \
                App.ActiveDocument.getObject('pinDisk').DriverPinDiameter
        print("done pindisk onchanged")
        
    def recomputeGB(self,H):
        print("recomputing pin disk",H)
        self.Object.Shape = cycloidFun.generatePinBase(H["ToothCount"], H["ToothPitch"], H["RollerDiameter"],
            H["Eccentricity"], H["RollerHeight"], H["DriverPinDiameter"], H["BaseHeight"],
            H["PressureAngleLimit"])
        #self.GearBox.gearBox.generatePinBase()

        
class   cycdiskClass():
    def __init__(self,obj,gearbox):
        self.Object = obj        
        obj.Proxy = self
        #obj.addProperty("App::PropertyString", "Parent","Parameter","Parent").Parent = App.ActiveDocument.GearBox_Parameters
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyInteger","DiskHoleCount","CycloidGearBox",QT_TRANSLATE_NOOP("APP::Property","Number of driving holes of the cycloid disk")).DiskHoleCount = param.DiskHoleCount
        obj.addProperty("App::PropertyLength", "CycloidalDiskHeight","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Cycloidal Disk Height")).CycloidalDiskHeight = param.CycloidalDiskHeight
        self.GearBox = gearbox
        self.ShapeColor=(0.12,0.02,0.63)        

    def onChanged(self, fp, prop):
        print("cycloiddisk onchanged", fp, prop)
        p = App.ActiveDocument.getObject("GearBox_Parameters")
        s = App.ActiveDocument.getObject('CycloidalDisk')
        if prop=='DiskHoleCount':
            p.DiskHoleCount = s.DiskHoleCount
        if prop=='CycloidalDiskHeight':
            p.CycloidalDiskHeight = s.CycloidalDiskHeight

    def execute(self, obj):
        #obj.Shape = self.gearBox.generatePinBase()
        print('cycloidgearbox execute',obj)

        
    def recomputeGB(self,H):
        print("recomputing cycloidal disk")
        self.Object.Shape = cycloidFun.generateCycloidalDisk(H["ToothCount"],
                                                             H["ToothPitch"],
                                                             H["RollerDiameter"],
                                                             H["Eccentricity"],
                                                             H["LineSegmentCount"],
                                                             H["PressureAngleLimit"],
                                                             H["PressureAngleOffset"],
                                                             H["BaseHeight"],
                                                             H["CycloidalDiskHeight"],
                                                             H["DiskHoleCount"])

class   EccShaft():
    def __init__(self,obj,gearbox):
        self.Object = obj
        self.gearbox = gearbox
        obj.Proxy = self        
        self.ShapeColor=(0.42,0.42,0.63)
        param = App.ActiveDocument.getObject("GearBox_Parameters")
        obj.addProperty("App::PropertyLength", "Eccentricity","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Eccentricity")).Eccentricity =param.Eccentricity

    def onChanged(selfself,fp,prop):
        if prop=="Eccentricity":
            gbp = App.ActiveDocument.getObject("GearBox_Parameters")
            es = App.ActiveDocument.getObject("EccentricShaft")
            gbp.Eccentricity = es.Eccentricity
            gbp.RollerDiameter = es.Eccentricity *2

    def recomputeGB(self,H):
        print("recomputing Eccentric Shaft")
        self.Object.Shape = cycloidFun.generateEccentricShaft(H["RollerDiameter"],H["RollerHeight"],H["Eccentricity"])

        
class   CycloidalGearBox():
    def __init__(self, obj):
        print("CycloidalGearBox __init__")
        obj.addProperty("App::PropertyFloat","Version","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","The version of CycloidGearBox Workbench used to create this object")).Version = version
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of teeth of the cycloidal disk")).ToothCount=12
        obj.addProperty("App::PropertyInteger","DiskHoleCount","CycloidGearBox",QT_TRANSLATE_NOOP("APP::Property","Number of driving holes of the cycloid disk")).DiskHoleCount = 6
        obj.addProperty("App::PropertyInteger", "LineSegmentCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of line segments to make up the cycloidal disk")).LineSegmentCount= 400
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).RollerDiameter = 4.7
        obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = 14.0
        obj.addProperty("App::PropertyAngle", "ToothPitch","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Tooth Pitch")).ToothPitch = 4
        obj.addProperty("App::PropertyLength", "Eccentricity","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Eccentricity")).Eccentricity = 4.7 /2
        obj.addProperty("App::PropertyLength", "CenterDiameter","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Center Diameter")).CenterDiameter = 5.0
        obj.addProperty("App::PropertyLength", "PressureAngleLimit","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Limit")).PressureAngleLimit= 50.0
        obj.addProperty("App::PropertyAngle", "PressureAngleOffset","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Offset")).PressureAngleOffset= 0.0
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Base Height")).BaseHeight = 10.0
        obj.addProperty("App::PropertyLength", "DriverPinDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Driver Pin Diameter")).DriverPinDiameter = 12
        obj.addProperty("App::PropertyLength", "CycloidalDiskHeight","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Cycloidal Disk Height")).CycloidalDiskHeight = 4
        obj.Proxy = self
        self.recomputeList = []
        print("Properties added")        
        self.Object = obj        
        attrs = vars(self)
        print( ', '.join("%s: %s" % item for item in attrs.items()))

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
        print("cycloid gearbox_parameters onchanged", fp, prop)
        dirty = False

        obj = App.ActiveDocument.getObject("GearBox_Parameters")
        pinDisk =     App.ActiveDocument.getObject('pinDisk')
        es = App.ActiveDocument.getObject('EccentricShaft')
        if prop=='RollerDiameter':
            if es.Eccentricity!=obj.Eccentricity:
                es.Eccentricity = obj.Eccentricity
            dirty = True
        if prop=='ToothCount':
            if pinDisk.ToothCount != obj.ToothCount:
                pinDisk.ToothCount = obj.ToothCount
            dirty = True
        if prop=='LineSegmentCount':
            dirty = True
        if prop=='RollerDiameter':
            if obj.Eccentricity!=obj.RollerDiameter / 2:
                obj.Eccentricity = obj.RollerDiameter /2
            if es.Eccentricity!=obj.Eccentricity:
                es.Eccentricity = obj.Eccentricity
            if pinDisk.RollerDiameter!= obj.RollerDiameter:
                pinDisk.RollerDiameter = obj.RollerDiameter
            dirty = True
        if prop=='RollerHeight':
            if pinDisk.RollerHeight != obj.RollerHeight:
                pinDisk.RollerHeight = obj.RollerHeight
            dirty = True
        if prop=='ToothPitch':
            if pinDisk.ToothCount!= obj.ToothCount:
                pinDisk.ToothCount = obj.ToothCount
            dirty = True
        if prop=='Eccentricity':
            if (obj.RollerDiamter != obj.Eccentricity*2):
                obj.RollerDiameter = obj.Eccentricity*2
            if es.Eccentricity!=obj.Eccentricity:
                es.Eccentricity = obj.Eccentricity
            dirty = True
        if prop=='CenterDiameter':
            dirty = True
        if prop=='PressureAngleLimit':
            dirty = True
        if prop=='PressureAngleOffset':
            dirty = True
        if prop=='BaseHeight':
            if pinDisk.BaseHeight!=obj.BaseHeight:
                pinDisk.BaseHeight = obj.BaseHeight
            dirty = True
        if prop=='DriverPinDiameter':
            dirty = True
        if prop=='CycloidalDiskHeight':
            dirty = True
        if prop=='DiskHoleCount':
            dirty = True
        if prop=='Refresh':
            dirty = True
        if dirty:
            print("recomputing")
            self.recompute()
        print("done gearbox_parameters onChanged")
        
    def recompute(self):
        hyperparameters = {"ToothCount" : self.Object.__getattribute__("ToothCount"),
                           "LineSegmentCount" : self.Object.__getattribute__("LineSegmentCount"),
                           "RollerDiameter" : self.Object.__getattribute__("RollerDiameter").Value,
                           "RollerHeight" : self.Object.__getattribute__("RollerHeight").Value,
                           "ToothPitch" : self.Object.__getattribute__("ToothPitch").Value,
                           "Eccentricity" : self.Object.__getattribute__("Eccentricity").Value,
                           "CenterDiameter" : self.Object.__getattribute__("CenterDiameter").Value,
                           "PressureAngleLimit" : self.Object.__getattribute__("PressureAngleLimit").Value,
                           "PressureAngleOffset" : self.Object.__getattribute__("PressureAngleOffset").Value,
                           "BaseHeight" : self.Object.__getattribute__("BaseHeight").Value,
                           "DriverPinDiameter" : self.Object.__getattribute__("DriverPinDiameter").Value,
                           "CycloidalDiskHeight" : self.Object.__getattribute__("CycloidalDiskHeight").Value,
                           "DiskHoleCount" : self.Object.__getattribute__("DiskHoleCount")
        }
        for a in self.recomputeList:
            a.recomputeGB(hyperparameters)

    def execute(self, obj):
        #obj.Shape = self.gearBox.generatePinBase()
        print('cycloidgearbox execute',obj)

        

class ViewProviderCGBox:
   def __init__(self, obj,icon):
       """
       Set this object to the proxy object of the actual view provider
       """
       print("ViewProviderCGBox init start")
       print(self)
       print(obj)
       obj.Proxy = self
       self.part = obj
       self.icon = icon
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
       print("viewProviderCGBox updateData",fp,prop)
       
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
       return self.icon
       #return main_CGB_Icon
 
   def __getstate__(self):
       return None

   def __setstate__(self,state):
       print("__setstate__",state)
       return None


FreeCADGui.addCommand('CycloidGearBoxCreateObject',CycloidGearBoxCreateObject())
    
