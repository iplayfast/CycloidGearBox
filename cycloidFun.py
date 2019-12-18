#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 16:43:09 2019

@author: chris
"""

import math
import FreeCAD
from FreeCAD import Base
import Part


def QT_TRANSLATE_NOOP(scope, text):
    return text


def toPolar(x, y):
    return (x ** 2.0 + y ** 2.0) ** 0.5, math.atan2(y, x)


def toRect(r, a):
    return r * math.cos(a), r * math.sin(a)


def calcyp(ToothCount, Eccentricity, ToothPitch, a):
    return math.atan(math.sin(ToothCount * a) / (
            math.cos(ToothCount * a) + (ToothCount * ToothPitch) / (Eccentricity * (ToothCount + 1))))


def calcX(ToothCount, Eccentricity, ToothPitch, RollerDiameter: float, a):
    return (ToothCount * ToothPitch) * math.cos(a) + Eccentricity * \
           math.cos((ToothCount + 1) * a) - RollerDiameter / 2.0 * \
           math.cos(calcyp(ToothCount, Eccentricity, ToothPitch, a) + a)


def calcY(ToothCount: int, Eccentricity, ToothPitch, RollerDiameter: float, a):
    return (ToothCount * ToothPitch) * math.sin(a) + Eccentricity * \
           math.sin((ToothCount + 1) * a) - RollerDiameter / 2.0 * \
           math.sin(calcyp(ToothCount, Eccentricity, ToothPitch, a) + a)

def CalculateRs(pinCount: int, Eccentricity, OuterDiameter, PinDiameter:float):
    """

    :param pinCount: Number of teeth of cycloidal gear
    :param Eccentricity: offset of cycloidal gear
    :param OuterDiameter: diameter of gear
    :param PinDiameter: diameter of pins
    :return: r1,r2 (formulas used for calculating points along the array)
    """
    OuterRadius = OuterDiameter / 2.0
    PinRadius = PinDiameter / 2.0
    # No less than 3, no more than 50 pins
    if pinCount<3:
        pinCount = 3
    if pinCount>50:
        pinCount = 50
    # e cannot be larger than r (d/2)
    if( Eccentricity > PinRadius ):
        Eccentricity = PinRadius

    # Validate r based on R and N: canot be larger than R * sin(pi/N) or the circles won't fit
    if( PinRadius > OuterRadius * math.sin( math.pi)/ pinCount ):
        PinRadius = OuterRadius * math.sin(math.pi)/ pinCount
        PinDiameter = PinRadius * 2.0
    inset = PinRadius
    angle = 360 / pinCount


    # To draw a epitrachoid, we need r1 (big circle), r2 (small rolling circle) and d (displament of point)
    # r1 + r2 = R = D/2
    # r1/r2 = (N-1)
    # From the above equations: r1 = (N - 1) * R/N, r2 = R/N
    r1 = (pinCount - 1)* OuterDiameter / 2 / pinCount
    r2 = OuterDiameter / 2 / pinCount
    return r1,r2

def calculate(step : int, Eccentricity, r1, r2: float):
    X = (r1 + r2) * math.cos(2 * math.pi * step) + Eccentricity * math.cos((r1 + r2) * 2 * math.pi * step / r2)
    Y = (r1 + r2) * math.sin(2 * math.pi * step) + Eccentricity * math.sin((r1 + r2) * 2 * math.pi * step / r2)
    return X,Y,0.0

def clean1(a):
    """ return -1 < a < 1 """
    return min(1, max(a, -1))


def calcPressureAngle(ToothCount, ToothPitch, RollerDiameter, angle):
    """ calculate the angle of the cycloidalDisk teeth at the angle """
    ex = 2.0 ** 0.5
    r3 = ToothPitch * ToothCount
    #        p * n
    rg = r3 / ex
    pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - RollerDiameter / 2.0
    return math.asin(clean1(((r3 * math.cos(angle) - rg) / (pp + RollerDiameter / 2.0)))) * 180 / math.pi


def calcPressureLimit(ToothCount, ToothPitch, Eccentricity, RollerDiameter, a):
    ex = 2.0 ** 0.5
    r3 = ToothPitch * ToothCount
    rg = r3 / ex
    q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
    x = rg - Eccentricity + (q - RollerDiameter / 2.0) * (r3 * math.cos(a) - rg) / q
    y = (q - RollerDiameter / 2.0) * r3 * math.sin(a) / q
    return (x ** 2.0 + y ** 2.0) ** 0.5


def checkLimit(v: FreeCAD.Vector, PressureAngleOffset, minrad, maxrad):
    """ if x,y outside limit return x,y as at limit, else return x,y
        :type v: FreeCAD.Vector """
    r, a = toPolar(v.x, v.y)
    if (r > maxrad) or (r < minrad):
        r = r - PressureAngleOffset
        v.x, v.y = toRect(r, a)
    return v


def minmaxRadius(H):
    """ Find the pressure angle limit circles """
    ToothCount= H['ToothCount']
    ToothPitch= H['ToothPitch']
    RollerDiameter= H['RollerDiameter']
    Eccentricity= H['Eccentricity']
    PressureAngleLimit= H['PressureAngleLimit']

    minAngle = -1.0
    maxAngle = -1.0
    for i in range(0, 180):
        x = calcPressureAngle(ToothCount, ToothPitch, RollerDiameter, i * math.pi / 180)
        if (x < PressureAngleLimit) and (minAngle < 0):
            minAngle = i * 1.0
        if (x < -PressureAngleLimit) and (maxAngle < 0):
            maxAngle = i  - 1.0
    minRadius = calcPressureLimit(ToothCount, ToothPitch, Eccentricity, RollerDiameter, minAngle * math.pi / 180)
    maxRadius = calcPressureLimit(ToothCount, ToothPitch, Eccentricity, RollerDiameter, maxAngle * math.pi / 180)
    return minRadius, maxRadius


def generatePinBase(H):
    """ create the base that the fixedRingPins will be attached to """
    ToothCount = H["ToothCount"]
    ToothPitch = H["ToothPitch"]
    RollerDiameter = H["RollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    BaseHeight = H["BaseHeight"]
    DriverDiskHeight = H["DriverDiskHeight"]
    ShaftDiameter = H["ShaftDiameter"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    clearance = H["clearance"]
    minRadius, maxRadius = minmaxRadius(H)
    pinBase = Part.makeCylinder(minRadius + RollerDiameter*2, BaseHeight) # base of the whole system
    dd = Part.makeCylinder(minRadius * 0.75 + clearance, DriverDiskHeight*2, Base.Vector(0, 0,BaseHeight-DriverDiskHeight)) #hole for the driver disk to fit in
    pinBase = pinBase.cut(dd)
    RollerHeight = CycloidalDiskHeight * 2+DriverDiskHeight + clearance
    # generate the pin locations
    pinRadius = (minRadius+maxRadius)/2.0 + RollerDiameter/2
    for i in range(0, ToothCount):
        x = pinRadius * math.cos(2.0 * math.pi * i/ToothCount)
        y = pinRadius * math.sin(2.0 * math.pi * i/ToothCount)

        negfixedRingPin = Part.makeCylinder(RollerDiameter/2.0 +clearance , RollerHeight, Base.Vector(x, y, 0))
        fixedRingPin = Part.makeCylinder(RollerDiameter , RollerHeight, Base.Vector(x, y, BaseHeight))
        fixedRingPinpin = Part.makeCylinder(RollerDiameter/2.0 -clearance, BaseHeight / 2.0 +RollerHeight, Base.Vector(x, y, BaseHeight))
        pinBase = pinBase.cut(negfixedRingPin) #make a hole if multple gearboxes are in line
        pinBase = pinBase.fuse(fixedRingPinpin) # make the pins the cycloid gear uses, and the Part that goes into the above hole
        pinBase = pinBase.fuse(fixedRingPin) # make the pins the cycloid gear uses
    # need hole for eccentric shaft, add a bit so not too tight
    # todo  allow user values for sizes
    # todo allow bearing option
    shaft = Part.makeCylinder(ShaftDiameter/ 2.0+clearance,BaseHeight*2,Base.Vector(0,0,-BaseHeight))
    return pinBase.cut(shaft)

def generateOutputShaft(H):
    minRadius,maxRadius = minmaxRadius(H)
    DiskHoleCount = H["DiskHoleCount"]
    ShaftDiameter = H["ShaftDiameter"]
    DriverDiskHeight = H["DriverDiskHeight"]
    Eccentricity = H["Eccentricity"]
    RollerDiameter = H["RollerDiameter"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    clearance = H["clearance"]
    BaseHeight = H["BaseHeight"]
    dd = Part.makeCylinder(minRadius * 0.75, DriverDiskHeight, Base.Vector(0, 0, 0))  # the main driver disk
    #os = Part.makeCylinder(ShaftDiameter/2.0,BaseHeight*2,Base.Vector(0,0,0))
    os = Part.makeCylinder(ShaftDiameter/2.0,CycloidalDiskHeight,Base.Vector(0,0,0))
    slotsize = ShaftDiameter / 2
    drivehole1 = Part.makeBox(slotsize,slotsize / 2,BaseHeight,Base.Vector(-slotsize/2,-slotsize/2+slotsize/4,0.0))
    os = os.fuse(drivehole1)
    drivehole2 = Part.makeBox(slotsize / 2,slotsize,BaseHeight,Base.Vector(-slotsize/2+slotsize/4,-slotsize/2,0.0))
    os = os.fuse(drivehole2)

    dd = dd.fuse(os)
    for i in range(0, DiskHoleCount):
        x = minRadius / 2 * math.cos(2.0 * math.pi / (DiskHoleCount) * i)
        y = minRadius / 2 * math.sin(2.0 * math.pi / (DiskHoleCount) * i)
        fixedringpin = Part.makeCylinder(RollerDiameter * 2 - Eccentricity+clearance, CycloidalDiskHeight * 3, Base.Vector(x, y, -1))  # driver pins
        dd = dd.cut(fixedringpin)
    fp = dd.translate(Base.Vector(0, 0, BaseHeight + CycloidalDiskHeight*2))
    return fp
def generateSlotSize(H,addClearence=False):
    ShaftDiameter = H["ShaftDiameter"]
    clearance = H["clearance"]
    slotsizeWidth = ShaftDiameter / 2
    slotsizeHeight = ShaftDiameter / 4
    if addClearence:
        slotsizeWidth += clearance /2
        slotsizeHeight += clearance /2
    return slotsizeWidth,slotsizeHeight


def generateEccentricShaft(H):
    minRadius,maxRadius = minmaxRadius(H)
    RollerDiameter = H["RollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    Eccentricity = H["Eccentricity"]
    BaseHeight = H["BaseHeight"]
    ShaftDiameter = H["ShaftDiameter"]
    DriverDiskHeight = H["DriverDiskHeight"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    clearance = H["clearance"]
    RollerHeight = CycloidalDiskHeight * 2+DriverDiskHeight + clearance
    DiskHoleCount = H["DiskHoleCount"]
    e = Part.makeCylinder(ShaftDiameter / 2.0, CycloidalDiskHeight, Base.Vector(-Eccentricity , 0,BaseHeight))
    d = Part.makeCylinder(ShaftDiameter/ 2.0,BaseHeight,Base.Vector(0,0,0)) # one base out sticking out the bottom, one base height through the base
    d = d.fuse(e)
    slotsizeWidth,slotsizeHeight = generateSlotSize(H)
    drivehole1 = Part.makeBox(slotsizeWidth,slotsizeHeight,BaseHeight,Base.Vector(-slotsizeWidth+slotsizeWidth/2,-slotsizeHeight+slotsizeHeight / 2,0.0))

    d = d.cut(drivehole1)
    drivehole2 = Part.makeBox(slotsizeHeight,slotsizeWidth,BaseHeight,Base.Vector(-slotsizeHeight+slotsizeHeight/2,-slotsizeWidth+slotsizeWidth/2,0.0))
    d = d.cut(drivehole2)
    drivehole3 = Part.makeBox(slotsizeHeight,slotsizeHeight,CycloidalDiskHeight,Base.Vector(-slotsizeHeight+2,-slotsizeHeight+slotsizeHeight / 2,BaseHeight+CycloidalDiskHeight))
    #drivehole3 = Part.makeBox(slotsizeWidth,slotsizeHeight,CycloidalDiskHeight,Base.Vector(-slotsizeHeight,-slotsizeHeight+slotsizeHeight / 2,BaseHeight+CycloidalDiskHeight))
    d = d.fuse(drivehole3)
    return d

def generateEccentricKey(H):
    minRadius,maxRadius = minmaxRadius(H)
    RollerDiameter = H["RollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    Eccentricity = H["Eccentricity"]
    BaseHeight = H["BaseHeight"]
    ShaftDiameter = H["ShaftDiameter"]
    DriverDiskHeight = H["DriverDiskHeight"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    DiskHoleCount = H["DiskHoleCount"]
    clearance = H["clearance"]
    RollerHeight = CycloidalDiskHeight * 2+DriverDiskHeight + clearance
    key = Part.makeCylinder(ShaftDiameter / 2.0, CycloidalDiskHeight, Base.Vector(Eccentricity , 0,BaseHeight+CycloidalDiskHeight))
    slotsizeWidth,slotsizeHeight = generateSlotSize(H,True)
    drivehole1 = Part.makeBox(slotsizeHeight,slotsizeHeight,CycloidalDiskHeight,Base.Vector(-slotsizeHeight+2,-slotsizeHeight+slotsizeHeight / 2,BaseHeight + CycloidalDiskHeight))
    #drivehole1 = Part.makeBox(slotsizeWidth,slotsizeHeight,CycloidalDiskHeight,Base.Vector(-slotsizeHeight,-slotsizeHeight+slotsizeHeight / 2,BaseHeight + CycloidalDiskHeight))
    key = key.cut(drivehole1)
    return key

def generateCycloidalDiskArray(H):
    ToothCount = H["ToothCount"]-1
    ToothPitch = H["ToothPitch"]
    RollerDiameter = H["RollerDiameter"]
    Eccentricity = H["Eccentricity"]
    LineSegmentCount = H["LineSegmentCount"]
    PressureAngleOffset = H["PressureAngleOffset"]
    """ make the array to be used in the bspline
        that is the cycloidalDisk
    """
    minRadius, maxRadius = minmaxRadius(H)
    q = 2.0 * math.pi / LineSegmentCount
    i = 0
    r1,r2 = CalculateRs(ToothCount,Eccentricity,105,10)
    v1 = Base.Vector(calcX(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * i),
                     calcY(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * i), 0)
    v1 = checkLimit(v1, PressureAngleOffset, minRadius, maxRadius)
    va1 = Base.Vector(calculate(0,Eccentricity,r1,r2))
    va1 = checkLimit(va1, PressureAngleOffset, minRadius, maxRadius)
    cycloidalDiskArray = []
    cycloidalDiskArrayAlternative = []
    cycloidalDiskArray.append(v1)
    cycloidalDiskArrayAlternative.append(va1)
    for i in range(0, LineSegmentCount):
        v2 = Base.Vector(
            calcX(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * (i + 1)),
            calcY(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * (i + 1)),
            0)
        v2 = checkLimit(v2, PressureAngleOffset, minRadius, maxRadius)
        cycloidalDiskArray.append(v2)
        va2 = Base.Vector(calculate(q * (i + 1), Eccentricity, r1, r2))
        va2 = checkLimit(va2, PressureAngleOffset, minRadius, maxRadius)
        cycloidalDiskArrayAlternative.append(va2)
    return cycloidalDiskArray,cycloidalDiskArrayAlternative


def generateCycloidalDisk(H):
    """
    make the complete cycloidal disk
    """
    RollerDiameter = H["RollerDiameter"]
    Eccentricity = H["Eccentricity"]
    BaseHeight = H["BaseHeight"]
    ShaftDiameter = H["ShaftDiameter"]
    CycloidalDiskHeight = H["CycloidalDiskHeight"]
    DiskHoleCount = H["DiskHoleCount"]
    clearance = H["clearance"]
    minRadius, maxRadius = minmaxRadius(H)
    #get shape of cycloidal disk
    array,alternativearray = generateCycloidalDiskArray(H)
    #print("array")
    #print(array)
    #print("alternate array")
    #print(alternativearray)
    a = Part.BSplineCurve(array).toShape()
    w = Part.Wire([a])
    f = Part.Face(w)
    # todo add option for bearing here
    es = Part.makeCircle(ShaftDiameter /2.0+ clearance,Base.Vector(0,0,0))
    esw = Part.Wire([es])
    esf = Part.Face(esw)
    fc = f.cut(esf)
    for i in range(0, DiskHoleCount ):
        x = minRadius/2 * math.cos(2.0 * math.pi * (i / DiskHoleCount))
        y = minRadius/2 * math.sin(2.0 * math.pi * (i / DiskHoleCount))
        drivinghole= Part.makeCircle(RollerDiameter*2+clearance,Base.Vector(x,y,0))
        esw = Part.Wire([drivinghole])
        esf = Part.Face(esw)
        fc = fc.cut(esf)

    #fc = f.fuse(esw)
    e = fc.extrude(FreeCAD.Vector(0, 0, CycloidalDiskHeight))
    e.translate(Base.Vector(-Eccentricity, 0, BaseHeight + 0.1))
    return e

def generateDriverDisk(H):
    minRadius,maxRadius = minmaxRadius(H)
    DiskHoleCount = H["DiskHoleCount"]
    DriverDiskHeight = H["DriverDiskHeight"]
    RollerDiameter = H["RollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    Eccentricity = H["Eccentricity"]
    ShaftDiameter = H["ShaftDiameter"]
    BaseHeight = H["BaseHeight"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    clearance = H["clearance"]
    RollerHeight = CycloidalDiskHeight * 2+DriverDiskHeight + clearance
    dd = Part.makeCylinder(minRadius * 0.75, DriverDiskHeight, Base.Vector(0, 0,0)) # the main driver disk
    shaft = Part.makeCylinder(ShaftDiameter/ 2.0+clearance,DriverDiskHeight+BaseHeight*2,Base.Vector(0,0,-BaseHeight))
    for i in range(0, DiskHoleCount):
        x = minRadius / 2 * math.cos(2.0 * math.pi / (DiskHoleCount) * i)
        y = minRadius / 2 * math.sin(2.0 * math.pi / (DiskHoleCount) * i)
        fixedringpin = Part.makeCylinder(RollerDiameter*2 - Eccentricity , CycloidalDiskHeight*3, Base.Vector(x, y, CycloidalDiskHeight)) #driver pins
        dd = dd.fuse(fixedringpin)

    fp = dd.translate(Base.Vector(0,0,BaseHeight - DriverDiskHeight))
    # need to make hole for eccentric shaft, add a bit so not to tight
    #todo  allow user values for sizes
    #todo allow bearing option
    fp = fp.cut(shaft)
    return fp

def generateDefaultHyperParam():
    hyperparameters = {
        "Eccentricity": 4.7 / 2,
        "ToothCount": 12,
        "DiskHoleCount":6,
        "LineSegmentCount": 400,
        "ToothPitch": 4,
        "RollerDiameter": 4.7,
#        "RollerHeight": 12.0, # RollerHeight = CycloidalDiskHeight * 2+DriverDiskHeight + clearence
        "CenterDiameter": 5.0,
        "PressureAngleLimit": 50.0,
        "PressureAngleOffset": 0.0,
        "BaseHeight":10.0,
        "DriverPinHeight":10.0,
        "DriverDiskHeight":4.0,
        "CycloidalDiskHeight":4,
        "ShaftDiameter":13.0,
        "clearance" : 0.5
        }
    return hyperparameters

def testgenerateEccentricShaft():
    Part.show(generateEccentricShaft(generateDefaultHyperParam()))

def testgenerateEccentricKey():
    Part.show(generateEccentricKey(generateDefaultHyperParam()))

def testgeneratePinBase():
    Part.show(generatePinBase(generateDefaultHyperParam()))

def testgenerateDriverDisk():
    Part.show(generateDriverDisk(generateDefaultHyperParam()))

def testgenerateCycloidalDisk():
    Part.show(generateCycloidalDisk(generateDefaultHyperParam()))

def testgenerateOutputShaft():
    Part.show(generateOutputShaft(generateDefaultHyperParam()))
