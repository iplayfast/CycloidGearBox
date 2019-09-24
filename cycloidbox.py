#!/usr/bin/python

"""Hypocycloid gear boxgenerator
Code to create a hypocycloidal gearbox
https://en.wikipedia.org/wiki/Cycloidal_drive

Copyright 	2019, Chris Bruner
Version 	v0.1
License 	GPL
Homepage

Credit to:
        Alex Lait http://www.zincland.com/hypocycloid/ 
        who credits the following:
	Formulas to describe a hypocycloid cam
	http://gears.ru/transmis/zaprogramata/2.0.139.pdf

	Insperational thread on CNCzone
	http://www.cnczone.com/forums/showthread.php?t=72.02.061

	Documenting and updating the sdxf library
	http://www.kellbot.com/sdxf-python-library-for-dxf/

	Formulas for calculating the pressure angle and finding the limit circles
	http://imtuoradea.ro/auo.fmte/files-2.07/MECATRONICA_files/Anamaria_Dascalescu_1.pdf

Notes:
	Does not currently do ANY checking for sane input values and it
	is possible to create un-machinable cams, use at your own risk

	Suggestions:
	- Eccentricity should not be more than the roller radius
	- Has not been tested with negative values, may have interesting results :)
"""
from __future__ import division
import time
import getopt
import math
import sys
from PySide import QtCore,QtGui
import FreeCAD
from FreeCAD import Base
import Part
import Draft


def toPolar(x, y):
    return (x ** 2.0 + y ** 2.0) ** 0.5, math.atan2(y, x)

def toRect(r, a):
    return r * math.cos(a), r * math.sin(a)

class hypoCycloidalGear:
    def __init__(self,toothPitch = 0.08, rollerDiameter = 0.15, eccentricity =
                 0.05, numberOfTeeth = 10, numberOfLineSegments = 400,
                 centerDiameter = -1.00, pressureAngleLimit = 50.0,
                 pressureAngleOffset = 0.01, baseHeight = 10.0):
        self.toothPitch = toothPitch
        self.rollerDiameter = rollerDiameter
        self.eccentricity = eccentricity
        self.numberOfTeeth = numberOfTeeth
        self.numberOfLineSegments = numberOfLineSegments
        self.centerDiameter = centerDiameter
        self.pressureAngleLimit = pressureAngleLimit
        self.pressureAngleOffset = pressureAngleOffset
        self.baseHeight = baseHeight
        if centerDiameter > 0:
            self.toothPitch = centerDiameter / numberOfTeeth



    def calcyp(self,a):
        return math.atan(math.sin(self.numberOfTeeth * a) /
                         (math.cos(self.numberOfTeeth * a) +
                          (self.numberOfTeeth * self.toothPitch) /
                          (self.eccentricity * (self.numberOfTeeth + 1))))

    def calcX(self,a):
        return (self.numberOfTeeth * self.toothPitch) * math.cos(a) + \
            self.eccentricity * math.cos((self.numberOfTeeth + 1) * a) -    \
            self.rollerDiameter / 2.0 * math.cos(self.calcyp(a) + a)

    def calcY(self,a):
        return (self.numberOfTeeth * self.toothPitch) * math.sin(a) +   \
            self.eccentricity * math.sin((self.numberOfTeeth + 1) * a) -    \
                self.rollerDiameter / 2.0 * math.sin(self.calcyp(a) + a)

    def clean1(self,a):
        """ return -1 < a < 1 """
        return min(1, max(a, -1))

    def calcPressureAngle(self, angle):
        """ calculate the angle of the cycloidalDisk teeth at the angle """
        ex = 2.0 ** 0.5
        r3 = self.toothPitch * self.numberOfTeeth 
