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
import cycloidClass

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
   obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', obj_name)
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
        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument()
        doc = FreeCAD.ActiveDocument
        """# test code
        sketch = doc.Body.newObject('Sketcher::SketchObject','Sketch') 
        sketch.Support = (FreeCAD.activeDocument().XY_Plane, [''])
        sketch.MapMode = 'FlatFace'
        """
        obj=doc.addObject("Part::FeaturePython","GearBox Parameters")   
        cbg = CycloidalGearBox(obj)          
        #ViewProviderCGBox(obj.ViewObject)

        pindiskobj = doc.addObject("Part::FeaturePython","pinDisk")
        pindisk = pindiskClass(pindiskobj,cbg)
        pindiskobj.Shape = cbg.gearBox.generatePinBase()
        pindiskobj.Proxy= cbg
        cbg.recomputeList.append(pindisk)
        ViewProviderCGBox(pindiskobj.ViewObject,pin_Icon)
        
        cycdiskobj = doc.addObject("Part::FeaturePython","CycloidalDisk")        
        cycdisk = cycdiskClass(cycdiskobj,cbg)        
        cycdiskobj.Shape = cbg.gearBox.generateCycloidalDisk()
        cycdiskobj.Proxy = cbg
        cbg.recomputeList.append(cycdisk)
        ViewProviderCGBox(cycdiskobj.ViewObject, main_Icon)
        
        
        esobj = doc.addObject("Part::FeaturePython","EccentricShaft")
        escShaft = EccShaft(esobj,cbg)    
        esobj.Shape = cbg.gearBox.generateEccentricShaft()
        esobj.Proxy = cbg
        cbg.recomputeList.append(escShaft)
        ViewProviderCGBox(esobj.ViewObject,eccentric_Icon)
        
        cbg.onChanged('','Refresh')
        cbg.recompute()
        doc.recompute()
        cbg.recompute()
        return cbg
        
        
    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        print ("CycloidalGearBox.Deactivated()\n") 

    def execute(self, obj):
        print('cycloidgearboxCreateObject execute')


class   pindiskClass():
    def __init__(self,obj,gearbox):
        self.Object = obj
        obj.Proxy = self
        self.GearBox = gearbox
        self.ShapeColor=(0.67,0.68,0.88)
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).RollerDiameter = 10.0
        obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = 18.0
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of teeth of the cycloidal disk")).ToothCount=12
        obj.addProperty("App::PropertyFloat", "BaseHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Base Height")).BaseHeight = 15.0

    def onChanged(self, fp, prop):
        print("pindisk onchanged", fp, prop)                
        #FreeCAD.ActiveDocument.getObject("GearBox_Parameters").onChanged(fp,prop)
        if prop=='Proxy':
            pass
        if hasattr(self, 'ToothCount'):
            FreeCAD.ActiveDocument.getObject("GearBox_Parameters").ToothCount = self.ToothCount
        if hasattr(self,'RollerDiameter'):
            FreeCAD.ActiveDocument.getObject("GearBox_Parameters").RollerDiameter = self.RollerDiameter
        if hasattr(self,'RollerHeight'):
            FreeCAD.ActiveDocument.getObject("GearBox_Parameters").RollerHeight = self.RollerHeight
        if hasattr(self,'BaseHeight'):
            FreeCAD.ActiveDocument.getObject("GearBox_Parameters").BaseHeight = self.BaseHeight
        print("done pindisk onchanged")
        
        #self.GearBox.onChanged(GearBox,fp,prop)
        
        #if prop=="CycloidalDiskHeight":            
            #FreeCAD.ActiveDocument.getObject("GearBox_Parameters").CycloidalDiskHeight = fp.getPropertyByName("CycloidalDiskHeight")
            #Proxy.onChanged(fp.prop)
            #parent = FreeCAD.ActiveDocument.getObject(fp.getPropertyByName("Parent"))
            #print(parent)
            #FreeCAD.getDocument("Parent").getObject("GearBox_Parameters").CycloidalDiskHeight = fp.getPropertyByName("CycloidalDiskHeight")
            #recomputeGB()
        
        
    def recomputeGB(self,gp):
        print("recomputing pin disk")
        self.Object.Shape = gp.gearBox.generatePinBase()
        #self.GearBox.gearBox.generatePinBase()

        
class   cycdiskClass():
    def __init__(self,obj,gearbox):
        self.Object = obj
        obj.Proxy = self
        #obj.addProperty("App::PropertyString", "Parent","Parameter","Parent").Parent = gearbox.Label
        #obj.addProperty("App::PropertyFloat", "CycloidalDiskHeight","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Cycloidal Disk Height")).CycloidalDiskHeight = 1.75
        self.GearBox = gearbox
        self.ShapeColor=(0.12,0.02,0.63)

    def onChanged(self, fp, prop):
        print("cycloiddisk onchanged", fp, prop)                
        #self.GearBox.onChanged(GearBox,fp,prop)
        
        #if prop=="CycloidalDiskHeight":            
            #FreeCAD.ActiveDocument.getObject("GearBox_Parameters").CycloidalDiskHeight = fp.getPropertyByName("CycloidalDiskHeight")
            #Proxy.onChanged(fp.prop)
            #parent = FreeCAD.ActiveDocument.getObject(fp.getPropertyByName("Parent"))
            #print(parent)
            #FreeCAD.getDocument("Parent").getObject("GearBox_Parameters").CycloidalDiskHeight = fp.getPropertyByName("CycloidalDiskHeight")
            #recomputeGB()
            
        
    def recompute(self):
        for a in self.recomputeList:
            a.recomputeGB()
        
    def execute(self, obj):
        obj.Shape = self.gearBox.generatePinBase()
        print('cycloidgearbox execute',obj)

        
    def recomputeGB(self,gp):
        print("recomputing cycloidal disk")
        self.Object.Shape = self.GearBox.gearBox.generateCycloidalDisk()
        
