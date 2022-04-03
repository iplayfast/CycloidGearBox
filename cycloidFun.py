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

import math
import FreeCAD
from FreeCAD import Base
import FreeCAD as App
import Part
import Sketcher
import random # for colors

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


def calc_yp(tooth_count, eccentricity, tooth_pitch, a):
    return math.atan(math.sin(tooth_count * a) / (
            math.cos(tooth_count * a) + (tooth_count * tooth_pitch) / (eccentricity * (tooth_count + 1))))

    
def calc_x(tooth_count, eccentricity, tooth_pitch, pin_disk_pin_diameter: float, a):
    return (tooth_count * tooth_pitch) * math.cos(a) + eccentricity * \
           math.cos((tooth_count + 1) * a) - pin_disk_pin_diameter / 2.0 * \
           math.cos(calc_yp(tooth_count, eccentricity, tooth_pitch, a) + a)


def calc_y(tooth_count: int, eccentricity, tooth_pitch, pin_disk_pin_diameter: float, a):
    return (tooth_count * tooth_pitch) * math.sin(a) + eccentricity * \
           math.sin((tooth_count + 1) * a) - pin_disk_pin_diameter / 2.0 * \
           math.sin(calc_yp(tooth_count, eccentricity, tooth_pitch, a) + a)

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

    
def SketchCircle(sketch,x,y,r,last,Name="",ref=False):
    #print("SketchCircle",x,y,r,last,ref)
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
        rad = sketch.addConstraint(Sketcher.Constraint('Diameter',c,r*2))
        if Name!="":
            sketch.renameConstraint(rad,Name)
    
    if (ref):
        sketch.toggleConstruction(c);    
    return c
    
def SketchCircleOfHoles(sketch,circle_radius,hole_radius,hole_count,name):
    last = -1
    for i in range(hole_count):
        x,y = driver_shaft_hole(circle_radius,hole_count,i)
        last = SketchCircle(sketch,x,y,hole_radius,last,name)

def calculate_pressure_angle(tooth_count, tooth_pitch, pin_disk_pin_diameter, angle):
    """ calculate the angle of the cycloidalDisk teeth at the angle """
    ex = 2.0 ** 0.5
    r3 = tooth_pitch * tooth_count
    #        p * n
    rg = r3 / ex
    pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - pin_disk_pin_diameter / 2.0
    return math.asin(clean1(((r3 * math.cos(angle) - rg) / (pp + pin_disk_pin_diameter / 2.0)))) * 180 / math.pi


def calculate_pressure_limit(tooth_count, tooth_pitch, eccentricity, pin_disk_pin_diameter, a):
    ex = 2.0 ** 0.5
    r3 = tooth_pitch * tooth_count
    rg = r3 / ex
    q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
    x = rg - eccentricity + (q - pin_disk_pin_diameter / 2.0) * (r3 * math.cos(a) - rg) / q
    y = (q - pin_disk_pin_diameter / 2.0) * r3 * math.sin(a) / q
    return (x ** 2.0 + y ** 2.0) ** 0.5


def check_limit(v: FreeCAD.Vector, pressure_angle_offset, minrad, maxrad):
    """ if x,y outside limit return x,y as at limit, else return x,y
        :type v: FreeCAD.Vector """
    r, a = to_polar(v.x, v.y)
    if (r > maxrad) or (r < minrad):
        r = r - pressure_angle_offset
        v.x, v.y = to_rect(r, a)
    return v


def calculate_min_max_radii(parameters):
    """ Find the pressure angle limit circles """
    #test code
    tooth_count= parameters['tooth_count']
    radius_requested = parameters['Diameter']/2.0
    pi2 = 2 * math.pi
    circumfrence_requested = pi2 * radius_requested 
    roller_diameter = parameters['pin_disk_pin_diameter']
    roller_cirumfrence_needed = tooth_count*2*roller_diameter #  teeth and space betweenteeth * roller diameter
    roller_ring_radius = roller_cirumfrence_needed / pi2   
    
    if (roller_cirumfrence_needed>circumfrence_requested): # rollers larger than base
        circumfrence_requested = roller_cirumfrence_needed + roller_diameter
        print("Diameter too small-- resizing")
        
    return roller_cirumfrence_needed/pi2,circumfrence_requested / pi2
    
    tooth_count= parameters['tooth_count']
    tooth_pitch= parameters['tooth_pitch']
    pin_disk_pin_diameter= parameters['pin_disk_pin_diameter']
    eccentricity= parameters['eccentricity']
    pressure_angle_limit= parameters['pressure_angle_limit']

    min_angle = -1.0
    max_angle = -1.0
    for i in range(0, 180):
        x = calculate_pressure_angle(tooth_count, tooth_pitch, pin_disk_pin_diameter, i * math.pi / 180)
        if (x < pressure_angle_limit) and (min_angle < 0):
            min_angle = i * 1.0
        if (x < -pressure_angle_limit) and (max_angle < 0):
            max_angle = i  - 1.0
    min_radius = calculate_pressure_limit(tooth_count, tooth_pitch, eccentricity, pin_disk_pin_diameter, min_angle * math.pi / 180)
    max_radius = calculate_pressure_limit(tooth_count, tooth_pitch, eccentricity, pin_disk_pin_diameter, max_angle * math.pi / 180)
    return min_radius, max_radius