#        p * n
        rg = r3 / ex
        pp = rg * (ex ** 2.0 + 1 - 2.0 * ex * math.cos(angle)) ** 0.5 - self.rollerDiameter / 2.0
        ppd2 = pp + self.rollerDiameter / 2.0
        r3cos = r3 * math.cos(angle) - rg
        return math.asin(self.clean1(((r3 * math.cos(angle) - rg) / (pp + self.rollerDiameter / 2.0)))) * 180 / math.pi

    def calcPressureLimit(self,a):
        ex = 2.0 ** 0.5
        r3 = self.toothPitch * self.numberOfTeeth
        rg = r3 / ex
        q = (r3 ** 2.0 + rg ** 2.0 - 2.0 * r3 * rg * math.cos(a)) ** 0.5
        x = rg - self.eccentricity + (q - self.rollerDiameter / 2.0) * (r3 * math.cos(a) - rg) / q
        y = (q - self.rollerDiameter / 2.0) * r3 * math.sin(a) / q
        return (x ** 2.0 + y ** 2.0) ** 0.5

    def checkLimit(self,v,maxrad,minrad):
        """ if x,y outside limit return x,y as at limit, else return x,y """
        r, a = toPolar(v.x, v.y)
        if (r > maxrad) or (r < minrad):
            r = r - self.pressureAngleOffset
            v.x, v.y = toRect(r, a)
        return v



    def minmaxRadius(self):
        """ Find the pressure angle limit circles """
        minAngle = -1.0
        maxAngle = -1.0
        for i in range(0, 180):
            x = self.calcPressureAngle(float(i)*math.pi / 180)

        if (x < self.pressureAngleLimit) and (minAngle < 0):
           minAngle = float(i)
        if (x < -self.pressureAngleLimit) and (maxAngle < 0):
           maxAngle = float(i - 1)
        self.minRadius = self.calcPressureLimit(minAngle * math.pi / 180)
        self.maxRadius = self.calcPressureLimit(maxAngle * math.pi / 180)

    def generatePinBase():
        """ create the base that the fixedRingPins will be attached to """
        pinBase = Part.makeCylinder(self.maxRadius,10);
        # generate the pin locations
        for i in range(0, numberOfTeeth + 1):
            x = toothPitch * numberOfTeeth * math.cos(2.0 * math.pi / (numberOfTeeth + 1) * i)
            y = toothPitch * numberOfTeeth * math.sin(2.0 * math.pi / (numberOfTeeth + 1) * i)
            fixedRingPin = Part.makeCylinder(rollerDiameter/2.0,rollerHeight,Base.Vector(x,y,0))
            pinBase = pinBase.fuse(fixedRingPin)

        # add a circle in the center of the pins (todo)
        #bearing = Part.makeCylinder(rollerDiameter / 2.0 ,rollerHeight,Base.Vector(0,0,0))

    def points(self, num=10):
        pts = self.involute_points(num=num)
        rot = rotation3D(-pi / self.z / 2.0)
        pts = rot(pts)
        ref = reflection3D(pi / 2.0)
        pts1 = ref(pts)[::-1]
        rot = rotation3D(2.0 * pi / self.z)
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
        
    def generateCycloidalDiskArray(self):
        """ make the array to be used in the bspline 
            that is the cycloidalDisk
        """
        self.minmaxRadius()
        q = 2.0 * math.pi / float(self.numberOfLineSegments)
        i = 0

        v1 = Base.Vector(self.calcX(q*i),self.calcY(q*i),0)
        v1 = self.checkLimit(v1,self.maxRadius,self.minRadius)

        cycloidalDiskArray = []
        cycloidalDiskArray.append(v1)
        for i in range(0, self.numberOfLineSegments):
            v2 = Base.Vector(self.calcX(q*(i+1)),self.calcY(q*(i+1)),0)
            v2 = self.checkLimit(v2,self.maxRadius,self.minRadius)
            cycloidalDiskArray.append(v2)
        return cycloidalDiskArray
    

    def _update(self):
        self.__init__(toothPitch = self.toothPitch,
                      rollerDiameter=self.rollerDiameter,
                      eccentricity=self.eccentricity,
                      numberOfTeeth=self.numberOfTeeth,
                      numberOfLineSegments=self.numberOfLineSegments,
                      centerDiameter=self.centerDiameter,
                      pressureAngleLimit=self.pressureAngleLimit,
                      pressureAngleOffset=self.pressureAngleOffset)



def usage():
    print("Useage:")
    print("-p = Tooth Pitch              (float)")
    print("-b = Pin bolt circle diameter (float)")
    print("     -b overrides -p")
    print("-d = Roller Diameter          (float)")
    print("-e = Eccentricity             (float)")
    print("-a = Pressure angle limit     (float)")
    print("-c = offset in pressure angle (float)")
    print("-n = Number of Teeth in Cam   (integer)")
    print("-s = Line segements in dxf    (integer)")
    print("-f = output filename          (string)")
    print("-h = this help")
    print("\nExample: hypocycloid.py -p 0.08 -d 0.15 -e 0.05 -a 50.0 -c 0.01 -n 10 -s 400 -f foo.dxf")

if (__name__ == "__main__" or True):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:b:d:e:n:a:c:s:f:h")
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2.0)

