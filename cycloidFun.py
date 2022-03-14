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

def newPad(body,sketch,height,name='Pad'):
    pad = body.Document.addObject("PartDesign::Pad",name)
    body.addObject(pad)
    pad.Length = height
    pad.Profile = sketch
    return pad

def newPocket(body,sketch,height,name='Pocket'):
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
        rad = sketch.addConstraint(Sketcher.Constraint('Radius',c,r))
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

def calc_mmr(min_radius,max_radius):
    return (min_radius+max_radius)/4

def calc_min_dia(parameters):
    min_radius, max_radius = calculate_min_max_radii(parameters)    
    return 2 * ((min_radius + max_radius) / 2 + parameters["pin_disk_pin_diameter"]+ parameters["eccentricity"])

def generate_slot_size(parameters,add_clearence=False):
    shaft_diameter = parameters["shaft_diameter"]
    clearance = parameters["clearance"]
    slot_size_width = shaft_diameter / 2
    slot_size_height = shaft_diameter / 2
    if add_clearence:
        slot_size_width += clearance /2
        slot_size_height += clearance /2
    return slot_size_width,slot_size_height


def generate_key_sketch(parameters,add_clearence,sketch):    
    x,y = generate_slot_size(parameters,add_clearence)
    arc = sketch.addGeometry(Part.ArcOfCircle(Part.Circle(Base.Vector(0,0,0),Base.Vector(0,0,1),x),2,1),False)
    sketch.addConstraint(Sketcher.Constraint('Coincident',arc,3,-1,1))
    c = sketch.addConstraint(Sketcher.Constraint('Radius',arc,x/2))
    l = sketch.addGeometry(Part.LineSegment(Base.Vector(-2,y/3,0),Base.Vector(2,y/3,0)),False)
    #print(arc,l)
    sketch.addConstraint(Sketcher.Constraint('Coincident',l,1,arc,1))
    sketch.addConstraint(Sketcher.Constraint('Coincident',l,2,arc,2))
    sketch.addConstraint(Sketcher.Constraint('Horizontal',l))
    vc = sketch.addConstraint(Sketcher.Constraint('DistanceY',0,3,l,1,y/3))

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
    pin_height = driver_disk_height*3
    SketchCircle(sketch,0,0,shaft_diameter / 2.0 + clearance,-1,"ShaftHole")
    SketchCircle(sketch,0,0,parameters["Diameter"]/2,-1,"OuterDiameter")   #outer circle
    newPad(part,sketch,base_height - driver_disk_height,'centerPad');
    sketch1 = newSketch(part)
    SketchCircle(sketch1,0,0,parameters["Diameter"]/2,-1,"OuterDiameter")   #outer circle
    SketchCircle(sketch1,0,0,min_radius * 0.75 + clearance,-1,"OutputDia")    
    newPad(part,sketch1,base_height,'outsidePad')
    pin_circle_radius =  ((min_radius+max_radius)/2.0 + pin_disk_pin_diameter/2)
    pinsketch = newSketch(part,'pinSketchMale')    
    SketchCircleOfHoles(pinsketch,pin_circle_radius,pin_disk_pin_diameter/4.0,tooth_count,"pinMale")    
    newPad(part,pinsketch,base_height+pin_height+driver_disk_height,'pinMale')    
    pinsketch1 = newSketch(part,'roller')
    SketchCircleOfHoles(pinsketch1,pin_circle_radius,pin_disk_pin_diameter,tooth_count,"pinRoller")
    newPad(part,pinsketch1,base_height+pin_height,"Roller")
    pinsketch2 = newSketch(part,'pinSketchFemale')
    SketchCircleOfHoles(pinsketch2,pin_circle_radius,pin_disk_pin_diameter/4.0+clearance,tooth_count,"pinFemale")    
    newPocket(part,pinsketch,pin_height,'pinJoiner')    

def generate_driver_disk_part(body,parameters):
    sketch = newSketch(body,'DriverDiskBase')            
    min_radius,max_radius= calculate_min_max_radii(parameters)
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    eccentricity = parameters["eccentricity"]
    shaft_diameter = parameters["shaft_diameter"]
    base_height = parameters["base_height"]
    clearance = parameters["clearance"]
    disk_height = parameters["disk_height"]
    SketchCircle(sketch,0,0,min_radius*0.75,-1,"")    
    SketchCircle(sketch,0,0,shaft_diameter / 2.0 + clearance,-1,"ShaftHole")
    pad = newPad(body,sketch,disk_height)
    r = parameters["driver_hole_diameter"] / 2    
    last = -1   
    mmr = calc_mmr(min_radius,max_radius);
    sketch1 = newSketch(body,'DriverShaft')
    SketchCircleOfHoles(sketch1,mmr,r ,driver_disk_hole_count,"DriverShaft")
    pad = body.Document.addObject("PartDesign::Pad","Pad")
    body.addObject(pad)
    pad.Length = disk_height * 4
    pad.Profile = sketch1
    body.Placement = Base.Placement(Base.Vector(0,0,base_height - disk_height),Base.Rotation(Base.Vector(0,0,1),0))

