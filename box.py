#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 02:24:45 2019

@author: chris
"""

import FreeCAD
import Part
import FreeCADGui
import os


import cycloidpath_locator

version = 0.01

smWBpath = os.path.dirname(cycloidpath_locator.__file__)
smWB_icons_path =  os.path.join( smWBpath, 'icons')
global main_box_Icon
main_box_Icon = os.path.join( smWB_icons_path , 'samplebox.svg')


def QT_TRANSLATE_NOOP(scope, text):
    return text


class BoxCreateObject():
    def GetResources(self):
        print(os.path.join( 'icons','cycloidgearbox.svg'))
        return {'Pixmap' : main_box_Icon,
            'MenuText': "&Create A hypoCycloidalGear", 
            'ToolTip' : "Create samplecode box" }
    
    def __init__(self):
        pass
        
        #ViewProviderBox(a.ViewObject)
    def Activated(self):            
        print("cycloidbox Activated")
        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument()
        doc = FreeCAD.ActiveDocument
        obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', "mybox")
        fpo = box(obj)
        ViewProviderBox(obj.ViewObject)
        FreeCAD.ActiveDocument.recompute()
        return fpo
        
        
        
    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        print ("CycloidalGearBox.Deactivated()\n") 

    def execute(self, obj):
        print('boxCreateObject execute')

def create(obj_name):
   """
   Object creation method
   """

   obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', obj_name)

   fpo = box(obj)

   ViewProviderBox(obj.ViewObject)

   FreeCAD.ActiveDocument.recompute()

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
       return mode

   def onChanged(self, vobj, prop):
       """
       Print the name of the property that has changed
       """

       FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

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
   
FreeCADGui.addCommand('BoxCreateObject',BoxCreateObject())
