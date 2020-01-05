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


def QT_TRANSLATE_NOOP(scope, text):
    return text


def toPolar(x, y):
    return (x ** 2.0 + y ** 2.0) ** 0.5, math.atan2(y, x)


def toRect(r, a):
    return r * math.cos(a), r * math.sin(a)


def calcyp(toothCount, eccentricity, toothPitch, a):
    return math.atan(math.sin(toothCount * a) / (
            math.cos(toothCount * a) + (toothCount * toothPitch) / (eccentricity * (toothCount + 1))))


def calcX(toothCount, eccentricity, toothPitch, rollerDiameter: float, a):
    return (toothCount * toothPitch) * math.cos(a) + eccentricity * \
           math.cos((toothCount + 1) * a) - rollerDiameter / 2.0 * \
           math.cos(calcyp(toothCount, eccentricity, toothPitch, a) + a)


def calcY(toothCount: int, eccentricity, toothPitch, rollerDiameter: float, a):
    return (toothCount * toothPitch) * math.sin(a) + eccentricity * \
           math.sin((toothCount + 1) * a) - rollerDiameter / 2.0 * \
           math.sin(calcyp(toothCount, eccentricity, toothPitch, a) + a)

def CalculateRs(pinCount: int, eccentricity, OuterDiameter, PinDiameter:float):
    """

    :param pinCount: Number of teeth of cycloidal gear
    :param eccentricity: offset of cycloidal gear
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
    if( eccentricity > PinRadius ):
        eccentricity = PinRadius

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

def calculate(step : int, eccentricity, r1, r2: float):
    X = (r1 + r2) * math.cos(2 * math.pi * step) + eccentricity * math.cos((r1 + r2) * 2 * math.pi * step / r2)
    Y = (r1 + r2) * math.sin(2 * math.pi * step) + eccentricity * math.sin((r1 + r2) * 2 * math.pi * step / r2)
    return X,Y,0.0

def clean1(a):
    """ return -1 < a < 1 """
    return min(1, max(a, -1))


def calcPressureAngle(toothCount, toothPitch, rollerDiameter, angle):
    """ calculate the angle of the cycloidalDisk teeth at the angle """
    ex = 2.0 ** 0.5
    r3 = toothPitch * toothCount
    #        p * n
    rg = r3 / ex
    pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - rollerDiameter / 2.0
    return math.asin(clean1(((r3 * math.cos(angle) - rg) / (pp + rollerDiameter / 2.0)))) * 180 / math.pi


def calcPressureLimit(toothCount, toothPitch, eccentricity, rollerDiameter, a):
    ex = 2.0 ** 0.5
    r3 = toothPitch * toothCount
    rg = r3 / ex
    q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
    x = rg - eccentricity + (q - rollerDiameter / 2.0) * (r3 * math.cos(a) - rg) / q
    y = (q - rollerDiameter / 2.0) * r3 * math.sin(a) / q
    return (x ** 2.0 + y ** 2.0) ** 0.5


def checkLimit(v: FreeCAD.Vector, pressureAngleOffset, minrad, maxrad):
    """ if x,y outside limit return x,y as at limit, else return x,y
        :type v: FreeCAD.Vector """
    r, a = toPolar(v.x, v.y)
    if (r > maxrad) or (r < minrad):
        r = r - pressureAngleOffset
        v.x, v.y = toRect(r, a)
    return v


def MinMaxRadius(H):
    """ Find the pressure angle limit circles """
    toothCount= H['toothCount']
    toothPitch= H['toothPitch']
    rollerDiameter= H['rollerDiameter']
    eccentricity= H['eccentricity']
    pressureAngleLimit= H['pressureAngleLimit']

    minAngle = -1.0
    maxAngle = -1.0
    for i in range(0, 180):
        x = calcPressureAngle(toothCount, toothPitch, rollerDiameter, i * math.pi / 180)
        if (x < pressureAngleLimit) and (minAngle < 0):
            minAngle = i * 1.0
        if (x < -pressureAngleLimit) and (maxAngle < 0):
            maxAngle = i  - 1.0
    minRadius = calcPressureLimit(toothCount, toothPitch, eccentricity, rollerDiameter, minAngle * math.pi / 180)
    maxRadius = calcPressureLimit(toothCount, toothPitch, eccentricity, rollerDiameter, maxAngle * math.pi / 180)
    return minRadius, maxRadius

def xyScaleMinMaxRadius(H):
    """ xyscales the minmax radius to pinDiskDiameter proportions

        eg I want 40, maxRadius comes out to 46 and change
        divide 40/maxRadius to get ratio of 0.86
        multiply both by 0.86...
        """
    pinDiskDiameter = H["pinDiskDiameter"]
    rollerDiameter = H["rollerDiameter"]
    minRadius, maxRadius = MinMaxRadius(H)
    xyScale = pinDiskDiameter / (minRadius + rollerDiameter * 2)
    return minRadius, maxRadius, xyScale


def generatePinBase(H):
    """ create the base that the fixedRingPins will be attached to """
    toothCount = H["toothCount"]
    toothPitch = H["toothPitch"]
    rollerDiameter = H["rollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    baseHeight = H["baseHeight"]
    driverDiskHeight = H["driverDiskHeight"]
    shaftDiameter = H["shaftDiameter"]
    cycloidalDiskHeight =  H["cycloidalDiskHeight"]
    clearance = H["clearance"]
    minRadius, maxRadius,xyScale = xyScaleMinMaxRadius(H)
    pinBase = Part.makeCylinder(minRadius + rollerDiameter*2, baseHeight) # base of the whole system
    dd = Part.makeCylinder(minRadius * 0.75 + clearance, driverDiskHeight*2, Base.Vector(0, 0,baseHeight-driverDiskHeight)) #hole for the driver disk to fit in
    pinBase = pinBase.cut(dd)
    RollerHeight = cycloidalDiskHeight * 2+driverDiskHeight + clearance
    # generate the pin locations
    pinRadius = (minRadius+maxRadius)/2.0 + rollerDiameter/2
    for i in range(0, toothCount):
        x = pinRadius * math.cos(2.0 * math.pi * i/toothCount)
        y = pinRadius * math.sin(2.0 * math.pi * i/toothCount)

        negfixedRingPin = Part.makeCylinder(rollerDiameter/2.0 +clearance , RollerHeight, Base.Vector(x, y, 0))
        fixedRingPin = Part.makeCylinder(rollerDiameter , RollerHeight, Base.Vector(x, y, baseHeight))
        fixedRingPinpin = Part.makeCylinder(rollerDiameter/2.0 -clearance, baseHeight / 2.0 +RollerHeight, Base.Vector(x, y, baseHeight))
        pinBase = pinBase.cut(negfixedRingPin) #make a hole if multple gearboxes are in line
        pinBase = pinBase.fuse(fixedRingPinpin) # make the pins the cycloid gear uses, and the Part that goes into the above hole
        pinBase = pinBase.fuse(fixedRingPin) # make the pins the cycloid gear uses
    # need hole for eccentric shaft, add a bit so not too tight
    # todo  allow user values for sizes
    # todo allow bearing option
    shaft = Part.makeCylinder(shaftDiameter/ 2.0+clearance,baseHeight*2,Base.Vector(0,0,-baseHeight))
    return pinBase.cut(shaft).scale(xyScale,Base.Vector(1,1,0))

def generateOutputShaft(H):
    minRadius,maxRadius,xyScale = xyScaleMinMaxRadius(H)
    diskHoleCount = H["diskHoleCount"]
    shaftDiameter = H["shaftDiameter"]
    driverDiskHeight = H["driverDiskHeight"]
    eccentricity = H["eccentricity"]
    rollerDiameter = H["rollerDiameter"]
    cycloidalDiskHeight =  H["cycloidalDiskHeight"]
    clearance = H["clearance"]
    baseHeight = H["baseHeight"]
    dd = Part.makeCylinder(minRadius * 0.75, driverDiskHeight, Base.Vector(0, 0, 0))  # the main driver disk
    #os = Part.makeCylinder(shaftDiameter/2.0,baseHeight*2,Base.Vector(0,0,0))
    os = Part.makeCylinder(shaftDiameter/2.0,cycloidalDiskHeight,Base.Vector(0,0,0))

    slotsizeWidth, slotsizeHeight = generateSlotSize(H,True)
    driveHole1 = Part.makeBox(slotsizeWidth, slotsizeHeight, baseHeight,
                              Base.Vector(-slotsizeWidth + slotsizeWidth / 2, -slotsizeHeight + slotsizeHeight / 2,
                                          0.0))

    os = os.fuse(driveHole1)
    driveHole2 = Part.makeBox(slotsizeHeight, slotsizeWidth, baseHeight,
                              Base.Vector(-slotsizeHeight + slotsizeHeight / 2, -slotsizeWidth + slotsizeWidth / 2,
                                          0.0))
    os = os.fuse(driveHole2)

    """
    slotsize = shaftDiameter / 2
    driveHole1 = Part.makeBox(slotsize,slotsize / 2,baseHeight,Base.Vector(-slotsize/2,-slotsize/2+slotsize/4,0.0))
    os = os.fuse(driveHole1)
    driveHole2 = Part.makeBox(slotsize / 2,slotsize,baseHeight,Base.Vector(-slotsize/2+slotsize/4,-slotsize/2,0.0))
    os = os.fuse(driveHole2)
    """
    dd = dd.fuse(os)
    for i in range(0, diskHoleCount):
        x = minRadius / 2 * math.cos(2.0 * math.pi / (diskHoleCount) * i)
        y = minRadius / 2 * math.sin(2.0 * math.pi / (diskHoleCount) * i)
        fixedringpin = Part.makeCylinder(rollerDiameter * 2 - eccentricity+clearance, cycloidalDiskHeight * 3, Base.Vector(x, y, -1))  # driver pins
        dd = dd.cut(fixedringpin)
    fp = dd.translate(Base.Vector(0, 0, baseHeight + cycloidalDiskHeight*2))
    return fp.scale(xyScale,Base.Vector(1,1,0))

def generateSlotSize(H,addClearence=False):
    shaftDiameter = H["shaftDiameter"]
    clearance = H["clearance"]
    slotsizeWidth = shaftDiameter / 2
    slotsizeHeight = shaftDiameter / 4
    if addClearence:
        slotsizeWidth += clearance /2
        slotsizeHeight += clearance /2
    return slotsizeWidth,slotsizeHeight


def generateEccentricShaft(H):
    minRadius,maxRadius,xyScale = xyScaleMinMaxRadius(H)
    rollerDiameter = H["rollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    eccentricity = H["eccentricity"]
    baseHeight = H["baseHeight"]
    shaftDiameter = H["shaftDiameter"]
    driverDiskHeight = H["driverDiskHeight"]
    cycloidalDiskHeight =  H["cycloidalDiskHeight"]
    clearance = H["clearance"]
    RollerHeight = cycloidalDiskHeight * 2+driverDiskHeight + clearance
    diskHoleCount = H["diskHoleCount"]
    e = Part.makeCylinder(shaftDiameter / 2.0, cycloidalDiskHeight, Base.Vector(-eccentricity , 0,baseHeight))
    d = Part.makeCylinder(shaftDiameter/ 2.0,baseHeight,Base.Vector(0,0,0)) # one base out sticking out the bottom, one base height through the base
    d = d.fuse(e)
    slotsizeWidth,slotsizeHeight = generateSlotSize(H)
    driveHole1 = Part.makeBox(slotsizeWidth,slotsizeHeight,baseHeight,Base.Vector(-slotsizeWidth+slotsizeWidth/2,-slotsizeHeight+slotsizeHeight / 2,0.0))

    d = d.cut(driveHole1)
    driveHole2 = Part.makeBox(slotsizeHeight,slotsizeWidth,baseHeight,Base.Vector(-slotsizeHeight+slotsizeHeight/2,-slotsizeWidth+slotsizeWidth/2,0.0))
    d = d.cut(driveHole2)
    driveHole3 = Part.makeBox(slotsizeHeight,slotsizeHeight,cycloidalDiskHeight,Base.Vector(-slotsizeHeight+2,-slotsizeHeight+slotsizeHeight / 2,baseHeight+cycloidalDiskHeight))
    #driveHole3 = Part.makeBox(slotsizeWidth,slotsizeHeight,cycloidalDiskHeight,Base.Vector(-slotsizeHeight,-slotsizeHeight+slotsizeHeight / 2,baseHeight+cycloidalDiskHeight))
    d = d.fuse(driveHole3)
    return d.scale(xyScale,Base.Vector(1,1,0))

def generateEccentricKey(H):
    minRadius,maxRadius,xyScale = xyScaleMinMaxRadius(H)
    rollerDiameter = H["rollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    eccentricity = H["eccentricity"]
    baseHeight = H["baseHeight"]
    shaftDiameter = H["shaftDiameter"]
    driverDiskHeight = H["driverDiskHeight"]
    cycloidalDiskHeight =  H["cycloidalDiskHeight"]
    diskHoleCount = H["diskHoleCount"]
    clearance = H["clearance"]
    RollerHeight = cycloidalDiskHeight * 2+driverDiskHeight + clearance
    key = Part.makeCylinder(shaftDiameter / 2.0, cycloidalDiskHeight, Base.Vector(eccentricity , 0,baseHeight+cycloidalDiskHeight))
    slotsizeWidth,slotsizeHeight = generateSlotSize(H,True)
    driveHole1 = Part.makeBox(slotsizeHeight,slotsizeHeight,cycloidalDiskHeight,Base.Vector(-slotsizeHeight+2,-slotsizeHeight+slotsizeHeight / 2,baseHeight + cycloidalDiskHeight))
    #driveHole1 = Part.makeBox(slotsizeWidth,slotsizeHeight,cycloidalDiskHeight,Base.Vector(-slotsizeHeight,-slotsizeHeight+slotsizeHeight / 2,baseHeight + cycloidalDiskHeight))
    key = key.cut(driveHole1)
    return key.scale(xyScale,Base.Vector(1,1,0))

def generateCycloidalDiskArray(H):
    toothCount = H["toothCount"]-1
    toothPitch = H["toothPitch"]
    rollerDiameter = H["rollerDiameter"]
    eccentricity = H["eccentricity"]
    lineSegmentCount = H["lineSegmentCount"]
    pressureAngleOffset = H["pressureAngleOffset"]
    """ make the array to be used in the bspline
        that is the cycloidalDisk
    """
    minRadius, maxRadius,xyScale = xyScaleMinMaxRadius(H)
    q = 2.0 * math.pi / lineSegmentCount
    i = 0
    r1,r2 = CalculateRs(toothCount,eccentricity,105,10)
    v1 = Base.Vector(calcX(toothCount, eccentricity, toothPitch, rollerDiameter, q * i),
                     calcY(toothCount, eccentricity, toothPitch, rollerDiameter, q * i), 0)
    v1 = checkLimit(v1, pressureAngleOffset, minRadius, maxRadius)
    va1 = Base.Vector(calculate(0,eccentricity,r1,r2))
    va1 = checkLimit(va1, pressureAngleOffset, minRadius, maxRadius)
    cycloidalDiskArray = []
    cycloidalDiskArrayAlternative = []
    cycloidalDiskArray.append(v1)
    cycloidalDiskArrayAlternative.append(va1)
    for i in range(0, lineSegmentCount):
        v2 = Base.Vector(
            calcX(toothCount, eccentricity, toothPitch, rollerDiameter, q * (i + 1)),
            calcY(toothCount, eccentricity, toothPitch, rollerDiameter, q * (i + 1)),
            0)
        v2 = checkLimit(v2, pressureAngleOffset, minRadius, maxRadius)
        cycloidalDiskArray.append(v2)
        va2 = Base.Vector(calculate(q * (i + 1), eccentricity, r1, r2))
        va2 = checkLimit(va2, pressureAngleOffset, minRadius, maxRadius)
        cycloidalDiskArrayAlternative.append(va2)
    return cycloidalDiskArray,cycloidalDiskArrayAlternative


def generateCycloidalDisk(H):
    """
    make the complete cycloidal disk
    """
    rollerDiameter = H["rollerDiameter"]
    eccentricity = H["eccentricity"]
    baseHeight = H["baseHeight"]
    shaftDiameter = H["shaftDiameter"]
    cycloidalDiskHeight = H["cycloidalDiskHeight"]
    diskHoleCount = H["diskHoleCount"]
    clearance = H["clearance"]
    minRadius, maxRadius,xyScale = xyScaleMinMaxRadius(H)
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
    es = Part.makeCircle(shaftDiameter /2.0+ clearance,Base.Vector(0,0,0))
    esw = Part.Wire([es])
    esf = Part.Face(esw)
    fc = f.cut(esf)
    for i in range(0, diskHoleCount ):
        x = minRadius/2 * math.cos(2.0 * math.pi * (i / diskHoleCount))
        y = minRadius/2 * math.sin(2.0 * math.pi * (i / diskHoleCount))
        drivingHole= Part.makeCircle(rollerDiameter*2+clearance,Base.Vector(x,y,0))
        esw = Part.Wire([drivingHole])
        esf = Part.Face(esw)
        fc = fc.cut(esf)

    #fc = f.fuse(esw)
    e = fc.extrude(FreeCAD.Vector(0, 0, cycloidalDiskHeight))
    e.translate(Base.Vector(-eccentricity, 0, baseHeight + 0.1))
    return e.scale(xyScale,Base.Vector(1,1,0))

def generateDriverDisk(H):
    minRadius,maxRadius,xyScale = xyScaleMinMaxRadius(H)
    diskHoleCount = H["diskHoleCount"]
    driverDiskHeight = H["driverDiskHeight"]
    rollerDiameter = H["rollerDiameter"]
    #RollerHeight = H["RollerHeight"]
    eccentricity = H["eccentricity"]
    shaftDiameter = H["shaftDiameter"]
    baseHeight = H["baseHeight"]
    cycloidalDiskHeight =  H["cycloidalDiskHeight"]
    clearance = H["clearance"]
    RollerHeight = cycloidalDiskHeight * 2+driverDiskHeight + clearance
    dd = Part.makeCylinder(minRadius * 0.75, driverDiskHeight, Base.Vector(0, 0,0)) # the main driver disk
    shaft = Part.makeCylinder(shaftDiameter/ 2.0+clearance,driverDiskHeight+baseHeight*2,Base.Vector(0,0,-baseHeight))
    for i in range(0, diskHoleCount):
        x = minRadius / 2 * math.cos(2.0 * math.pi / (diskHoleCount) * i)
        y = minRadius / 2 * math.sin(2.0 * math.pi / (diskHoleCount) * i)
        fixedringpin = Part.makeCylinder(rollerDiameter*2 - eccentricity , cycloidalDiskHeight*3, Base.Vector(x, y, cycloidalDiskHeight)) #driver pins
        dd = dd.fuse(fixedringpin)

    fp = dd.translate(Base.Vector(0,0,baseHeight - driverDiskHeight))
    # need to make hole for eccentric shaft, add a bit so not to tight
    #todo  allow user values for sizes
    #todo allow bearing option
    fp = fp.cut(shaft)
    return fp.scale(xyScale,Base.Vector(1,1,0))

def generateDefaultHyperParam():
    hyperparameters = {
        "eccentricity": 4.7 / 2,
        "toothCount": 12,
        "diskHoleCount":6,
        "lineSegmentCount": 400,
        "toothPitch": 4,
        "pinDiskDiameter" : 40,
        "rollerDiameter": 4.7,
#        "RollerHeight": 12.0, # RollerHeight = cycloidalDiskHeight * 2+driverDiskHeight + clearence
        "centerDiameter": 5.0,
        "pressureAngleLimit": 50.0,
        "pressureAngleOffset": 0.0,
        "baseHeight":10.0,
        "driverPinHeight":10.0,
        "driverDiskHeight":4.0,
        "cycloidalDiskHeight":4,
        "shaftDiameter":13.0,
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
