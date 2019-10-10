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

class cycloidClass:
    """ Create Object command"""
    def __init__(self,ToothPitch = 0.08, RollerDiameter = 0.15,RollerHeight=4, Eccentricity =
                 0.05, ToothCount = 10, LineSegmentCount = 400,
                 CenterDiameter = -1.00, PressureAngleLimit = 50.0,
                 PressureAngleOffset = 0.01, baseHeight = 2.0,DriverPinDiameter = 0.25,CycloidalDiskHeight = 1.74):
        self.ToothPitch = ToothPitch
        self.RollerDiameter = RollerDiameter
        self.RollerHeight = RollerHeight
        self.Eccentricity = Eccentricity
        self.ToothCount = ToothCount
        self.LineSegmentCount = LineSegmentCount
        self.CenterDiameter = CenterDiameter
        self.PressureAngleLimit = PressureAngleLimit
        self.PressureAngleOffset = PressureAngleOffset
        self.DriverPinDiameter = DriverPinDiameter
        self.baseHeight = baseHeight
        self.CycloidalDiskHeight = CycloidalDiskHeight
        if CenterDiameter > 0:
            self.ToothPitch = CenterDiameter / ToothCount
        self.minmaxRadius();



    def calcyp(self,a):
        return math.atan(math.sin(self.ToothCount * a) /
                         (math.cos(self.ToothCount * a) +
                          (self.ToothCount * self.ToothPitch) /
                          (self.Eccentricity * (self.ToothCount + 1))))

    def calcX(self,a):
        return (self.ToothCount * self.ToothPitch) * math.cos(a) + \
            self.Eccentricity * math.cos((self.ToothCount + 1) * a) -    \
            float(self.RollerDiameter) / 2.0 * math.cos(self.calcyp(a) + a)

    def calcY(self,a):
        return (self.ToothCount * self.ToothPitch) * math.sin(a) +   \
            self.Eccentricity * math.sin((self.ToothCount + 1) * a) -    \
                float(self.RollerDiameter) / 2.0 * math.sin(self.calcyp(a) + a)

    def clean1(self,a):
        """ return -1 < a < 1 """
        return min(1, max(a, -1))

    def calcPressureAngle(self, angle):
        """ calculate the angle of the cycloidalDisk teeth at the angle """
        ex = 2.0 ** 0.5
        r3 = self.ToothPitch * self.ToothCount 
