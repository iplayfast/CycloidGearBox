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
           math.cos((ToothCount + 1) * a) - float(RollerDiameter) / 2.0 * \
           math.cos(calcyp(ToothCount, Eccentricity, ToothPitch, a) + a)


def calcY(ToothCount: int, Eccentricity, ToothPitch, RollerDiameter: float, a):
    return (ToothCount * ToothPitch) * math.sin(a) + Eccentricity * \
           math.sin((ToothCount + 1) * a) - float(RollerDiameter) / 2.0 * \
           math.sin(calcyp(ToothCount, Eccentricity, ToothPitch, a) + a)

def CalculateRs(pinCount,step : int,Eccentricity, bigdiam,pindiam:float):
    D = bigdiam
    d = pindiam
    R = D / 2.0
    r = d / 2.0
    N = pinCount
    u = step
    # No less than 3, no more than 50 pins
    if N<3:
        N = 3
    if N>50:
        N = 50
    e = Eccentricity
    # e cannot be larger than r (d/2)
    if( e > r ):
        e = r

    # Validate r based on R and N: canot be larger than R * sin(pi/N) or the circles won't fit
    if( r > R * Math.sin( Math.PI / N ) ):
        r = R * Math.sin(Math.PI / N)
        d = r * 2.0
    inset = r
    angle = 360 / N


    # To draw a epitrachoid, we need r1 (big circle), r2 (small rolling circle) and d (displament of point)
    # r1 + r2 = R = D/2
    # r1/r2 = (N-1)
    # From the above equations: r1 = (N - 1) * R/N, r2 = R/N
    r1 = (N - 1)* D / 2 / N;
    r2 = D / 2 / N
    return r1,r2

def calculate(u : int,e,r1,r2: float):
    X = (r1 + r2) * math.cos(2 * math.pi * u) + e * math.cos((r1 + r2) * 2 * math.pi * u / r2)
    Y = (r1 + r2) * math.sin(2 * math.pi * u) + e * math.sin((r1 + r2) * 2 * math.pi * u / r2)
    return X,Y





def clean1(a):
    """ return -1 < a < 1 """
    return min(1, max(a, -1))


def calcPressureAngle(ToothCount, ToothPitch, RollerDiameter, angle):
    """ calculate the angle of the cycloidalDisk teeth at the angle """
    ex = 2.0 ** 0.5
    r3 = ToothPitch * ToothCount
    #        p * n
    rg = r3 / ex
    pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - float(RollerDiameter) / 2.0
    return math.asin(clean1(((r3 * math.cos(angle) - rg) / (pp + float(RollerDiameter) / 2.0)))) * 180 / math.pi


def calcPressureLimit(ToothCount, ToothPitch, Eccentricity, RollerDiameter, a):
    ex = 2.0 ** 0.5
    r3 = ToothPitch * ToothCount
    rg = r3 / ex
    q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
    x = rg - Eccentricity + (q - float(RollerDiameter) / 2.0) * (r3 * math.cos(a) - rg) / q
    y = (q - float(RollerDiameter) / 2.0) * r3 * math.sin(a) / q
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
        x = calcPressureAngle(ToothCount, ToothPitch, RollerDiameter, float(i) * math.pi / 180)
        if (x < PressureAngleLimit) and (minAngle < 0):
            minAngle = float(i)
        if (x < -PressureAngleLimit) and (maxAngle < 0):
            maxAngle = float(i - 1)
    minRadius = calcPressureLimit(ToothCount, ToothPitch, Eccentricity, RollerDiameter, minAngle * math.pi / 180)
    maxRadius = calcPressureLimit(ToothCount, ToothPitch, Eccentricity, RollerDiameter, maxAngle * math.pi / 180)
    return minRadius, maxRadius