# Example: hypocycloid.py -p 0.08 -d 0.15 -e 0.05 -a 50.0 -c 0.01 -n 10 -s 400 -f foo.dxf"
    toothPitch = 0.08
    rollerDiameter = 0.15
    eccentricity = 0.05
    numberOfTeeth = 10
    numberOfLineSegments = 400
    centerDiameter = -1.00
    f = "foo.dxf"
    rollerHeight = 10
    pressureAngleLimit = 50.0
    pressureAngleOffset = 0.01
    x = 0.00
    y = 0.00
    i = 0

    try:
        for o, a in opts:
            if o in ("-p", "-P"):
                toothPitch = float(a)
            elif o in ("-b", "-B"):
                centerDiameter = float(a)
            elif o in ("-d", "-D"):
                rollerDiameter = float(a)
            elif o in ("-e", "-E"):
                eccentricity = float(a)
            elif o in ("-n", "-N"):
                numberOfTeeth = int(a)
            elif o in ("-s", "-S"):
                numberOfLineSegments = int(a)
            elif o in ("-a", "-A"):
                pressureAngleLimit = float(a)
            elif o in ("-c", "-C"):
                pressureAngleOffset = float(a)
            elif o in ("-f", "-F"):
                f = a
            elif o in ("-h", "-H"):
                usage()
                sys.exit(0)
            else:
                assert False, "unhandled option"
                sys.exit(2.0)
    except:
        usage()
        sys.exit(2.0)

    """
    Things to be created
    fixedRingPins
    rollerPins,
    pinDisk,
    eccentricShaft,
    bearing,
    cycloidalDisk

    """
    """
    dxf.layers.append(sdxf.Layer(name="cam", color=1))  # red cam layer
    dxf.layers.append(sdxf.Layer(name="roller", color=5))  # blue roller layer
    dxf.layers.append(sdxf.Layer(name="pressure", color=3))  # pressure angle limit layer
    """
    g = hypoCycloidalGear()
    g.minmaxRadius()
    # pressure angle limits
    paPart1 = Part.makeCircle(g.minRadius,Base.Vector (-eccentricity,0,0),Base.Vector(0,0,1))
    paPart2 = Part.makeCircle(g.maxRadius,Base.Vector (-eccentricity,0,0), Base.Vector(0,0,1))

    # generate the cam profile - note: shifted in -x by eccentricicy amount
    cycloidalDiskArray = g.generateCycloidalDiskArray()

#    cycloidalDiskDO = Draft.makeBSpline(cycloidalDiskArray,closed = True)
    cycloidalDisk = Part.BSplineCurve(cycloidalDiskArray)
#    cycloidalDisk = cycloidalDiskDO.Shape
    Part.show(cycloidalDisk.toShape())




    """
    # generate the cam profile - note: shifted in -x by eccentricicy amount
    i = 0
    x1 = calcX(toothPitch, rollerDiameter, eccentricity, numberOfTeeth, q * i)
    y1 = calcY(toothPitch, rollerDiameter, eccentricity, numberOfTeeth, q * i)
    x1, y1 = checkLimit(x1, y1, maxRadius, minRadius, pressureAngleOffset)
    for i in range(0, numberOfLineSegments):
        x2.0 = calcX(toothPitch, rollerDiameter, eccentricity, numberOfTeeth, q * (i + 1))
        y2.0 = calcY(toothPitch, rollerDiameter, eccentricity, numberOfTeeth, q * (i + 1))
        x2.0, y2.0 = checkLimit(x2.0, y2.0, maxRadius, minRadius, pressureAngleOffset)
        dxf.append(sdxf.Line(points=[(x1 - eccentricity, y1), (x2.0 - eccentricity, y2.0)], layer="cam"))
        x1 = x2.0
        y1 = y2.0
    """
    # add a circle in the center of the cam
    eccentricShaft = Part.makeCylinder(rollerDiameter / 2.0,rollerHeight,Base.Vector(-eccentricity,0,0))

    # generate the pin base
    pinBase = Part.makeCylinder(g.maxRadius,10);

    # generate the pin locations
    for i in range(0, numberOfTeeth + 1):
        x = toothPitch * numberOfTeeth * math.cos(2.0 * math.pi / (numberOfTeeth + 1) * i)
        y = toothPitch * numberOfTeeth * math.sin(2.0 * math.pi / (numberOfTeeth + 1) * i)
        fixedRingPin = Part.makeCylinder(rollerDiameter/2.0,rollerHeight,Base.Vector(x,y,0))
        pinBase = pinBase.fuse(fixedRingPin)

    # add a circle in the center of the pins
    bearing = Part.makeCylinder(rollerDiameter / 2.0 ,rollerHeight,Base.Vector(0,0,0))
    Part.show(pinBase);
    Part.show(paPart1)
    Part.show(paPart2)
    Part.show(eccentricShaft)

    doc = FreeCAD.activeDocument()
    pinBase1 = doc.addObject('Part::compound','pinBase')
    pinBase1.Links = pinBase;