#        p * n
        rg = r3 / ex
        pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - float(self.RollerDiameter) / 2.0
        return math.asin(self.clean1(((r3 * math.cos(angle) - rg) / (pp + float(self.RollerDiameter) / 2.0)))) * 180 / math.pi

    def calcPressureLimit(self,a):
        ex = 2.0 ** 0.5
        r3 = self.ToothPitch * self.ToothCount
        rg = r3 / ex
        q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
        x = rg - self.Eccentricity + (q - float(self.RollerDiameter) / 2.0) * (r3 * math.cos(a) - rg) / q
        y = (q - float(self.RollerDiameter) / 2.0) * r3 * math.sin(a) / q
        return (x ** 2.0 + y ** 2.0) ** 0.5

    def checkLimit(self,v,maxrad,minrad):
        """ if x,y outside limit return x,y as at limit, else return x,y """
        r, a = toPolar(v.x, v.y)
        if (r > maxrad) or (r < minrad):
            r = r - self.PressureAngleOffset
            v.x, v.y = toRect(r, a)
        return v



    def minmaxRadius(self):
        """ Find the pressure angle limit circles """
        minAngle = -1.0
        maxAngle = -1.0
        for i in range(0, 180):
            x = self.calcPressureAngle(float(i)*math.pi / 180)
            if (x < self.PressureAngleLimit) and (minAngle < 0):
                minAngle = float(i)
            if (x < -self.PressureAngleLimit) and (maxAngle < 0):
                maxAngle = float(i - 1)
        self.minRadius = self.calcPressureLimit(minAngle * math.pi / 180)
        self.maxRadius = self.calcPressureLimit(maxAngle * math.pi / 180)

    def generatePinBase(self):
        """ create the base that the fixedRingPins will be attached to """        
        self.minmaxRadius()
        pinBase = Part.makeCylinder(self.maxRadius+float(self.RollerDiameter),self.baseHeight);
        # generate the pin locations
        for i in range(0, self.ToothCount + 1):
            x = self.ToothPitch * self.ToothCount * math.cos(2.0 * math.pi /
                                                           (self.ToothCount + 1) * i)
            y = self.ToothPitch * self.ToothCount * math.sin(2.0 * math.pi /
                                                           (self.ToothCount + 1) * i)
            fixedRingPin = Part.makeCylinder(float(self.RollerDiameter)/2.0,self.RollerHeight,Base.Vector(x,y,0))
            pinBase = pinBase.fuse(fixedRingPin)
        accesshole = Part.makeCylinder(self.DriverPinDiameter/2.0,10000);
        pinBase.cut(accesshole);
        return pinBase

    def generateEccentricShaft(self):
    # add a circle in the center of the cam
        eccentricShaft = Part.makeCylinder(float(self.RollerDiameter) / 2.0,self.RollerHeight,Base.Vector(-self.Eccentricity,0,0))
        return eccentricShaft

    """
    def points(self, num=10):
        pts = self.involute_points(num=num)
        rot = rotation3D(-math.pi / self.z / 2.0)
        pts = rot(pts)
        ref = reflection3D(math.pi / 2.0)
        pts1 = ref(pts)[::-1]
        rot = rotation3D(2.0 * math.pi / self.z)
        if self.add_foot:
            return (array([
                array([pts[0], pts[1]]),
                pts[1:],
                array([pts[-1], pts1[0]]),
                pts1[:-1],
                array([pts1[-2.0], pts1[-1]])
            ]))
        else:
            return (array([pts, array([pts[-1], pts1[0]]), pts1]))
    """        

    def generateCycloidalDiskArray(self):
        """ make the array to be used in the bspline 
            that is the cycloidalDisk
        """
        self.minmaxRadius()
        q = 2.0 * math.pi / float(self.LineSegmentCount)
        i = 0

        v1 = Base.Vector(self.calcX(q*i),self.calcY(q*i),0)
        v1 = self.checkLimit(v1,self.maxRadius,self.minRadius)

        cycloidalDiskArray = []
        cycloidalDiskArray.append(v1)
        for i in range(0, self.LineSegmentCount):
            v2 = Base.Vector(self.calcX(q*(i+1)),self.calcY(q*(i+1)),0)
            v2 = self.checkLimit(v2,self.maxRadius,self.minRadius)
            cycloidalDiskArray.append(v2)
        return cycloidalDiskArray
    
    def generateCycloidalDisk(self):
        """
        make the complete cycloidal disk
        """
        a = Part.BSplineCurve(self.generateCycloidalDiskArray()).toShape()
        w = Part.Wire([a])
        f = Part.Face(w)
        e = f.extrude(FreeCAD.Vector(0,0,self.CycloidalDiskHeight))
        e.translate(Base.Vector(-self.Eccentricity, 0, self.baseHeight+0.1))
        return e
        
    def _update(self):
        self.__init__(ToothPitch = self.ToothPitch,
                      RollerDiameter=self.RollerDiameter,
                      RollerHeight = self.RollerHeight,
                      Eccentricity=self.Eccentricity,
                      ToothCount=self.ToothCount,
                      LineSegmentCount=self.LineSegmentCount,
                      CenterDiameter=self.CenterDiameter,
                      PressureAngleLimit=self.PressureAngleLimit,
                      PressureAngleOffset=self.PressureAngleOffset,
                      DriverPinDiameter=self.DriverPinDiameter,
                      CycloidalDiskHeight=self.CycloidalDiskHeight)

