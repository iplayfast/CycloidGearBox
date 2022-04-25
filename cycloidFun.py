#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 16:43:09 2019

@author: Chris Bruner
Hypocycloid gear boxgenerator
Code to create a hypocycloidal gearbox
https://en.wikipedia.org/wiki/Cycloidal_drive
Copyright 	2019, Chris Bruner
Version 	v0.1
License 	LGPL V2.1
Homepage https://github.com/iplayfast/CycloidGearBox

Useful tip
from importlib import reload
import foo

while True:
    # Do some things.
    if is_changed(foo):
        foo = reload(foo)
"""

from locale import YESEXPR
import math
from operator import truediv
import FreeCAD
from FreeCAD import Base
import FreeCAD as App

import Sketcher
import random # for colors
import numpy as np
import Part
from Part import BSplineCurve, Shape, Wire, Face, makePolygon, \
    makeLoft, Line, BSplineSurface, \
    makePolygon, makeHelix, makeShell, makeSolid


from inspect import currentframe    #for debugging
""" style guide
def functions_are_lowercase(variables_as_well):

class ClassesArePascalCase:

SomeClass.some_variable
"""

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

def QT_TRANSLATE_NOOP(scope, text):
    return text


def to_polar(x, y):
    return (x ** 2.0 + y ** 2.0) ** 0.5, math.atan2(y, x)


def to_rect(r, a):
    return r * math.cos(a), r * math.sin(a)

                                                                              
def calcyp(p,a,e,n):                                                   
    return math.atan(math.sin(n*a)/(math.cos(n*a)+(n*p)/(e*(n+1))))  

def calc_x(p,roller_diameter,eccentricty,tooth_count,angle):                                                 
    return (tooth_count*p)*math.cos(angle)+eccentricty*math.cos((tooth_count+1)*angle)-roller_diameter/2*math.cos(calcyp(p,angle,eccentricty,tooth_count)+angle)
                                                                                
def calc_y(p,roller_diameter,eccentricity,tooth_count,angle):                                                     
    return (tooth_count*p)*math.sin(angle)+eccentricity*math.sin((tooth_count+1)*angle)-roller_diameter/2*math.sin(calcyp(p,angle,eccentricity,tooth_count)+angle)
         


def buildCurve(self, obj):
        pts = self.Points[obj.FirstIndex:obj.LastIndex+1]
        bs = Part.BSplineCurve()
        if (obj.Method == "Parametrization") and (obj.Parametrization == "Curvilinear") and (hasattr(obj.PointObject,"Distance")):
            params = []
            try:
                dis = obj.PointObject.Distance
            except:
                dis = 1.0
            for i in range(len(pts)):
                params.append(1.0 * i * dis)
            lv = pts[-1].sub(pts[-2])
            params[-1] = params[-2] + lv.Length
            bs.interpolate(Points = pts, Parameters = params, Tolerance = obj.ApproxTolerance)

        elif obj.Method == "Parametrization":
            bs.approximate(Points = pts, DegMin = obj.DegreeMin, DegMax = obj.DegreeMax, Tolerance = obj.ApproxTolerance, Continuity = obj.Continuity, ParamType = obj.Parametrization)
        elif obj.Method == "Smoothing Algorithm":
            bs.approximate(Points = pts, DegMin = obj.DegreeMin, DegMax = obj.DegreeMax, Tolerance = obj.ApproxTolerance, Continuity = obj.Continuity, LengthWeight = obj.LengthWeight, CurvatureWeight = obj.CurvatureWeight , TorsionWeight = obj.TorsionWeight)
        if obj.ClampEnds:
            bs.setPole(1,self.Points[0])
            bs.setPole(int(bs.NbPoles),self.Points[-1])
        self.curve = bs 

def calc_pressure_angle(pin_circle_radius,roller_diameter,a):
    ex = 2**0.5
    pin_circle_radius
    rg = pin_circle_radius/ex
    pp = rg * (ex**2 + 1 - 2*ex*math.cos(a))**0.5 - roller_diameter/2
    return math.asin( (pin_circle_radius*math.cos(a)-rg)/(pp+roller_diameter/2))*180/math.pi

def calc_pressure_limit(pin_circle_radius,roller_diameter,eccentricity,angle):
    ex = 2**0.5        
    rg = pin_circle_radius/ex
    q = (pin_circle_radius**2 + rg**2 - 2*pin_circle_radius*rg*math.cos(angle))**0.5
    x = rg - eccentricity + (q-roller_diameter/2)*(pin_circle_radius*math.cos(angle)-rg)/q
    y = (q-roller_diameter/2)*pin_circle_radius*math.sin(angle)/q
    return (x**2 + y**2)**0.5

def check_limit(x,y,maxrad,minrad,offset):
    r, a = to_polar(x, y)
    if (r > maxrad) or (r < minrad):
            r = r - offset
            x, y = to_rect(r, a)
    return x, y


def calculate_radii(pin_count: int, eccentricity, outer_diameter, pin_diameter:float):
    """

    :param pin_count: Number of teeth of cycloidal gear
    :param eccentricity: offset of cycloidal gear
    :param outer_diameter: diameter of gear
    :param pin_diameter: diameter of pins
    :return: r1,r2 (formulas used for calculating points along the array)
    """
    outer_radius = outer_diameter / 2.0
    pin_radius = pin_diameter / 2.0
    # No less than 3, no more than 50 pins
    if pin_count<3:
        pin_count = 3
    if pin_count>50:
        pin_count = 50
    # e cannot be larger than r (d/2)
    if eccentricity > pin_radius:
        eccentricity = pin_radius

    # Validate r based on R and N: canot be larger than R * sin(pi/N) or the circles won't fit
    if pin_radius > outer_radius * math.sin( math.pi)/ pin_count :
        pin_radius = outer_radius * math.sin(math.pi)/ pin_count
    inset = pin_radius
    angle = 360 / pin_count


    # To draw a epitrachoid, we need r1 (big circle), r2 (small rolling circle) and d (displament of point)
    # r1 + r2 = R = D/2
    # r1/r2 = (N-1)
    # From the above equations: r1 = (N - 1) * R/N, r2 = R/N
    r1 = (pin_count - 1)* outer_radius / pin_count
    r2 = outer_radius / pin_count
    return r1,r2

def calculate(step : int, eccentricity, r1, r2: float):
    X = (r1 + r2) * math.cos(2 * math.pi * step) + eccentricity * math.cos((r1 + r2) * 2 * math.pi * step / r2)
    Y = (r1 + r2) * math.sin(2 * math.pi * step) + eccentricity * math.sin((r1 + r2) * 2 * math.pi * step / r2)
    return X,Y,0.0

def clean1(a):
    """ return -1 < a < 1 """
    return min(1, max(a, -1))

def fcvec(x):
    if len(x) == 2:
        return(App.Vector(x[0], x[1], 0))
    else:
        return(App.Vector(x[0], x[1], x[2]))

def make_bspline(pts):
    curve = []
    for i in pts:
        out = BSplineCurve()
        out.interpolate(list(map(fcvec, i)))
        curve.append(out)
    return curve

def make_bspline_wire(pts):
    wi = []
    for i in pts:
        out = BSplineCurve()
        out.interpolate(list(map(fcvec, i)))
        wi.append(out.toShape())
    return Wire(wi)

def driver_shaft_hole(radius,hole_count,hole_number):        
    x = radius * math.cos((2.0 * math.pi / hole_count) * hole_number)
    y = radius * math.sin((2.0 * math.pi / hole_count) * hole_number)
    return x,y

def newSketch(body,name=''):
    """ all sketches are centered around xyplane"""
    name = name + 'Sketch'
    sketch = body.Document.addObject('Sketcher::SketchObject',name)
    sketch.Support = (body.Document.getObject('XY_Plane'),[''])
    sketch.MapMode = 'FlatFace'
    body.addObject(sketch)
    sketch.Visibility = False
    return sketch

def newPad(body,sketch,height,name=''):
    name = name + 'Pad'
    pad = body.Document.addObject("PartDesign::Pad",name)
    body.addObject(pad)
    pad.Length = height
    pad.Profile = sketch
    return pad

def newPolar(body,pad,sketch,count,name=''):
    name = name + 'Polar'
    polar = body.newObject('PartDesign::PolarPattern',name)
    polar.Axis = (sketch,['N_Axis'])
    polar.Angle = 360
    polar.Occurrences = count
    return polar

def newPocket(body,sketch,height,name=''):
    name = name + 'Pocket'
    pocket = body.Document.addObject("PartDesign::Pocket",name)
    body.addObject(pocket)
    pocket.Length = height
    pocket.Profile = sketch
    pocket.Reversed = True 
    return pocket

    
def SketchCircle(sketch,x,y,diameter,last,Name="",ref=False):
    #print("SketchCircle",x,y,diameter,last,ref)
    c = sketch.addGeometry(Part.Circle())
    if x==0 and y==0:
        cst = sketch.addConstraint(Sketcher.Constraint('Coincident',c,3,-1,1))#3 (edge selector) means center point of circle,
    else:
        if x==0:            
            #print('point x')
            cst = sketch.addConstraint(Sketcher.Constraint('PointOnObject',c,3,-2))
        else:
            #print('Distance X')
            cst = sketch.addConstraint(Sketcher.Constraint('DistanceX',c,3,-1,1,x))                    
        if y==0:
            #print('Point Y',c)
            cst = sketch.addConstraint(Sketcher.Constraint('PointOnObject',c,3,-1))
        else:
            #print('Distance Y')
            cst = sketch.addConstraint(Sketcher.Constraint('DistanceY',c,3,-1,1,y))    
        #sketch.setDatum(yc,y)    
    if last!=-1:
        rad = sketch.addConstraint(Sketcher.Constraint('Equal',last,c))
    else:
        rad = sketch.addConstraint(Sketcher.Constraint('Diameter',c,diameter))
        if Name!="":
            sketch.renameConstraint(rad,Name)
    
    if (ref):
        sketch.toggleConstruction(c);    
    return c    

def SketchCircleOfHoles(sketch,circle_radius,hole_radius,hole_count,orgx,orgy,name):
    last = -1
    for i in range(hole_count):
        x = orgx + circle_radius * math.cos((2.0 * math.pi / hole_count) * i)
        y = orgy + circle_radius * math.sin((2.0 * math.pi / hole_count) * i)        
        last = SketchCircle(sketch,x,y,hole_radius,last,"")#name + i)

def calculate_pressure_angle(p,roller_diameter,tooth_count,angle):
    ex = 2**0.5        
    r3 = p * tooth_count
    rg = r3/ex
    pp = rg * (ex**2 + 1 - 2*ex*math.cos(angle))**0.5 - roller_diameter/2
    return math.asin( (r3*math.cos(angle)-rg)/(pp+roller_diameter/2))*180/math.pi

    

def calculate_pressure_limit(p,roller_diameter,eccentricity,tooth_count,a):                                    
    #print("calc_pressure_limit",p,roller_diameter,eccentricity,tooth_count,a)
    ex = 2**0.5
    r3 = p*tooth_count
    rg = r3/ex
    q = (r3**2 + rg**2 - 2*r3*rg*math.cos(a))**0.5
    x = rg - eccentricity + (q-roller_diameter/2)*(r3*math.cos(a)-rg)/q
    y = (q-roller_diameter/2)*r3*math.sin(a)/q
    return (x**2 + y**2)**0.5


def calculate_min_max_radii(parameters):    
    """ Find the pressure angle limit circles """
    pin_circle_radius = parameters["pin_circle_diameter"] / 2.0
    tooth_count = parameters["tooth_count"]
    roller_diameter = parameters["roller_diameter"]
    pressure_angle_limit = parameters["pressure_angle_limit"]
    eccentricity = parameters["eccentricity"]
    p = pin_circle_radius / tooth_count
    
    minAngle = -1.0
    maxAngle = -1.0
    for i in range(0, 180):
        x = calculate_pressure_angle(p,roller_diameter,tooth_count, i * math.pi / 180.)
        if ( x < pressure_angle_limit) and (minAngle < 0):
            minAngle = float(i)
        if (x < -pressure_angle_limit) and (maxAngle < 0):
            maxAngle = float(i-1)
    #print("min/max angle",minAngle,maxAngle)
    min_radius = calculate_pressure_limit(p,roller_diameter,eccentricity,tooth_count, minAngle * math.pi / 180.)
    max_radius = calculate_pressure_limit(p,roller_diameter,eccentricity,tooth_count, maxAngle * math.pi / 180.)
    #print("min/max Radius",min_radius,max_radius)

    return min_radius, max_radius

                

def calc_DriveHoleRRadius(driver_disk_diameter,shaft_diameter):
    """ Calculates the radius that the drive holes are in
    about 1/2 way between rollers and central shaft."""  
    #not using parameters as these values might be resized from requested  
    cent = (driver_disk_diameter/2+shaft_diameter)/2
    return cent    

def generate_slot_size(parameters,add_clearence):        
    key_radius = parameters["key_diameter"]/2
    key_flat = parameters["key_flat_diameter"] -key_radius    
    key_radius += add_clearence /2
    key_flat += add_clearence /2
    return key_radius,key_flat


def generate_key_sketch(parameters,add_clearence,sketch,Offset=0):    
    key_radius,key_flat = generate_slot_size(parameters,add_clearence)
    arc = sketch.addGeometry(Part.ArcOfCircle(Part.Circle(Base.Vector(Offset,0,0),Base.Vector(0,0,1),key_radius),2,1),False)
    sketch.addConstraint(Sketcher.Constraint('Coincident',arc,3,-1,1))
    c = sketch.addConstraint(Sketcher.Constraint('Radius',arc,key_radius))
    l = sketch.addGeometry(Part.LineSegment(Base.Vector(-2,key_flat,0),Base.Vector(2,key_flat/3,0)),False)
    #print(arc,l)
    sketch.addConstraint(Sketcher.Constraint('Coincident',l,1,arc,1))
    sketch.addConstraint(Sketcher.Constraint('Coincident',l,2,arc,2))
    sketch.addConstraint(Sketcher.Constraint('Horizontal',l))
    vc = sketch.addConstraint(Sketcher.Constraint('DistanceY',0,3,l,1,key_flat))

   
    

def generate_pin_disk_part(part,parameters):
    """ create the base that the fixed_ring_pins will be attached to """
    sketch = newSketch(part,'DriverDiskBase')
    #sketch.deleteAllConstraints()
    #sketch.deleteAllGeometry()
    
    tooth_count = parameters["tooth_count"]
    roller_diameter = parameters["roller_diameter"]
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"]
    Height = parameters["Height"]
    clearance = parameters["clearance"]
    eccentric = parameters["eccentricity"]
    min_radius = parameters["min_rad"]
    max_radius = parameters["max_rad"]
    pin_circle_diameter = parameters["pin_circle_diameter"]
    Diameter = parameters["Diameter"]
    driver_disk_height = parameters["disk_height"]
    driver_disk_diameter = parameters["driver_disk_diameter"]
    #print(driver_disk_diameter,min_radius,roller_diameter)
    
    #if driver_disk_diameter>min_radius*2-roller_diameter/2:
    #    print("driver diameter too big, resizing")
    #    driver_disk_diameter = min_radius*2-roller_diameter/2
    #    parameters["driver_disk_diameter"] = driver_disk_diameter

    

    #driver_disk_diameter += clearance
    
    pin_height = driver_disk_height*3
    #bottom plate, total width of box = outdiameter
    SketchCircle(sketch,0,0,shaft_diameter + clearance,-1,"ShaftHole")
    SketchCircle(sketch,0,0,Diameter,-1,"Diameter")   
    newPad(part,sketch,base_height - driver_disk_height,'center');
    
    sketch1 = newSketch(part)    
    SketchCircle(sketch1,0,0,Diameter,-1,"Diameter")   #outer circle    
    SketchCircle(sketch1,0,0,driver_disk_diameter + clearance,-1,"driver_disk_diameter")    
    newPad(part,sketch1,base_height,'outside')
    #base is done, now for the rollers
    
    roller_ring_radius = pin_circle_diameter /2 + clearance
    pinsketch = newSketch(part,'pinMale')    
    SketchCircle(pinsketch,roller_ring_radius,0,roller_diameter/4.0,-1,"pin_circle_diameter_male")
    pad = newPad(part,pinsketch,base_height+pin_height+driver_disk_height,'pinMale')    
    
    pinsketch1 = newSketch(part,'roller')
    p = roller_ring_radius / tooth_count
    i = 0
    x = p * tooth_count * math.cos(2 * math.pi / (tooth_count + 1) * i)
    y = p * tooth_count * math.sin(2 * math.pi / (tooth_count + 1) * i)
    SketchCircle(pinsketch1,roller_ring_radius,0,roller_diameter,-1,"pin_circle_diameter_roller")
    rol = newPad(part,pinsketch1,base_height+pin_height,"Roller")
    
    pinsketch2 = newSketch(part,'pinSketchFemale')    
    SketchCircle(pinsketch2,roller_ring_radius,0,roller_diameter/4.0+clearance,-1,"pin_circle_diameter_female")
    
    join = newPocket(part,pinsketch2,pin_height,'pinJoiner')    
    pol = newPolar(part,pad,pinsketch,tooth_count+1,'pin')
    pol.Originals = [pad,rol,join]
    pad.Visibility = False
    rol.Visibility = False
    join.Visibility = False    
    pol.Visibility = True
    part.Tip = pol

def generate_driver_disk_part(part,parameters):
    sketch = newSketch(part,'DriverDiskBase')            
    min_radius = parameters["min_rad"]
    max_radius = parameters["max_rad"]
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    roller_diameter = parameters["roller_diameter"]
    eccentricity = parameters["eccentricity"]
    shaft_diameter = parameters["shaft_diameter"]
    base_height = parameters["base_height"]
    clearance = parameters["clearance"]
    disk_height = parameters["disk_height"]
    driver_disk_diameter = parameters["driver_disk_diameter"]
    
    #if driver_disk_diameter>min_radius-roller_diameter/2:
    #    print("driver diameter too big, resizing")
    #    driver_disk_diameter = min_radius*2-roller_diameter/2
    #    parameters["driver_disk_diameter"] = driver_disk_diameter
    
    SketchCircle(sketch,0,0,driver_disk_diameter,-1,"DriverDiameter")    
    innershaftDia = (shaft_diameter  + eccentricity+clearance/2) 
    SketchCircle(sketch,0,0,innershaftDia,-1,"ShaftHole")
    pad = newPad(part,sketch,disk_height)
    driver_hole_diameter = parameters["driver_hole_diameter"]
    last = -1   
    DriveHoleRRadius = calc_DriveHoleRRadius(driver_disk_diameter,shaft_diameter);
    
    sketch1 = newSketch(part,'DriverShaft')
    SketchCircle(sketch1,DriveHoleRRadius,0,driver_hole_diameter,-1,"DriverShaft")    
    pad = newPad(part,sketch1,disk_height*4)    
    
    part.Placement = Base.Placement(Base.Vector(0,0,base_height - disk_height),Base.Rotation(Base.Vector(0,0,1),0))
    pol = newPolar(part,pad,sketch1,driver_disk_hole_count,'DriverDisk')
    pol.Originals = [pad]
    pad.Visibility = False
    pol.Visibility = True
    part.Tip = pol

def generate_input_shaft_part(body,parameters):
    eccentricity = parameters["eccentricity"] #default 2
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"] # default 13
    clearance = parameters["clearance"] #defualt .5
    disk_height = parameters["disk_height"]
    driver_disk_height = parameters["disk_height"]
    sketch1 = newSketch(body,'Shaft')
    
    SketchCircle(sketch1,0,0,shaft_diameter,-1,"Shaft")
    newPad(body,sketch1,base_height - driver_disk_height,'bearinghole');
        
    sketch2 = newSketch(body,'Shaft1')
    sketch2.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    innershaftDia = (shaft_diameter  + eccentricity)  
    SketchCircle(sketch2,0,0,innershaftDia,-1,"InnerShaft")
    newPad(body,sketch2,driver_disk_height,'shaftabovebase');
    pin_dia = eccentricity*2
    innershaftRadius = innershaftDia /2 
    #key_radius = parameters["key_diameter"]/2
    #generate_key_sketch(parameters,clearance,sketch2,shaft_diameter-(key_radius+clearance))    
    pinsketch1 = newSketch(body,'Pin1')
    pinsketch1.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch1,-(innershaftRadius-pin_dia)/2,0,pin_dia,-1,"pin1")
    newPad(body,pinsketch1,driver_disk_height+disk_height,'Pin1');
    
    pinsketch2 = newSketch(body,'Pin2')
    pinsketch2.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch2,-(innershaftRadius-(pin_dia)),0,pin_dia,-1,"pin2")
    newPad(body,pinsketch2,driver_disk_height+disk_height,'Pin2');
    
    keysketch = newSketch(body,'InputKey')
    generate_key_sketch(parameters,0,keysketch)
    newPocket(body,keysketch,base_height+driver_disk_height,'InputKey')
    
    body.Placement = Base.Placement(Base.Vector(0,0,0),Base.Rotation(Base.Vector(0,0,1),0))

def generate_cycloidal_disk_array(parameters):
    tooth_count = parameters["tooth_count"]
    tooth_pitch = parameters["tooth_pitch"]
    pin_circle_radius = parameters["pin_circle_diameter"] / 2.0
    roller_diameter = parameters["roller_diameter"]
    eccentricity = parameters["eccentricity"]
    line_segment_count = parameters["line_segment_count"]
    pressure_angle_offset = parameters["pressure_angle_offset"]
    pressure_angle_limit = parameters["pressure_angle_limit"]
    min_radius = parameters["min_rad"]
    max_radius = parameters["max_rad"]
    p = pin_circle_radius / tooth_count
    """ make the array to be used in the bspline
        that is the cycloidalDisk
    """
    q = 2 * math.pi / float(line_segment_count)
    # Find the pressure angle limit circles

    i=0
    x = calc_x(p,  roller_diameter, eccentricity, tooth_count, q*i / float(tooth_count))
    y = calc_y(p,  roller_diameter, eccentricity, tooth_count, q*i / tooth_count)
    x, y = check_limit(x,y,max_radius,min_radius,pressure_angle_offset)
    
    cycloidal_disk_array = [Base.Vector(x-eccentricity, y, 0)]
    for i in range(0,line_segment_count):
        x = calc_x(p,  roller_diameter, eccentricity, tooth_count, q*(i+1) / tooth_count)
        y = calc_y(p,  roller_diameter, eccentricity, tooth_count, q*(i+1)/ tooth_count)
        x, y = check_limit(x,y,max_radius,min_radius,pressure_angle_offset)        
        cycloidal_disk_array.append([x-eccentricity, y, 0])
    
    #cycloidal_disk_array.append(cycloidal_disk_array[0])
    #print("diskarray")
    #print(cycloidal_disk_array)
    return cycloidal_disk_array


def generate_cycloidal_disk_part(part,parameters,DiskOne):    
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"]
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    clearance = parameters["clearance"]
    tooth_count = parameters["tooth_count"]
    disk_height = parameters["disk_height"]
    driver_disk_diameter = parameters["driver_disk_diameter"]
    offset = 0.0
    rot = 180 - (tooth_count+1)/tooth_count
    name = "cycloid001"
    
    mat= App.Matrix()
    mat.move(App.Vector(eccentricity, 0., 0.))
    mat.rotateZ(2 * np.pi / tooth_count)
    mat.move(App.Vector(-eccentricity, 0., 0.))    
    
    #get shape of cycloidal disk
    if not DiskOne: #second disk
        offset = disk_height
        rot = 0
        name = "cycloid002"

    
    array = generate_cycloidal_disk_array(parameters)    
    sketch = newSketch(part,name)    
    wi = make_bspline([array])        
    wires = []
    
    for _ in range(tooth_count):
        w0 = wi[0]
        w0.transform(mat)                
        g = sketch.addGeometry(w0)
        sketch.addConstraint(Sketcher.Constraint('Block',g))                   
    
    part.Placement = Base.Placement(Base.Vector(0*eccentricity,0,base_height+offset),Base.Rotation(Base.Vector(0,0,1),rot))    
    SketchCircle(sketch,eccentricity,0,shaft_diameter +clearance,-1,"centerHole")        
    driver_hold_diameter = (parameters["driver_hole_diameter"]+eccentricity*2) 
    last = -1
    DriveHoleRRadius = calc_DriveHoleRRadius(driver_disk_diameter,shaft_diameter);
    pad = newPad(part,sketch,disk_height,name)                
    SketchCircleOfHoles(sketch,DriveHoleRRadius,driver_hold_diameter,driver_disk_hole_count,eccentricity,0,"DriverShaftHole")
    
    
def generate_eccentric_key_part(part,parameters):    
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    clearance = parameters["clearance"]
    shaft_diameter = parameters["shaft_diameter"]
    disk_height = parameters["disk_height"]
    driver_disk_height = parameters["disk_height"]
    
    sketch = newSketch(part,'key1')
    SketchCircle(sketch,-eccentricity,0,shaft_diameter,-1,"Key1")    
    newPad(part,sketch,disk_height,'keyPad')
    
    sketch = newSketch(part,'key2')
    sketch.AttachmentOffset = Base.Placement(Base.Vector(0,0,disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(sketch,eccentricity,0,shaft_diameter,-1,"Key1")    
    newPad(part,sketch,disk_height,'keyPad')
    
    pin_dia = eccentricity*2
    
    innershaftDia = (shaft_diameter  + eccentricity)  #(13+2) = 15
    innershaftRadius = innershaftDia /2 
    pinsketch1 = newSketch(part,'Pin1')
    pinsketch1.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch1,-(innershaftRadius-pin_dia)/2,0,pin_dia,-1,"pin1")
    pock1 = newPocket(part,pinsketch1,driver_disk_height+disk_height,'Pin1');
    pock1.Reversed = False

    pinsketch2 = newSketch(part,'Pin2')
    pinsketch2.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch2,-(innershaftRadius-(pin_dia)),0,pin_dia,-1,"pin2")
    pock2 = newPocket(part,pinsketch2,driver_disk_height+disk_height,'Pin2');
    pock2.Reversed = False
        
    part.Placement = Base.Placement(Base.Vector(0,0,base_height),Base.Rotation(Base.Vector(0,0,1),0))

def generate_output_shaft_part(part,parameters):    
    sketch = newSketch(part,'OutputShaftBase') 
    min_radius = parameters["min_rad"]
    max_radius = parameters["max_rad"]

    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    eccentricity = parameters["eccentricity"]
    roller_diameter = parameters["roller_diameter"]
    shaft_diameter = parameters["shaft_diameter"]
    clearance = parameters["clearance"]
    base_height = parameters["base_height"]
    disk_height = parameters["disk_height"]
    driver_disk_diameter = parameters["driver_disk_diameter"]
    #if driver_disk_diameter>min_radius*2-roller_diameter/2:
    #    print("driver diameter too big, resizing")
    #    driver_disk_diameter = min_radius*2-roller_diameter/2
    #    parameters["driver_disk_diameter"] = driver_disk_diameter

    SketchCircle(sketch,0,0,driver_disk_diameter,-1,"Base") #outer circle    
    pad = newPad(part,sketch,disk_height)
    sketchh = newSketch(part,'holes')
    driver_hole_diameter = (parameters["driver_hole_diameter"]+clearance)
    last = -1        
    DriveHoleRRadius = calc_DriveHoleRRadius(driver_disk_diameter,shaft_diameter);
    
    SketchCircle(sketchh,DriveHoleRRadius,0,driver_hole_diameter,-1,"DriverHoles")
    pocket = newPocket(part,sketchh,disk_height)
    pol = newPolar(part,pocket,sketchh,driver_disk_hole_count,"DriverHole")
    pol.Originals = [pocket]
    pocket.Visibility = False
    pol.Visibility = True
    
    keysketch = newSketch(part,'InputKey')
    generate_key_sketch(parameters,0,keysketch)
    pad = newPad(part,keysketch,20)
    part.Placement = Base.Placement(Base.Vector(0,0,base_height+disk_height*2),Base.Rotation(Base.Vector(0,0,1),0))
    pol.Visibility = False
    part.Tip = pol
    pol.Visibility = True

def ready_part(doc,name):
    """ will create a body of "name" if not already present.
    if Is present, will delete anything in it """
    part = doc.getObject(name)
    if part:        
        part.removeObjectsFromDocument()
    else:
        part = doc.addObject('PartDesign::Body', name)        
    return part

def testcycloidal():
    if not App.ActiveDocument:
        App.newDocument()
    doc = App.ActiveDocument
    p = generate_default_parameters()    
    part = ready_part(doc,'cycloidalDisk1')        
    return generate_cycloidal_disk_part(part,p,True)        

def generate_parts(doc,parameters):
    """ will (re)create all bodys of all parts needed """
    minr,maxr = calculate_min_max_radii(parameters)            
    parameters["min_rad"] = minr
    parameters["max_rad"] = maxr

    print("cyloidFun creating parts")
    random.seed(555)

    part = ready_part(doc,'pinDisk')           
    generate_pin_disk_part(part,parameters)            
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)    
    
    part = ready_part(doc,'driverDisk')    
    generate_driver_disk_part(part,parameters) 
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)     
    
    part = ready_part(doc,'inputShaft')           
    generate_input_shaft_part(part,parameters)    
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)    
    
    part = ready_part(doc,'cycloidalDisk1')        
    generate_cycloidal_disk_part(part,parameters,True)
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)    
    
    part = ready_part(doc,'cycloidalDisk2')    
    generate_cycloidal_disk_part(part,parameters,False)
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)
    
    part = ready_part(doc,'eccentricKey')    
    generate_eccentric_key_part(part,parameters)   
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)    
    
    part = ready_part(doc,'outputShaft')       
    generate_output_shaft_part(part,parameters)   
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)    
    
    #doc.recompute()
    
    
def generate_default_parameters():
    parameters = {
        "eccentricity": 2.0,#4.7 / 2,
        "tooth_count": 11,#12,
        "driver_disk_hole_count": 6,
        "driver_hole_diameter": 10,
        "driver_disk_diameter": 50.0,
        "line_segment_count": 42, #tooth_count squared
        "tooth_pitch": 4,
        "Diameter" : 95,#110,
        "roller_diameter": 9.4,
        "pin_circle_diameter" : 80,
        "pressure_angle_limit": 50.0,
        "pressure_angle_offset": 0.1,
        "base_height":10.0,
        "disk_height":5.0,
        "shaft_diameter":13.0,
        "key_diameter":5,
        "key_flat_diameter": 4.8,
        "Height" : 20.0,
        "clearance" : 0.5        
        }
    minr,maxr = calculate_min_max_radii(parameters)            
    parameters["min_rad"] = minr
    parameters["max_rad"] = maxr
    return parameters

def test_parts():
    if not App.ActiveDocument:
        App.newDocument()
    doc = App.ActiveDocument
    h = generate_default_parameters()    
    generate_parts(doc,h)

    
