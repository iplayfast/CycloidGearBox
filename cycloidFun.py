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
Homepage
"""

import math
import FreeCAD
from FreeCAD import Base
import Part

""" style guide
def functions_are_lowercase(variables_as_well):

class ClassesArePascalCase:

SomeClass.some_variable
"""
def QT_TRANSLATE_NOOP(scope, text):
    return text


def to_polar(x, y):
    return (x ** 2.0 + y ** 2.0) ** 0.5, math.atan2(y, x)


def to_rect(r, a):
    return r * math.cos(a), r * math.sin(a)


def calc_yp(tooth_count, eccentricity, tooth_pitch, a):
    return math.atan(math.sin(tooth_count * a) / (
            math.cos(tooth_count * a) + (tooth_count * tooth_pitch) / (eccentricity * (tooth_count + 1))))


def calc_x(tooth_count, eccentricity, tooth_pitch, roller_diameter: float, a):
    return (tooth_count * tooth_pitch) * math.cos(a) + eccentricity * \
           math.cos((tooth_count + 1) * a) - roller_diameter / 2.0 * \
           math.cos(calc_yp(tooth_count, eccentricity, tooth_pitch, a) + a)


def calc_y(tooth_count: int, eccentricity, tooth_pitch, roller_diameter: float, a):
    return (tooth_count * tooth_pitch) * math.sin(a) + eccentricity * \
           math.sin((tooth_count + 1) * a) - roller_diameter / 2.0 * \
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
        pin_diameter = pin_radius * 2.0
    inset = pin_radius
    angle = 360 / pin_count


    # To draw a epitrachoid, we need r1 (big circle), r2 (small rolling circle) and d (displament of point)
    # r1 + r2 = R = D/2
    # r1/r2 = (N-1)
    # From the above equations: r1 = (N - 1) * R/N, r2 = R/N
    r1 = (pin_count - 1)* outer_diameter / 2 / pin_count
    r2 = outer_diameter / 2 / pin_count
    return r1,r2

def calculate(step : int, eccentricity, r1, r2: float):
    X = (r1 + r2) * math.cos(2 * math.pi * step) + eccentricity * math.cos((r1 + r2) * 2 * math.pi * step / r2)
    Y = (r1 + r2) * math.sin(2 * math.pi * step) + eccentricity * math.sin((r1 + r2) * 2 * math.pi * step / r2)
    return X,Y,0.0

def clean1(a):
    """ return -1 < a < 1 """
    return min(1, max(a, -1))


def calculate_pressure_angle(tooth_count, tooth_pitch, roller_diameter, angle):
    """ calculate the angle of the cycloidalDisk teeth at the angle """
    ex = 2.0 ** 0.5
    r3 = tooth_pitch * tooth_count
    #        p * n
    rg = r3 / ex
    pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - roller_diameter / 2.0
    return math.asin(clean1(((r3 * math.cos(angle) - rg) / (pp + roller_diameter / 2.0)))) * 180 / math.pi


def calculate_pressure_limit(tooth_count, tooth_pitch, eccentricity, roller_diameter, a):
    ex = 2.0 ** 0.5
    r3 = tooth_pitch * tooth_count
    rg = r3 / ex
    q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
    x = rg - eccentricity + (q - roller_diameter / 2.0) * (r3 * math.cos(a) - rg) / q
    y = (q - roller_diameter / 2.0) * r3 * math.sin(a) / q
    return (x ** 2.0 + y ** 2.0) ** 0.5


def check_limit(v: FreeCAD.Vector, pressure_angle_offset, minrad, maxrad):
    """ if x,y outside limit return x,y as at limit, else return x,y
        :type v: FreeCAD.Vector """
    r, a = to_polar(v.x, v.y)
    if (r > maxrad) or (r < minrad):
        r = r - pressure_angle_offset
        v.x, v.y = to_rect(r, a)
    return v


def calculate_min_max_radii(H):
    """ Find the pressure angle limit circles """
    tooth_count= H['tooth_count']
    tooth_pitch= H['tooth_pitch']
    roller_diameter= H['roller_diameter']
    eccentricity= H['eccentricity']
    pressure_angle_limit= H['pressure_angle_limit']

    min_angle = -1.0
    max_angle = -1.0
    for i in range(0, 180):
        x = calculate_pressure_angle(tooth_count, tooth_pitch, roller_diameter, i * math.pi / 180)
        if (x < pressure_angle_limit) and (min_angle < 0):
            min_angle = i * 1.0
        if (x < -pressure_angle_limit) and (max_angle < 0):
            max_angle = i  - 1.0
    min_radius = calculate_pressure_limit(tooth_count, tooth_pitch, eccentricity, roller_diameter, min_angle * math.pi / 180)
    max_radius = calculate_pressure_limit(tooth_count, tooth_pitch, eccentricity, roller_diameter, max_angle * math.pi / 180)
    return min_radius, max_radius

def xy_scale_calculate_min_max_radii(H):
    """ xyscales the minmax radius to pin_disk_diameter proportions

        eg I want 40, max_radius comes out to 46 and change
        divide 40/max_radius to get ratio of 0.86
        multiply both by 0.86...
        """
    pin_disk_diameter = H["pin_disk_diameter"]
    roller_diameter = H["roller_diameter"]
    min_radius, max_radius = calculate_min_max_radii(H)
    if (H["pin_disk_scale"]):
        xy_scale = pin_disk_diameter / (min_radius + roller_diameter * 2)
    else:
        xy_scale = 1.0
    return min_radius, max_radius, xy_scale


def generate_pin_base(H):
    """ create the base that the fixed_ring_pins will be attached to """
    tooth_count = H["tooth_count"]
    tooth_pitch = H["tooth_pitch"]
    roller_diameter = H["roller_diameter"]
    #roller_height = H["roller_height"]
    base_height = H["base_height"]
    driver_disk_height = H["driver_disk_height"]
    shaft_diameter = H["shaft_diameter"]
    cycloidal_disk_height =  H["cycloidal_disk_height"]
    slot_height = H["slot_height"]
    clearance = H["clearance"]
    min_radius, max_radius,xy_scale = xy_scale_calculate_min_max_radii(H)
    #pin_base = Part.makeCylinder(min_radius + roller_diameter*2, base_height) # base of the whole system
    pin_base = Part.makeCylinder(H["pin_disk_diameter"]/2, base_height) # base of the whole system
    dd = Part.makeCylinder(min_radius * 0.75 + clearance, driver_disk_height*2, Base.Vector(0, 0,base_height-driver_disk_height)) #hole for the driver disk to fit in
    pin_base = pin_base.cut(dd)
    roller_height = slot_height #was ... cycloidal_disk_height * 2+driver_disk_height + clearance
    # generate the pin locations
    pin_radius = (min_radius+max_radius)/2.0 + roller_diameter/2
    for i in range(0, tooth_count):
        x = pin_radius * math.cos(2.0 * math.pi * i/tooth_count)
        y = pin_radius * math.sin(2.0 * math.pi * i/tooth_count)

        neg_fixed_ring_pin = Part.makeCylinder(roller_diameter/2.0 +clearance , roller_height, Base.Vector(x, y, 0))
        fixed_ring_pin = Part.makeCylinder(roller_diameter , roller_height, Base.Vector(x, y, base_height))
        fixed_ring_pin_pin = Part.makeCylinder(roller_diameter/2.0 -clearance, base_height / 2.0 +roller_height, Base.Vector(x, y, base_height))
        pin_base = pin_base.cut(neg_fixed_ring_pin) #make a hole if multple gearboxes are in line
        pin_base = pin_base.fuse(fixed_ring_pin_pin) # make the pins the cycloid gear uses, and the Part that goes into the above hole
        pin_base = pin_base.fuse(fixed_ring_pin) # make the pins the cycloid gear uses
    # need hole for eccentric shaft, add a bit so not too tight
    # todo  allow user values for sizes
    # todo allow bearing option
    shaft = Part.makeCylinder(shaft_diameter/ 2.0+clearance,base_height*2,Base.Vector(0,0,-base_height))
    return pin_base.cut(shaft).scale(xy_scale,Base.Vector(1,1,0))

def generate_output_shaft(H):
    min_radius,max_radius,xy_scale = xy_scale_calculate_min_max_radii(H)
    disk_hole_count = H["disk_hole_count"]
    shaft_diameter = H["shaft_diameter"]
    driver_disk_height = H["driver_disk_height"]
    eccentricity = H["eccentricity"]
    roller_diameter = H["roller_diameter"]
    cycloidal_disk_height =  H["cycloidal_disk_height"]
    clearance = H["clearance"]
    base_height = H["base_height"]
    slot_height = H["slot_height"]
    dd = Part.makeCylinder(min_radius * 0.75, driver_disk_height, Base.Vector(0, 0, 0))  # the main driver disk
    #os = Part.makeCylinder(shaft_diameter/2.0,base_height*2,Base.Vector(0,0,0))
    os = Part.makeCylinder(shaft_diameter/2.0,cycloidal_disk_height,Base.Vector(0,0,0))

    slot_size_width, slot_size_height = generate_slot_size(H,True)
    drive_hole1 = Part.makeBox(slot_size_width, slot_size_height-clearance, slot_height,
                              Base.Vector(-slot_size_width + slot_size_width / 2, -slot_size_height + slot_size_height / 2,
                                          0.0))

    os = os.fuse(drive_hole1)
    drive_hole2 = Part.makeBox(slot_size_height, slot_size_width, slot_height-clearance,
                              Base.Vector(-slot_size_height + slot_size_height / 2, -slot_size_width + slot_size_width / 2,
                                          0.0))
    os = os.fuse(drive_hole2)

    """
    slotsize = shaft_diameter / 2
    drive_hole1 = Part.makeBox(slotsize,slotsize / 2,base_height,Base.Vector(-slotsize/2,-slotsize/2+slotsize/4,0.0))
    os = os.fuse(drive_hole1)
    drive_hole2 = Part.makeBox(slotsize / 2,slotsize,base_height,Base.Vector(-slotsize/2+slotsize/4,-slotsize/2,0.0))
    os = os.fuse(drive_hole2)
    """
    dd = dd.fuse(os)
    for i in range(0, disk_hole_count):
        x = min_radius / 2 * math.cos(2.0 * math.pi / (disk_hole_count) * i)
        y = min_radius / 2 * math.sin(2.0 * math.pi / (disk_hole_count) * i)
        fixed_ring_pin = Part.makeCylinder(roller_diameter * 2 - eccentricity+clearance, cycloidal_disk_height * 3, Base.Vector(x, y, -1))  # driver pins
        dd = dd.cut(fixed_ring_pin)
    fp = dd.translate(Base.Vector(0, 0, base_height + cycloidal_disk_height*2))
    return fp.scale(xy_scale,Base.Vector(1,1,0))

def generate_slot_size(H,add_clearence=False):
    shaft_diameter = H["shaft_diameter"]
    clearance = H["clearance"]
    slot_size_width = shaft_diameter / 2
    slot_size_height = shaft_diameter / 4
    if add_clearence:
        slot_size_width += clearance /2
        slot_size_height += clearance /2
    return slot_size_width,slot_size_height


def generate_eccentric_shaft(H):
    min_radius,max_radius,xy_scale = xy_scale_calculate_min_max_radii(H)
    roller_diameter = H["roller_diameter"]
    #roller_height = H["roller_height"]
    eccentricity = H["eccentricity"]
    base_height = H["base_height"]
    shaft_diameter = H["shaft_diameter"]
    driver_disk_height = H["driver_disk_height"]
    cycloidal_disk_height =  H["cycloidal_disk_height"]
    slot_height = H["slot_height"]
    clearance = H["clearance"]
    roller_height = cycloidal_disk_height * 2+driver_disk_height + clearance
    disk_hole_count = H["disk_hole_count"]
    #make shaft and eccentric cylinders
    e = Part.makeCylinder(shaft_diameter / 2.0, cycloidal_disk_height, Base.Vector(-eccentricity , 0,base_height)) #eccentric part
    d = Part.makeCylinder(shaft_diameter/ 2.0,base_height,Base.Vector(0,0,0)) # one base out sticking out the bottom, one base height through the base
    d = d.fuse(e) #base with the excentric disk on top
    #make hole in bottom
    slot_size_width,slot_size_height = generate_slot_size(H)
    drive_hole1 = Part.makeBox(slot_size_width,slot_size_height,slot_height,Base.Vector(-slot_size_width+slot_size_width/2,-slot_size_height+slot_size_height / 2,0.0))
    d = d.cut(drive_hole1)
    drive_hole2 = Part.makeBox(slot_size_height,slot_size_width,slot_height,Base.Vector(-slot_size_height+slot_size_height/2,-slot_size_width+slot_size_width/2,0.0))
    d = d.cut(drive_hole2)
    #make key
    drive_hole3 = Part.makeBox(slot_size_height,slot_size_height,cycloidal_disk_height,Base.Vector(-slot_size_height+2,-slot_size_height+slot_size_height / 2,base_height+cycloidal_disk_height))
    #drive_hole3 = Part.makeBox(slot_size_width,slot_size_height,cycloidal_disk_height,Base.Vector(-slot_size_height,-slot_size_height+slot_size_height / 2,base_height+cycloidal_disk_height))
    d = d.fuse(drive_hole3)
    return d.scale(xy_scale,Base.Vector(1,1,0))

def generate_eccentric_key(H):
    min_radius,max_radius,xy_scale = xy_scale_calculate_min_max_radii(H)
    roller_diameter = H["roller_diameter"]
    #roller_height = H["roller_height"]
    eccentricity = H["eccentricity"]
    base_height = H["base_height"]
    shaft_diameter = H["shaft_diameter"]
    driver_disk_height = H["driver_disk_height"]
    cycloidal_disk_height =  H["cycloidal_disk_height"]
    disk_hole_count = H["disk_hole_count"]
    clearance = H["clearance"]
    roller_height = cycloidal_disk_height * 2+driver_disk_height + clearance
    key = Part.makeCylinder(shaft_diameter / 2.0, cycloidal_disk_height, Base.Vector(eccentricity , 0,base_height+cycloidal_disk_height))
    slot_size_width,slot_size_height = generate_slot_size(H,True)
    drive_hole1 = Part.makeBox(slot_size_height,slot_size_height,cycloidal_disk_height,Base.Vector(-slot_size_height+2,-slot_size_height+slot_size_height / 2,base_height + cycloidal_disk_height))
    #drive_hole1 = Part.makeBox(slot_size_width,slot_size_height,cycloidal_disk_height,Base.Vector(-slot_size_height,-slot_size_height+slot_size_height / 2,base_height + cycloidal_disk_height))
    key = key.cut(drive_hole1)
    return key.scale(xy_scale,Base.Vector(1,1,0))

def generate_cycloidal_disk_array(H):
    tooth_count = H["tooth_count"]-1
    tooth_pitch = H["tooth_pitch"]
    roller_diameter = H["roller_diameter"]
    eccentricity = H["eccentricity"]
    line_segment_count = H["line_segment_count"]
    pressure_angle_offset = H["pressure_angle_offset"]
    """ make the array to be used in the bspline
        that is the cycloidalDisk
    """
    min_radius, max_radius,xy_scale = xy_scale_calculate_min_max_radii(H)
    q = 2.0 * math.pi / line_segment_count
    i = 0
    r1,r2 = calculate_radii(tooth_count,eccentricity,105,10)
    v1 = Base.Vector(calc_x(tooth_count, eccentricity, tooth_pitch, roller_diameter, q * i),
                     calc_y(tooth_count, eccentricity, tooth_pitch, roller_diameter, q * i), 0)
    v1 = check_limit(v1, pressure_angle_offset, min_radius, max_radius)
    va1 = Base.Vector(calculate(0,eccentricity,r1,r2))
    va1 = check_limit(va1, pressure_angle_offset, min_radius, max_radius)
    cycloidal_disk_array = []
    cycloidal_disk_array_alternative = []
    cycloidal_disk_array.append(v1)
    cycloidal_disk_array_alternative.append(va1)
    for i in range(0, line_segment_count):
        v2 = Base.Vector(
            calc_x(tooth_count, eccentricity, tooth_pitch, roller_diameter, q * (i + 1)),
            calc_y(tooth_count, eccentricity, tooth_pitch, roller_diameter, q * (i + 1)),
            0)
        v2 = check_limit(v2, pressure_angle_offset, min_radius, max_radius)
        cycloidal_disk_array.append(v2)
        va2 = Base.Vector(calculate(q * (i + 1), eccentricity, r1, r2))
        va2 = check_limit(va2, pressure_angle_offset, min_radius, max_radius)
        cycloidal_disk_array_alternative.append(va2)
    return cycloidal_disk_array,cycloidal_disk_array_alternative


def generate_cycloidal_disk(H):
    """
    make the complete cycloidal disk
    """
    roller_diameter = H["roller_diameter"]
    eccentricity = H["eccentricity"]
    base_height = H["base_height"]
    shaft_diameter = H["shaft_diameter"]
    cycloidal_disk_height = H["cycloidal_disk_height"]
    disk_hole_count = H["disk_hole_count"]
    clearance = H["clearance"]
    min_radius, max_radius,xy_scale = xy_scale_calculate_min_max_radii(H)
    #get shape of cycloidal disk
    array,alternative_array = generate_cycloidal_disk_array(H)
    #print("array")
    #print(array)
    #print("alternate array")
    #print(alternative_array)
    a = Part.BSplineCurve(array).toShape()
    w = Part.Wire([a])
    f = Part.Face(w)
    # todo add option for bearing here
    es = Part.makeCircle(shaft_diameter /2.0+ clearance,Base.Vector(0,0,0))
    esw = Part.Wire([es])
    esf = Part.Face(esw)
    fc = f.cut(esf)
    for i in range(0, disk_hole_count ):
        x = min_radius/2 * math.cos(2.0 * math.pi * (i / disk_hole_count))
        y = min_radius/2 * math.sin(2.0 * math.pi * (i / disk_hole_count))
        drivingHole= Part.makeCircle(roller_diameter*2+clearance,Base.Vector(x,y,0))
        esw = Part.Wire([drivingHole])
        esf = Part.Face(esw)
        fc = fc.cut(esf)

    #fc = f.fuse(esw)
    e = fc.extrude(FreeCAD.Vector(0, 0, cycloidal_disk_height))
    e.translate(Base.Vector(-eccentricity, 0, base_height + 0.1))
    return e.scale(xy_scale,Base.Vector(1,1,0))

def generate_driver_disk(H):
    min_radius,max_radius,xy_scale = xy_scale_calculate_min_max_radii(H)
    disk_hole_count = H["disk_hole_count"]
    driver_disk_height = H["driver_disk_height"]
    driver_pin_height = H["driver_pin_height"]
    roller_diameter = H["roller_diameter"]
    driver_disk_diameter = H["driver_disk_diameter"]
    #roller_height = H["roller_height"]
    eccentricity = H["eccentricity"]
    shaft_diameter = H["shaft_diameter"]
    base_height = H["base_height"]
    cycloidal_disk_height =  H["cycloidal_disk_height"]
    clearance = H["clearance"]
    #roller_height = cycloidal_disk_height * 2+driver_disk_height + clearance
    #dd = Part.makeCylinder(min_radius * 0.75, driver_disk_height, Base.Vector(0, 0,0)) # the main driver disk
    dd = Part.makeCylinder(driver_disk_diameter/2.0, driver_disk_height, Base.Vector(0, 0,0)) # the main driver disk
    shaft = Part.makeCylinder(shaft_diameter/ 2.0+clearance,driver_disk_height+base_height*2,Base.Vector(0,0,-base_height))
    for i in range(0, disk_hole_count):
        x = min_radius / 2 * math.cos(2.0 * math.pi / (disk_hole_count) * i)
        y = min_radius / 2 * math.sin(2.0 * math.pi / (disk_hole_count) * i)
#        fixed_ring_pin = Part.makeCylinder(roller_diameter*2 - eccentricity , cycloidal_disk_height*3, Base.Vector(x, y, cycloidal_disk_height)) #driver pins
        fixed_ring_pin = Part.makeCylinder(roller_diameter*2 - eccentricity , driver_pin_height, Base.Vector(x, y, cycloidal_disk_height)) #driver pins
        dd = dd.fuse(fixed_ring_pin)

    fp = dd.translate(Base.Vector(0,0,base_height - driver_disk_height))
    # need to make hole for eccentric shaft, add a bit so not to tight
    #todo  allow user values for sizes
    #todo allow bearing option
    fp = fp.cut(shaft)
    return fp.scale(xy_scale,Base.Vector(1,1,0))

def generate_default_hyperparam():
    hyperparameters = {
        "eccentricity": 4.7 / 2,
        "tooth_count": 12,
        "disk_hole_count":6,
        "line_segment_count": 400,
        "tooth_pitch": 4,
        "pin_disk_scale" : False,
        "pin_disk_diameter" : 110,
        "driver_disk_diameter" : 80,
        "roller_diameter": 4.7,
#        "roller_height": 12.0, # roller_height = cycloidal_disk_height * 2+driver_disk_height + clearence
        "center_diameter": 5.0,
        "pressure_angle_limit": 50.0,
        "pressure_angle_offset": 0.0,
        "base_height":10.0,
        "driver_pin_height":10.0,
        "driver_disk_height":4.0,
        "cycloidal_disk_height":4,
        "shaft_diameter":13.0,
        "slot_height" : 10.0,
        "clearance" : 0.5
        }
    return hyperparameters

def test_generate_eccentric_shaft():
    Part.show(generate_eccentric_shaft(generate_default_hyperparam()))

def test_generate_eccentric_key():
    Part.show(generate_eccentric_key(generate_default_hyperparam()))

def test_generate_pin_base():
    Part.show(generate_pin_base(generate_default_hyperparam()))

def test_generate_driver_disk():
    Part.show(generate_driver_disk(generate_default_hyperparam()))

def test_generate_cycloidal_disk():
    Part.show(generate_cycloidal_disk(generate_default_hyperparam()))

def test_generate_output_shaft():
    Part.show(generate_output_shaft(generate_default_hyperparam()))
