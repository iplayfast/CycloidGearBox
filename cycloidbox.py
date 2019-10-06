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
global main_CGB_Icon
main_CGB_Icon = os.path.join( smWB_icons_path , 'cycloidgearbox.svg')

__dir__ = os.path.dirname(__file__)
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
        self.gearBox = cycloidClass.cycloidClass()
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
 
   def __getstate__(self):
       return None

   def __setstate__(self,state):
       print("__setstate__",state)
       return None


FreeCADGui.addCommand('CycloidGearBoxCreateObject',CycloidGearBoxCreateObject())
    