def calc_DriveHoleRRadius(parameters):
    """ Calculates the radius that the drive holes are in
    about 1/2 way between rollers and central shaft."""    
    cent = (parameters["driver_disk_diameter"]+parameters["shaft_diameter"])/2
    return cent    

def calc_min_dia(parameters):
    min_radius, max_radius = calculate_min_max_radii(parameters)    
    return 2 * ((min_radius + max_radius) / 2 + parameters["pin_disk_pin_diameter"]+ parameters["eccentricity"])

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

   
    
def generate_cycloidal_disk_array(parameters,min_radius,max_radius):
    tooth_count = parameters["tooth_count"]-1
    tooth_pitch = parameters["tooth_pitch"]
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    eccentricity = parameters["eccentricity"]
    line_segment_count = parameters["line_segment_count"]
    pressure_angle_offset = parameters["pressure_angle_offset"]
    """ make the array to be used in the bspline
        that is the cycloidalDisk
    """
    #min_radius, max_radius= calculate_min_max_radii(H)
    q = 2.0 * math.pi / line_segment_count
    i = 0
    #r1,r2 = calculate_radii(tooth_count,eccentricity,105,10)
    r1,r2 = calculate_radii(tooth_count,eccentricity,(min_radius+max_radius)/2,pin_disk_pin_diameter)
    # v1 is starting point
    v1 = Base.Vector(calc_x(tooth_count, eccentricity, tooth_pitch, pin_disk_pin_diameter, q * i),
                     calc_y(tooth_count, eccentricity, tooth_pitch, pin_disk_pin_diameter, q * i),
                     0)
    v1 = check_limit(v1, pressure_angle_offset, min_radius, max_radius)
    #va1 = Base.Vector(calculate(0,eccentricity,r1,r2))
    #va1 = check_limit(va1, pressure_angle_offset, min_radius, max_radius)
    cycloidal_disk_array = []
    #cycloidal_disk_array_alternative = []
    cycloidal_disk_array.append(v1)
    #cycloidal_disk_array_alternative.append(va1)
    for i in range(0, line_segment_count):
        v2 = Base.Vector(
            calc_x(tooth_count, eccentricity, tooth_pitch, pin_disk_pin_diameter, q * (i + 1)),
            calc_y(tooth_count, eccentricity, tooth_pitch, pin_disk_pin_diameter, q * (i + 1)),
            0)
        v2 = check_limit(v2, pressure_angle_offset, min_radius, max_radius)
        cycloidal_disk_array.append(v2)
        #va2 = Base.Vector(calculate(q * (i + 1), eccentricity, r1, r2))
        #va2 = check_limit(va2, pressure_angle_offset, min_radius, max_radius)
        #cycloidal_disk_array_alternative.append(va2)
    return cycloidal_disk_array#,cycloidal_disk_array_alternative