def generatePinBase(H):
    """ create the base that the fixedRingPins will be attached to """
    ToothCount = H["ToothCount"]
    ToothPitch = H["ToothPitch"]
    RollerDiameter = H["RollerDiameter"]
    RollerHeight = H["RollerHeight"]
    BaseHeight = H["BaseHeight"]
    DriverDiskHeight = H["DriverDiskHeight"]
    ShaftDiameter = H["ShaftDiameter"]
    clearance = H["clearance"]
    minRadius, maxRadius = minmaxRadius(H)
    pinBase = Part.makeCylinder(minRadius + float(RollerDiameter)*2, BaseHeight) # base of the whole system
    dd = Part.makeCylinder(float(minRadius) * 0.75 + float(clearance), DriverDiskHeight*2, Base.Vector(0, 0,BaseHeight-DriverDiskHeight-1)) #hole for the driver disk to fit in
    pinBase = pinBase.cut(dd)
    # generate the pin locations
    pinRadius = (minRadius+maxRadius)/2.0 + float(RollerDiameter)/2
    for i in range(0, ToothCount):
        x = pinRadius * math.cos(2.0 * math.pi * i/ToothCount)
        y = pinRadius * math.sin(2.0 * math.pi * i/ToothCount)

        negfixedRingPin = Part.makeCylinder(float(RollerDiameter)/2.0 +0.5 , RollerHeight, Base.Vector(x, y, 0))
        fixedRingPin = Part.makeCylinder(float(RollerDiameter) , RollerHeight, Base.Vector(x, y, BaseHeight))
        fixedRingPinpin = Part.makeCylinder(float(RollerDiameter)/2.0 -float(clearance), BaseHeight / 2.0 +RollerHeight, Base.Vector(x, y, BaseHeight))
        pinBase = pinBase.cut(negfixedRingPin) #make a hole if multple gearboxes are in line
        pinBase = pinBase.fuse(fixedRingPinpin) # make the pins the cycloid gear uses, and the Part that goes into the above hole
        pinBase = pinBase.fuse(fixedRingPin) # make the pins the cycloid gear uses
    # need hole for eccentric shaft, add a bit so not too tight
    # todo  allow user values for sizes
    # todo allow bearing option
    shaft = Part.makeCylinder(float(ShaftDiameter)/ 2.0+float(clearance),BaseHeight*2,Base.Vector(0,0,-BaseHeight))
    return pinBase.cut(shaft)