class   EccShaft():
    def __init__(self,obj,gearbox):
        self.Object = obj
        obj.Proxy = self
        self.GearBox = gearbox
        self.ShapeColor=(0.42,0.42,0.63)
        
    def recomputeGB(self,gp):
        print("recomputing Eccentric Shaft")
        self.Object.Shape = self.GearBox.gearBox.generateEccentricShaft()
        
        
class   CycloidalGearBox():
    def __init__(self, obj):
        print("CycloidalGearBox __init__")       
        self.gearBox = cycloidClass.cycloidClass()
        obj.addProperty("App::PropertyFloat","Version","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","The version of CycloidGearBox Workbench used to create this object")).Version = version
        obj.addProperty("App::PropertyInteger", "ToothCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of teeth of the cycloidal disk")).ToothCount=12
        obj.addProperty("App::PropertyInteger", "LineSegmentCount", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Number of line segments to make up the cycloidal disk")).LineSegmentCount= 4000
        obj.addProperty("App::PropertyLength", "RollerDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Diameter of the rollers")).RollerDiameter = 10.0
        obj.addProperty("App::PropertyLength", "RollerHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Height of the rollers")).RollerHeight = 15.0
        obj.addProperty("App::PropertyAngle", "ToothPitch","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Tooth Pitch")).ToothPitch = 5.08
        obj.addProperty("App::PropertyLength", "Eccentricity","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Eccentricity")).Eccentricity = 3.4
        obj.addProperty("App::PropertyLength", "CenterDiameter","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Center Diameter")).CenterDiameter = -1.0
        obj.addProperty("App::PropertyAngle", "PressureAngleLimit","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Limit")).PressureAngleLimit= 50.0
        obj.addProperty("App::PropertyAngle", "PressureAngleOffset","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Pressure Angle Offset")).PressureAngleOffset= 0.01        
        obj.addProperty("App::PropertyLength", "BaseHeight", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Base Height")).BaseHeight = 15.0
        obj.addProperty("App::PropertyLength", "DriverPinDiameter", "CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Driver Pin Diameter")).DriverPinDiameter = 10.0
        obj.addProperty("App::PropertyLength", "CycloidalDiskHeight","CycloidGearBox", QT_TRANSLATE_NOOP("App::Property","Cycloidal Disk Height")).CycloidalDiskHeight = 10.75
        obj.Proxy = self            
        self.recomputeList = []
        print("Properties added")        
        self.Object = obj        
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
        if prop=='ToothCount':
           self.gearBox.ToothCount = fp.getPropertyByName("ToothCount")
           dirty = True
        if prop=='LineSegmentCount':
            self.gearBox.LineSegmentCount = fp.getPropertyByName("LineSegmentCount")
            dirty = True
        if prop=='RollerDiameter':
            self.gearBox.RollerDiameter = fp.getPropertyByName("RollerDiameter")
            dirty = True
        if prop=='RollerHeight':
            self.gearBox.RollerHeight = fp.getPropertyByName("RollerHeight")
            dirty = True
        if prop=='ToothPitch':
            self.gearBox.ToothPitch = fp.getPropertyByName("ToothPitch")
            dirty = True
        if prop=='Eccentricity':
            self.gearBox.Eccentricity = fp.getPropertyByName("Eccentricity")
            dirty = True
        if prop=='CenterDiameter':
            self.gearBox.CenterDiameter = fp.getPropertyByName("CenterDiameter")
            dirty = True
        if prop=='PressureAngleLimit':
            self.gearBox.PressureAngleLimit = fp.getPropertyByName("PressureAngleLimit")
            dirty = True
        if prop=='BaseHeight':
            self.gearBox.BaseHeight = fp.getPropertyByName("BaseHeight")
            dirty = True
        if prop=='DriverPinDiameter':
            self.gearBox.DriverPinDiameter = fp.getPropertyByName("DriverPinDiameter")
            dirty = True
        if prop=='CycloidalDiskHeight':
            self.gearBox.CycloidalDiskHeight = fp.getPropertyByName("CycloidalDiskHeight")
            dirty = True
        if prop=='Refresh':
            dirty = True
        if dirty:            
            self.recompute()
        print("done gearbox_parameters onChanged")
        
    def recompute(self):
        for a in self.recomputeList:
            a.recomputeGB(self)
        
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
       return self.icon
       #return main_CGB_Icon
 
   def __getstate__(self):
       return None

   def __setstate__(self,state):
       print("__setstate__",state)
       return None


FreeCADGui.addCommand('CycloidGearBoxCreateObject',CycloidGearBoxCreateObject())
    