def generate_pin_disk_part(part,parameters):
    """ create the base that the fixed_ring_pins will be attached to """
    sketch = newSketch(part,'DriverDiskBase')
    #sketch.deleteAllConstraints()
    #sketch.deleteAllGeometry()
    
    tooth_count = parameters["tooth_count"]
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"]
    Height = parameters["Height"]
    clearance = parameters["clearance"]
    min_radius, max_radius= calculate_min_max_radii(parameters)
    
    driver_disk_height = parameters["disk_height"]
    
    #testsketch = newSketch(part)
    #SketchCircle(testsketch,0,0,2*min_radius,-1,"min_radius")
    #SketchCircle(testsketch,0,0,2*max_radius,-1,"max_radius")    
    #newPad(part,testsketch,1,'test');
    roller_ring_radius = min_radius*2+pin_disk_pin_diameter*2
    
    outdiameter = max_radius*2+pin_disk_pin_diameter*2
    #diameter =  outdiameter - pin_disk_pin_diameter*2
    pin_height = driver_disk_height*3
    SketchCircle(sketch,0,0,shaft_diameter / 2.0 + clearance,-1,"ShaftHole")
    SketchCircle(sketch,0,0,outdiameter,-1,"OuterDiameter")   #outer circle
    #SketchCircle(sketch,0,0,outdiameter/2,-1,"OuterDiameter")   #outer circle
    newPad(part,sketch,base_height - driver_disk_height,'centerPad');
    sketch1 = newSketch(part)
    #SketchCircle(sketch1,0,0,outdiameter/2,-1,"OuterDiameter")   #outer circle
    SketchCircle(sketch1,0,0,outdiameter,-1,"OuterDiameter")   #outer circle
    driver_disk_diameter = parameters["driver_disk_diameter"]
    SketchCircle(sketch1,0,0,driver_disk_diameter + clearance,-1,"driver_diameter")    
    newPad(part,sketch1,base_height,'outside')
    #base is done, now for the rollers
    
    pinsketch = newSketch(part,'pinMale')    
    #SketchCircle(pinsketch,pin_circle_radius,0,pin_disk_pin_diameter/4.0,-1,"pinMale")
    SketchCircle(pinsketch,roller_ring_radius,0,pin_disk_pin_diameter/4.0,-1,"pinMale")
    pad = newPad(part,pinsketch,base_height+pin_height+driver_disk_height,'pinMale')    
    
    pinsketch1 = newSketch(part,'roller')
    #SketchCircle(pinsketch1,pin_circle_radius,0,pin_disk_pin_diameter,-1,"pinRoller")
    SketchCircle(pinsketch1,roller_ring_radius,0,pin_disk_pin_diameter,-1,"pinRoller")
    rol = newPad(part,pinsketch1,base_height+pin_height,"Roller")
    
    pinsketch2 = newSketch(part,'pinSketchFemale')
    #SketchCircle(pinsketch2,pin_circle_radius,0,pin_disk_pin_diameter/4.0+clearance,-1,"pinFemale")
    SketchCircle(pinsketch2,roller_ring_radius,0,pin_disk_pin_diameter/4.0+clearance,-1,"pinFemale")
    
    join = newPocket(part,pinsketch2,pin_height,'pinJoiner')    
    pol = newPolar(part,pad,pinsketch,tooth_count,'pin')
    pol.Originals = [pad,rol,join]
    pad.Visibility = False
    rol.Visibility = False
    join.Visibility = False    
    pol.Visibility = True

def generate_driver_disk_part(part,parameters):
    sketch = newSketch(part,'DriverDiskBase')            
    min_radius,max_radius= calculate_min_max_radii(parameters)
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    eccentricity = parameters["eccentricity"]
    shaft_diameter = parameters["shaft_diameter"]
    base_height = parameters["base_height"]
    clearance = parameters["clearance"]
    disk_height = parameters["disk_height"]
    driver_disk_diameter = parameters["driver_disk_diameter"]
    SketchCircle(sketch,0,0,driver_disk_diameter,-1,"")    
    innershaft = (shaft_diameter  + eccentricity+clearance/2) / 2.0
    SketchCircle(sketch,0,0,innershaft+clearance,-1,"ShaftHole")
    pad = newPad(part,sketch,disk_height)
    r = parameters["driver_hole_diameter"]/2.0
    last = -1   
    DriveHoleRRadius = calc_DriveHoleRRadius(parameters);
    
    sketch1 = newSketch(part,'DriverShaft')
    SketchCircle(sketch1,DriveHoleRRadius,0,r,-1,"DriverShaft")
    #SketchCircleOfHoles(sketch1,mmr,r ,driver_disk_hole_count,"DriverShaft")
    pad = newPad(part,sketch1,disk_height*4)
    #pad = body.Document.addObject("PartDesign::Pad","Pad")
    #part.addObject(pad)
    #pad.Length = disk_height * 4
    #pad.Profile = sketch1    
    part.Placement = Base.Placement(Base.Vector(0,0,base_height - disk_height),Base.Rotation(Base.Vector(0,0,1),0))
    pol = newPolar(part,pad,sketch1,driver_disk_hole_count,'DriverDisk')
    pol.Originals = [pad]
    pad.Visibility = False
    pol.Visibility = True