def generateOutputShaft(H):
    minRadius,maxRadius = minmaxRadius(H)
    DiskHoleCount = H["DiskHoleCount"]
    ShaftDiameter = H["ShaftDiameter"]
    DriverDiskHeight = H["DriverDiskHeight"]
    Eccentricity = H["Eccentricity"]
    RollerDiameter = H["RollerDiameter"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    BaseHeight = H["BaseHeight"]
    dd = Part.makeCylinder(float(minRadius) * 0.75, DriverDiskHeight, Base.Vector(0, 0, 0))  # the main driver disk
    os = Part.makeCylinder(float(ShaftDiameter)/2.0,BaseHeight*2,Base.Vector(0,0,0))
    dd = dd.fuse(os)
    for i in range(0, DiskHoleCount):
        x = minRadius / 2 * math.cos(2.0 * math.pi / (DiskHoleCount) * i)
        y = minRadius / 2 * math.sin(2.0 * math.pi / (DiskHoleCount) * i)
        fixedringpin = Part.makeCylinder(float(RollerDiameter * 2 - Eccentricity), CycloidalDiskHeight * 3,
                                         Base.Vector(x, y, -1))  # driver pins
        dd = dd.cut(fixedringpin)
    fp = dd.translate(Base.Vector(0, 0, BaseHeight +DriverDiskHeight))
    return fp

def generateEccentricShaft(H):
    minRadius,maxRadius = minmaxRadius(H)
    RollerDiameter = H["RollerDiameter"]
    RollerHeight = H["RollerHeight"]
    Eccentricity = H["Eccentricity"]
    BaseHeight = H["BaseHeight"]
    ShaftDiameter = H["ShaftDiameter"]
    DriverDiskHeight = H["DriverDiskHeight"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    DiskHoleCount = H["DiskHoleCount"]
    # add a circle in the center of the cam
    #print("shaft",RollerDiameter,Eccentricity)
    e1 = Part.makeCylinder(float(ShaftDiameter) / 2.0, CycloidalDiskHeight, Base.Vector(-Eccentricity , 0,BaseHeight))
    e2 = Part.makeCylinder(float(ShaftDiameter) / 2.0, CycloidalDiskHeight, Base.Vector(Eccentricity , 0, BaseHeight + CycloidalDiskHeight))
    e = e1.fuse(e2)
    d = Part.makeCylinder(float(ShaftDiameter)/ 2.0,BaseHeight*2,Base.Vector(0,0,-BaseHeight)) # one base out sticking out the bottom, one base height through the base
    d = d.fuse(e)
    drivehole = Part.makeCylinder(4.8/2.0,BaseHeight*1.75,Base.Vector(0,0,-BaseHeight))
    d = d.cut(drivehole)
    minRadius, maxRadius = minmaxRadius(H)
    #cyl = Part.makeCylinder(float(minRadius)*0.75,RollerHeight)
    #cyl = cyl.fuse(generatePinBase(H).translate(Base.Vector(0,0,-BaseHeight)))
    #d = d.fuse(cyl)
    return d

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
    q = 2.0 * math.pi / float(LineSegmentCount)
    i = 0

    v1 = Base.Vector(calcX(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * i),
                     calcY(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * i), 0)
    v1 = checkLimit(v1, PressureAngleOffset, minRadius, maxRadius)

    cycloidalDiskArray = []
    cycloidalDiskArray.append(v1)
    for i in range(0, LineSegmentCount):
        v2 = Base.Vector(
            calcX(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * (i + 1)),
            calcY(ToothCount, Eccentricity, ToothPitch, RollerDiameter, q * (i + 1)),
            0)
        v2 = checkLimit(v2, PressureAngleOffset, minRadius, maxRadius)
        cycloidalDiskArray.append(v2)
    return cycloidalDiskArray


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
    a = Part.BSplineCurve(generateCycloidalDiskArray(H)).toShape()
    w = Part.Wire([a])
    f = Part.Face(w)
    # need to cut out the eccentric shaft hole, add a bit so it isn't too tight,
    # todo add option for bearing here
    es = Part.makeCircle(float(ShaftDiameter) /2.0+ float(clearance),Base.Vector(0,0,0))
    esw = Part.Wire([es])
    esf = Part.Face(esw)
    fc = f.cut(esf)
    for i in range(0, DiskHoleCount ):
        x = minRadius/2 * math.cos(2.0 * math.pi * (i / DiskHoleCount))
        y = minRadius/2 * math.sin(2.0 * math.pi * (i / DiskHoleCount))
        drivinghole= Part.makeCircle(RollerDiameter*2+float(clearance),Base.Vector(x,y,0))
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
    RollerHeight = H["RollerHeight"]
    Eccentricity = H["Eccentricity"]
    ShaftDiameter = H["ShaftDiameter"]
    BaseHeight = H["BaseHeight"]
    CycloidalDiskHeight =  H["CycloidalDiskHeight"]
    clearance = H["clearance"]
    dd = Part.makeCylinder(float(minRadius) * 0.75, DriverDiskHeight, Base.Vector(0, 0,0)) # the main driver disk
    shaft = Part.makeCylinder(float(ShaftDiameter)/ 2.0+float(clearance),DriverDiskHeight+BaseHeight*2,Base.Vector(0,0,-BaseHeight))
    for i in range(0, DiskHoleCount):
        x = minRadius / 2 * math.cos(2.0 * math.pi / (DiskHoleCount) * i)
        y = minRadius / 2 * math.sin(2.0 * math.pi / (DiskHoleCount) * i)
        fixedringpin = Part.makeCylinder(float(RollerDiameter*2 - Eccentricity) , CycloidalDiskHeight*3, Base.Vector(x, y, CycloidalDiskHeight)) #driver pins
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
        "RollerHeight": 5.0,
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

def testgeneratePinBase():
    Part.show(generatePinBase(generateDefaultHyperParam()))

def testgenerateDriverDisk():
    Part.show(generateDriverDisk(generateDefaultHyperParam()))

def testgenerateCycloidalDisk():
    Part.show(generateCycloidalDisk(generateDefaultHyperParam()))

def testgenerateOutputShaft():
    Part.show(generateOutputShaft(generateDefaultHyperParam()))