def generate_eccentric_shaft_part(body,parameters):
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"]
    clearance = parameters["clearance"]
    disk_height = parameters["disk_height"]
    sketch = newSketch(body,'Shaft')
    SketchCircle(sketch,0,0,shaft_diameter / 2.0,-1,"Shaft")
    newPad(body,sketch,base_height,'Shaft')
    sketch1 = newSketch(body,'EccentricShaft')   
    SketchCircle(sketch1,0,-eccentricity,shaft_diameter / 2.0,-1,"EccentrickDisk") #outer circle
    sketch1.AttachmentOffset = Base.Placement(Base.Vector(eccentricity,0,base_height),Base.Rotation(Base.Vector(0,0,1),0))
    newPad(body,sketch1,disk_height)    
    keysketch = newSketch(body,'InputKey')
    generate_key_sketch(parameters,clearance,keysketch)
    newPocket(body,keysketch,base_height,'InputKey')
    keysketch = newSketch(body,'InputKey') #second one for second disk key
    generate_key_sketch(parameters,clearance*2,keysketch)    # make this hole a bit smaller
    newPocket(body,keysketch,base_height+disk_height,'SecondDiskKey')
    body.Placement = Base.Placement(Base.Vector(0,0,1),Base.Rotation(Base.Vector(0,0,1),-90))

def generate_cycloidal_disk_part(body,parameters,DiskOne):
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    shaft_diameter = parameters["shaft_diameter"]
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    clearance = parameters["clearance"]
    min_radius, max_radius = calculate_min_max_radii(parameters)
    disk_height = parameters["disk_height"]
    offset = 0.0
    rot = 5.0
    xeccentricy = eccentricity
    yeccentricy = -eccentricity
    name = "cycloid001"
    #get shape of cycloidal disk
    if not DiskOne: #second disk
        offset = disk_height
        rot = -5
        xeccentricy = 0.0
        yeccentricy = eccentricity
        name = "cycloid002"
    array = generate_cycloidal_disk_array(parameters,min_radius,max_radius)
    """testcode"""
    curve = Part.BSplineCurve()
    curve.interpolate(array)    
        
    sketch = newSketch(body,name)
    sketch.addGeometry(curve);
    sketch.addConstraint(Sketcher.Constraint('Block',0))
    #sketch.addGeometry(Part.BSplineCurve(array))
    """a = Part.BSplineCurve(array).toShape()
    w = Part.Wire([a])
    f = Part.Face(w)"""    
    SketchCircle(sketch,0,0,shaft_diameter / 2.0+clearance,-1,"centerHole")    
    r = parameters["driver_hole_diameter"] / 2    
    last = -1
    mmr = calc_mmr(min_radius,max_radius);
    SketchCircleOfHoles(sketch,mmr,r+eccentricity*2 ,driver_disk_hole_count,"DriverShaftHoles")
    pad = newPad(body,sketch,disk_height,name+'Pad')    
    body.Placement = Base.Placement(Base.Vector(xeccentricy,yeccentricy,base_height+offset),Base.Rotation(Base.Vector(0,0,1),rot))

def generate_eccentric_key_part(body,parameters):    
    eccentricity = parameters["eccentricity"]
    base_height = parameters["base_height"]
    clearance = parameters["clearance"]
    shaft_diameter = parameters["shaft_diameter"]
    disk_height = parameters["disk_height"]
    sketch = newSketch(body,'key')
    SketchCircle(sketch,eccentricity,0,shaft_diameter/2.0,-1,"Key")
    newPad(body,sketch,disk_height,'keyPad')
    sketch = newSketch(body,"KeyLock")
    generate_key_sketch(parameters,clearance*2,sketch)    
    pad = newPad(body,sketch,disk_height,'keyPad')
    pad.Reversed = True
    body.Placement = Base.Placement(Base.Vector(0,0,base_height+disk_height),Base.Rotation(Base.Vector(0,0,1),-90))

def generate_output_shaft_part(body,parameters):    
    sketch = newSketch(body,'OutputShaftBase') 
    min_radius,max_radius= calculate_min_max_radii(parameters)
    driver_disk_hole_count = parameters["driver_disk_hole_count"]
    eccentricity = parameters["eccentricity"]
    pin_disk_pin_diameter = parameters["pin_disk_pin_diameter"]
    clearance = parameters["clearance"]
    base_height = parameters["base_height"]
    disk_height = parameters["disk_height"]
    SketchCircle(sketch,0,0,min_radius*0.75,-1,"Base") #outer circle    
    r = parameters["driver_hole_diameter"] / 2    
    last = -1        
    mmr = calc_mmr(min_radius,max_radius);
    SketchCircleOfHoles(sketch,mmr,r+clearance ,driver_disk_hole_count,"DriverHoles")    
    pad = newPad(body,sketch,disk_height)
    keysketch = newSketch(body,'InputKey')
    generate_key_sketch(parameters,0,keysketch)
    pad = newPad(body,keysketch,20)
    body.Placement = Base.Placement(Base.Vector(0,0,base_height+disk_height*2),Base.Rotation(Base.Vector(0,0,1),0))


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
    random.seed(444)

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
        "driver_disk_hole_count": 3,#6,
        "driver_hole_diameter": 11,#5,
        "line_segment_count": 121, #tooth_count squared
        "tooth_pitch": 4,
        "Diameter" : 97,#110,
        "pin_disk_pin_diameter": 4.7,
        "pressure_angle_limit": 50.0,
        "pressure_angle_offset": 0.0,
        "base_height":10.0,
        "disk_height":5.0,
        "shaft_diameter":13.0,
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

    