def generate_eccentric_shaft_part(body,parameters):
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"]
    clearance = parameters["clearance"]
    disk_height = parameters["disk_height"]
    driver_disk_height = parameters["disk_height"]
    sketch1 = newSketch(body,'Shaft')
    
    SketchCircle(sketch1,0,0,shaft_diameter / 2.0,-1,"Shaft")
    newPad(body,sketch1,base_height - driver_disk_height,'bearinghole');
        
    sketch2 = newSketch(body,'Shaft1')
    sketch2.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    innershaft = (shaft_diameter  + eccentricity+clearance) / 2.0
    SketchCircle(sketch2,0,0,innershaft,-1,"InnerShaft")
    newPad(body,sketch2,driver_disk_height,'shaftabovebase');
    pin_dia = eccentricity
    
    #key_radius = parameters["key_diameter"]/2
    #generate_key_sketch(parameters,clearance,sketch2,shaft_diameter-(key_radius+clearance))    
    pinsketch1 = newSketch(body,'Pin1')
    pinsketch1.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch1,-(innershaft-pin_dia),0,pin_dia,-1,"pin1")
    newPad(body,pinsketch1,driver_disk_height+disk_height,'Pin1');
    
    pinsketch2 = newSketch(body,'Pin2')
    pinsketch2.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch2,-(innershaft-(pin_dia/2*3)),0,pin_dia,-1,"pin2")
    newPad(body,pinsketch2,driver_disk_height+disk_height,'Pin2');
    
    keysketch = newSketch(body,'InputKey')
    generate_key_sketch(parameters,0,keysketch)
    newPocket(body,keysketch,base_height+driver_disk_height,'InputKey')
    
    body.Placement = Base.Placement(Base.Vector(0,0,0),Base.Rotation(Base.Vector(0,0,1),-90))

def generate_cycloidal_disk_part(part,parameters,DiskOne):
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"]
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    clearance = parameters["clearance"]
    min_radius, max_radius = calculate_min_max_radii(parameters)
    disk_height = parameters["disk_height"]
    offset = 0.0
    rot = 7.0
    xeccentricy = 0
    yeccentricy = -eccentricity*2
    name = "cycloid001"
    #get shape of cycloidal disk
    if not DiskOne: #second disk
        offset = disk_height
        rot = -7
        xeccentricy = 0.0
        yeccentricy = eccentricity*2
        name = "cycloid002"
    array = generate_cycloidal_disk_array(parameters,min_radius,max_radius)
    
    curve = Part.BSplineCurve()
    curve.interpolate(array)    
        
    sketch = newSketch(part,name)
    sketch.addGeometry(curve);
    sketch.addConstraint(Sketcher.Constraint('Block',0))
    #sketch.addGeometry(Part.BSplineCurve(array))
    """a = Part.BSplineCurve(array).toShape()
    w = Part.Wire([a])
    f = Part.Face(w)"""    
    SketchCircle(sketch,0,0,shaft_diameter / 2.0+clearance,-1,"centerHole")    
    r = (parameters["driver_hole_diameter"]/2.0+eccentricity*2) 
    last = -1
    DriveHoleRRadius = calc_DriveHoleRRadius(parameters)
    
    #SketchCircleOfHoles(sketch,mmr,r+eccentricity ,driver_disk_hole_count,"DriverShaftHoles")
    pad = newPad(part,sketch,disk_height,name+'Pad')        
    part.Placement = Base.Placement(Base.Vector(xeccentricy,yeccentricy,base_height+offset),Base.Rotation(Base.Vector(0,0,1),rot))
    sketch = newSketch(part,'DriverShaftHoles')
    SketchCircle(sketch,DriveHoleRRadius,0,r,-1,"DriverShaftHole")    
    hole = newPocket(part,sketch,disk_height,'DriverShaftHole')
    pol = newPolar(part,hole,sketch,driver_disk_hole_count,'DriverShaftHoles')
    pol.Originals = [hole]
    hole.Visibility = False
    pol.Visibility = True
    

