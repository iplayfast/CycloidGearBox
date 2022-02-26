#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2019                                                    *  
#*   Chris Bruner                                                          *  
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************
#import cycloidbox
import os
import cycloidFun

smWBpath = os.path.dirname(cycloidFun.__file__)
smWB_icons_path =  os.path.join( smWBpath, 'icons')
global main_CGB_Icon
main_CGB_Icon = os.path.join( smWB_icons_path , 'cycloidgearbox.svg')
global sketch_Icon
sketch_Icon = os.path.join(smWB_icons_path,'SketcherWorkbench.svg')
#print(main_CGB_Icon)
#print(sketch_Icon)
#print("here")

"""
class CycloidSketch(Workbench):
    Icon = sketch_Icon
    MenuText = "CyclidalSketch"
    ToolTip = "make a sketch from gear_box"
    def __init__(self):
        pass

    def Initialize(self):
        Log("Initialize")
        import cycloidDiskSketch
        Log("Import")
        self.__class__.Icon = sketch_Icon
        Log("icon")
        self.appendToolBar("CycloidGearBox")
        Log("tb")

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Activated(self):
        Msg("CycloidSketch.Activated()\n")

    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        Msg("CycloidSketch.Deactivated()\n")
"""
class CycloidGearBoxWorkbench(Workbench):
    "Cycloid Gear Box object"
    
    Icon = main_CGB_Icon
    MenuText = "CycloidalGearBox"
    ToolTip = "A complete Cycloidal Gear Box"
    
    def __init__(self):
            pass
            

    def Initialize(self):
        #import cycloidbox        
        import cycloidbox
        import cycloidDiskSketch
        self.__class__.Icon = main_CGB_Icon
        profileitems = ["CycloidGearBoxCreateObject"]
        self.appendToolbar("CycloidGearBox",profileitems)
        self.appendMenu("CycloidGearBox",profileitems)
#        Gui.addCommand("CreateCycloidSketch",cycloidDiskSketch.CycloidCreateSketch(self,self))

        Log("Loading CycloidGearBox ... done\n")

    def GetClassName(self):
            return "Gui::PythonWorkbench"
        
    def Activated(self):            
            Msg ("CycloidalGearBox.Activated()\n")               
    def Deactivated(self):
        " This function is executed when the workbench is deactivated"
        Msg ("CycloidalGearBox.Deactivated()\n")               

        
FreeCADGui.addWorkbench(CycloidGearBoxWorkbench)

# File format pref pages are independent and can be loaded at startup
FreeCAD.__unit_test__ += [ "TestCycloid" ]


