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
import cycloidpath_locator

smWBpath = os.path.dirname(cycloidpath_locator.__file__)
smWB_icons_path =  os.path.join( smWBpath, 'icons')
global main_CGB_Icon
main_CGB_Icon = os.path.join( smWB_icons_path , 'cycloidgearbox.svg')
print(main_CGB_Icon)
class CycloidGearBox(Workbench):
    "Cycloid Gear Box object"
    def __init__(self):
        import os
        self.__class__.Icon = main_CGB_Icon
        #FreeCAD.getResourceDir() +
        #    "Mod/CycloidGearBox/icons/cycloidegearbox.svg"
        self.__class__.MenuText = "Cycloid"
        self.__class__.ToolTip = "Cycloid Gear Box workbench"

    def Initialize(self):
        import Part,FreeCAD,DraftTools,DraftGui,cycloidbox
        from FreeCAD import Base

        self.geartools = ["fixedRingPins","fixedRingPinDisk","rollerPins","eccentricShaft","cycloidalDisk"]
        self.utilities = []
                     
        # draft tools
        self.drafttools = ["Draft_Line","Draft_Wire","Draft_Circle","Draft_Arc","Draft_Ellipse",
                        "Draft_Polygon","Draft_Rectangle", "Draft_Text",
                        "Draft_Dimension", "Draft_BSpline","Draft_Point",
                        "Draft_Facebinder","Draft_BezCurve","Draft_Label"]
        self.draftmodtools = ["Draft_Move","Draft_Rotate","Draft_Offset",
                        "Draft_Trimex", "Draft_Upgrade", "Draft_Downgrade", "Draft_Scale",
                        "Draft_Shape2DView","Draft_Draft2Sketch","Draft_Array",
                        "Draft_Clone"]
        self.draftextratools = ["Draft_WireToBSpline","Draft_AddPoint","Draft_DelPoint","Draft_ShapeString",
                                "Draft_PathArray","Draft_Mirror","Draft_Stretch"]
        self.draftcontexttools = ["Draft_ApplyStyle","Draft_ToggleDisplayMode","Draft_AddToGroup","Draft_AutoGroup",
                            "Draft_SelectGroup","Draft_SelectPlane",
                            "Draft_ShowSnapBar","Draft_ToggleGrid","Draft_UndoLine",
                            "Draft_FinishLine","Draft_CloseLine"]
        self.draftutils = ["Draft_Layer","Draft_Heal","Draft_FlipDimension",
                           "Draft_ToggleConstructionMode","Draft_ToggleContinueMode","Draft_Edit",
                           "Draft_Slope","Draft_SetWorkingPlaneProxy","Draft_AddConstruction"]
        self.snapList = ['Draft_Snap_Lock','Draft_Snap_Midpoint','Draft_Snap_Perpendicular',
                         'Draft_Snap_Grid','Draft_Snap_Intersection','Draft_Snap_Parallel',
                         'Draft_Snap_Endpoint','Draft_Snap_Angle','Draft_Snap_Center',
                         'Draft_Snap_Extension','Draft_Snap_Near','Draft_Snap_Ortho','Draft_Snap_Special',
                         'Draft_Snap_Dimensions','Draft_Snap_WorkingPlane']
        
        def QT_TRANSLATE_NOOP(scope, text): return text
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench","cycloidal tools"),self.geartools) 
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench","Draft tools"),self.drafttools)
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench","Draft mod tools"),self.draftmodtools)
#        self.appendMenu([QT_TRANSLATE_NOOP("cycloid","&Arch"),
#                         QT_TRANSLATE_NOOP("arch","Utilities")],self.utilities)
        self.appendMenu(QT_TRANSLATE_NOOP("arch","&Cycloidal"),self.geartools)
        self.appendMenu(QT_TRANSLATE_NOOP("arch","&Draft"),self.drafttools+self.draftmodtools+self.draftextratools)
        self.appendMenu([QT_TRANSLATE_NOOP("arch","&Draft"),QT_TRANSLATE_NOOP("arch","Utilities")],self.draftutils+self.draftcontexttools)
        self.appendMenu([QT_TRANSLATE_NOOP("arch","&Draft"),QT_TRANSLATE_NOOP("arch","Snapping")],self.snapList)
        FreeCADGui.addIconPath(":/icons")
        FreeCADGui.addLanguagePath(":/translations")
        if hasattr(FreeCADGui,"draftToolBar"):
            if not hasattr(FreeCADGui.draftToolBar,"loadedArchPreferences"):
                FreeCADGui.addPreferencePage(":/ui/preferences-arch.ui","Arch")
                FreeCADGui.addPreferencePage(":/ui/preferences-archdefaults.ui","Arch")
                FreeCADGui.draftToolBar.loadedArchPreferences = True
            if not hasattr(FreeCADGui.draftToolBar,"loadedPreferences"):
                FreeCADGui.addPreferencePage(":/ui/preferences-draft.ui","Draft")
                FreeCADGui.addPreferencePage(":/ui/preferences-draftsnap.ui","Draft")
                FreeCADGui.addPreferencePage(":/ui/preferences-draftvisual.ui","Draft")
                FreeCADGui.addPreferencePage(":/ui/preferences-drafttexts.ui","Draft")
                FreeCADGui.draftToolBar.loadedPreferences = True
        Log ('Loading Cycloidal module... done\n')

    def Activated(self):
        if hasattr(FreeCADGui,"draftToolBar"):
            FreeCADGui.draftToolBar.Activated()
        if hasattr(FreeCADGui,"Snapper"):
            FreeCADGui.Snapper.show()
        Log("Cycloidal workbench activated\n")
                
    def Deactivated(self):
        if hasattr(FreeCADGui,"draftToolBar"):
            FreeCADGui.draftToolBar.Deactivated()
        if hasattr(FreeCADGui,"Snapper"):
            FreeCADGui.Snapper.hide()
        Log("Cycloidal workbench deactivated\n")

    def ContextMenu(self, recipient):
        self.appendContextMenu("Utilities",self.draftcontexttools)

    def GetClassName(self):
        return "CycloidGearBox::Workbench"

FreeCADGui.addWorkbench(CycloidGearBox)

# File format pref pages are independent and can be loaded at startup
FreeCAD.__unit_test__ += [ "TestCycloid" ]