def generate_eccentric_key_part(part,parameters):    
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    clearance = parameters["clearance"]
    shaft_diameter = parameters["shaft_diameter"]
    disk_height = parameters["disk_height"]
    driver_disk_height = parameters["disk_height"]
    
    sketch = newSketch(part,'key1')
    SketchCircle(sketch,-eccentricity*2,0,shaft_diameter/2.0,-1,"Key1")    
    newPad(part,sketch,disk_height,'keyPad')
    
    sketch = newSketch(part,'key2')
    sketch.AttachmentOffset = Base.Placement(Base.Vector(0,0,disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(sketch,eccentricity*2,0,shaft_diameter/2.0,-1,"Key1")    
    newPad(part,sketch,disk_height,'keyPad')
    
    pin_dia = eccentricity
    innershaft = (shaft_diameter  + eccentricity+clearance) / 2.0

    pinsketch1 = newSketch(part,'Pin1')
    pinsketch1.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch1,-(innershaft-pin_dia),0,pin_dia,-1,"pin1")
    pock1 = newPocket(part,pinsketch1,driver_disk_height+disk_height,'Pin1');
    pock1.Reversed = False

    pinsketch2 = newSketch(part,'Pin2')
    pinsketch2.AttachmentOffset = Base.Placement(Base.Vector(0,0,base_height-driver_disk_height),Base.Rotation(Base.Vector(0,0,1),0))     
    SketchCircle(pinsketch2,-(innershaft-(pin_dia/2*3)),0,pin_dia,-1,"pin2")
    pock2 = newPocket(part,pinsketch2,driver_disk_height+disk_height,'Pin2');
    pock2.Reversed = False
        
    part.Placement = Base.Placement(Base.Vector(0,0,base_height),Base.Rotation(Base.Vector(0,0,1),-90))

def generate_output_shaft_part(part,parameters):    
    sketch = newSketch(part,'OutputShaftBase') 
    min_radius,max_radius= calculate_min_max_radii(parameters)
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    eccentricity = parameters["eccentricity"]
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    clearance = parameters["clearance"]
    base_height = parameters["base_height"]
    disk_height = parameters["disk_height"]
    driver_disk_diameter = parameters["driver_disk_diameter"]
    SketchCircle(sketch,0,0,driver_disk_diameter,-1,"Base") #outer circle    
    pad = newPad(part,sketch,disk_height)
    sketchh = newSketch(part,'holes')
    r = (parameters["driver_hole_diameter"]+clearance)  / 2.0
    last = -1        
    DriveHoleRRadius = calc_DriveHoleRRadius(parameters)
    SketchCircle(sketchh,DriveHoleRRadius,0,r,-1,"DriverHoles")
    pocket = newPocket(part,sketchh,disk_height)
    pol = newPolar(part,pocket,sketchh,driver_disk_hole_count,"DriverHole")
    pol.Originals = [pocket]
    pocket.Visibility = False
    pol.Visibility = True
    #SketchCircleOfHoles(sketch,mmr,r ,driver_disk_hole_count,"DriverHoles")    #no clearance added for output shaft holes
    
    keysketch = newSketch(part,'InputKey')
    generate_key_sketch(parameters,0,keysketch)
    pad = newPad(part,keysketch,20)
    part.Placement = Base.Placement(Base.Vector(0,0,base_height+disk_height*2),Base.Rotation(Base.Vector(0,0,1),0))


def ready_part(doc,name):
    """ will create a body of "name" if not already present.
    if Is present, will delete anything in it """
    part = doc.getObject(name)
    if part:        
        part.removeObjectsFromDocument()
    else:
        part = doc.addObject('PartDesign::Body', name)        
    return part

    
def generate_parts(doc,parameters):
    """ will (re)create all bodys of all parts needed """
    print("cyloidFun creating parts")
    random.seed(555)

    part = ready_part(doc,'pinDisk')           
    generate_pin_disk_part(part,parameters)            
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)    
    
    part = ready_part(doc,'driverDisk')    
    generate_driver_disk_part(part,parameters) 
    part.ViewObject.ShapeColor = (random.random(),random.random(),random.random(),0.0)     
    
    part = ready_part(doc,'eccentricShaft')           
    generate_eccentric_shaft_part(part,parameters)    
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
    print("done creating parts")
    #doc.recompute()
    
    
def generate_default_parameters():
    parameters = {
        "eccentricity": 2,#4.7 / 2,
        "tooth_count": 11,#12,
        "driver_disk_hole_count": 6,
        "driver_hole_diameter": 5,
        "driver_disk_diameter": 38,
        "line_segment_count": 121, #tooth_count squared
        "tooth_pitch": 4,
        "Diameter" : 40,#110,
        "pin_disk_pin_diameter": 4.7,
        "pressure_angle_limit": 50.0,
        "pressure_angle_offset": 0.0,
        "base_height":10.0,
        "disk_height":5.0,
        "shaft_diameter":13.0,
        "key_diameter":5,
        "key_flat_diameter": 4.8,
        "Height" : 20.0,
        "clearance" : 0.5
        }
    return parameters

def test_parts():
    if not App.ActiveDocument:
        App.newDocument()
    doc = App.ActiveDocument
    h = generate_default_parameters()    
    generate_parts(doc,h)

    
