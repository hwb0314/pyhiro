#!/usr/bin/python

import os
import math
import numpy as np
import trimesh
import plot.pandageom as ppg
from direct.showbase.ShowBase import ShowBase
from direct.showbase.Loader import Loader
from panda3d.core import *
import plot.pandactrl as pandactrl
import plot.pandageom as pandageom
from utils import robotmath
from utils import designpattern
from shapely.geometry import Polygon
from shapely.geometry import Point
import matplotlib.pyplot as plt
from panda3d.bullet import BulletConvexHullShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

class Rtq85():
    '''
    use utils.designpattern.singleton() to get a single instance of this class
    '''

    def __init__(self, jawwidth=85):
        '''
        load the robotiq85 model, set jawwidth and return a nodepath
        the rtq85 gripper is composed of a parallelism and a fixed triangle,
        the parallelism: 1.905-1.905; 5.715-5.715; 70/110 degree
        the triangle: 4.75 (finger) 5.715 (inner knuckle) 3.175 (outer knuckle)

        ## input
        pandabase:
            the showbase() object
        jawwidth:
            the distance between fingertips

        ## output
        rtq85np:
            the nodepath of this rtq85 hand

        author: weiwei
        date: 20160627
        '''
        self.rtq85np = NodePath("rtq85hnd")
        self.jawwidth = jawwidth

        this_dir, this_filename = os.path.split(__file__)
        rtq85basepath = os.path.join(this_dir, "rtq85egg", "robotiq_85_base_link.egg")
        rtq85fingerpath = os.path.join(this_dir, "rtq85egg", "robotiq_85_finger_link.egg")
        rtq85fingertippath = os.path.join(this_dir, "rtq85egg", "robotiq_85_finger_tip_link.egg")
        rtq85innerknucklepath = os.path.join(this_dir, "rtq85egg", "robotiq_85_inner_knuckle_link.egg")
        rtq85knucklepath = os.path.join(this_dir, "rtq85egg", "robotiq_85_knuckle_link.egg")

        rtq85base = NodePath("rtq85base")
        rtq85lknuckle = NodePath("rtq85lknuckle")
        rtq85rknuckle = NodePath("rtq85rknuckle")
        rtq85lfgr = NodePath("rtq85lfgr")
        rtq85rfgr = NodePath("rtq85rfgr")
        rtq85ilknuckle = NodePath("rtq85ilknuckle")
        rtq85irknuckle = NodePath("rtq85irknuckle")
        rtq85lfgrtip = NodePath("rtq85lfgrtip")
        rtq85rfgrtip = NodePath("rtq85rfgrtip")

        # loader is a global variable defined by panda3d
        rtq85_basel = loader.loadModel(rtq85basepath)
        rtq85_fingerl = loader.loadModel(rtq85fingerpath)
        rtq85_fingertipl = loader.loadModel(rtq85fingertippath)
        rtq85_innerknucklel = loader.loadModel(rtq85innerknucklepath)
        rtq85_knucklel = loader.loadModel(rtq85knucklepath)

        # base
        rtq85_basel.instanceTo(rtq85base)
        rtq85base.setPos(0,0,0)
        # rtq85base.setColor(1,1,1,1)
        rtq85base.setTransparency(TransparencyAttrib.MAlpha)

        # left and right outer knuckle
        rtq85_knucklel.instanceTo(rtq85lknuckle)
        rtq85lknuckle.setPos(-3.060114443, 5.490451627, 0)
        rtq85lknuckle.setHpr(0, 0, 180)
        # rtq85lknuckle.setColor(1,1,1,1)
        rtq85lknuckle.setTransparency(TransparencyAttrib.MAlpha)
        rtq85lknuckle.reparentTo(rtq85base)
        rtq85_knucklel.instanceTo(rtq85rknuckle)
        rtq85rknuckle.setPos(3.060114443, 5.490451627, 0)
        rtq85rknuckle.setHpr(0, 0, 0)
        # rtq85rknuckle.setColor(1,1,1,1)
        rtq85rknuckle.setTransparency(TransparencyAttrib.MAlpha)
        rtq85rknuckle.reparentTo(rtq85base)

        # left and right finger
        rtq85_fingerl.instanceTo(rtq85lfgr)
        rtq85lfgr.setPos(3.148504435, -0.408552455, 0)
        # rtq85lfgr.setColor(1,1,1,1)
        rtq85lfgr.setTransparency(TransparencyAttrib.MAlpha)
        rtq85lfgr.reparentTo(rtq85lknuckle)
        rtq85_fingerl.instanceTo(rtq85rfgr)
        rtq85rfgr.setPos(3.148504435, -0.408552455, 0)
        # rtq85rfgr.setColor(1,1,1,1)
        rtq85rfgr.setTransparency(TransparencyAttrib.MAlpha)
        rtq85rfgr.reparentTo(rtq85rknuckle)

        # left and right inner knuckle
        rtq85_innerknucklel.instanceTo(rtq85ilknuckle)
        rtq85ilknuckle.setPos(-1.27, 6.142, 0)
        rtq85ilknuckle.setHpr(0, 0, 180)
        # rtq85ilknuckle.setColor(1,1,1,1)
        rtq85ilknuckle.setTransparency(TransparencyAttrib.MAlpha)
        rtq85ilknuckle.reparentTo(rtq85base)
        rtq85_innerknucklel.instanceTo(rtq85irknuckle)
        rtq85irknuckle.setPos(1.27, 6.142, 0)
        rtq85irknuckle.setHpr(0, 0, 0)
        # rtq85irknuckle.setColor(1,1,1,1)
        rtq85irknuckle.setTransparency(TransparencyAttrib.MAlpha)
        rtq85irknuckle.reparentTo(rtq85base)

        # left and right fgr tip
        rtq85_fingertipl.instanceTo(rtq85lfgrtip)
        rtq85lfgrtip.setPos(3.759940821, 4.303959807, 0)
        # rtq85lfgrtip.setColor(1,1,1,1)
        rtq85lfgrtip.setTransparency(TransparencyAttrib.MAlpha)
        rtq85lfgrtip.reparentTo(rtq85ilknuckle)
        rtq85_fingertipl.instanceTo(rtq85rfgrtip)
        rtq85rfgrtip.setPos(3.759940821, 4.303959807, 0)
        rtq85rfgrtip.setHpr(0, 0, 0)
        # rtq85rfgrtip.setColor(1,1,1,1)
        rtq85rfgrtip.setTransparency(TransparencyAttrib.MAlpha)
        rtq85rfgrtip.reparentTo(rtq85irknuckle)

        rtq85base.reparentTo(self.rtq85np)
        self.setJawwidth(jawwidth)

    def setJawwidth(self, jawwidth):
        '''
        set the jawwidth of rtq85hnd
        the formulea is deduced on a note book
        the rtq85 gripper is composed of a parallelism and a fixed triangle,
        the parallelism: 1.905-1.905; 5.715-5.715; 70/110 degree
        the triangle: 4.75 (finger) 5.715 (inner knuckle) 3.175 (outer knuckle)

        ## input
        rtq85hnd:
            nodepath of a robotiq85hand
        jawwidth:
            the width of the jaw

        author: weiwei
        date: 20160627
        '''
        assert(jawwidth <= 85)
        assert(jawwidth >= 0)

        self.jawwidth = jawwidth

        rotiknuckle = 0
        if jawwidth/2 >= 5:
            rotiknuckle=41-math.asin((jawwidth/2-5)/57.15)*180/math.pi
        else:
            rotiknuckle=41+math.asin((5-jawwidth/2)/57.15)*180/math.pi
        print rotiknuckle

        # right finger
        rtq85irknuckle = self.rtq85np.find("**/rtq85irknuckle")
        rtq85irknucklehpr = rtq85irknuckle.getHpr()
        rtq85irknuckle.setHpr(rotiknuckle, rtq85irknucklehpr[1], rtq85irknucklehpr[2])
        rtq85rknuckle = self.rtq85np.find("**/rtq85rknuckle")
        rtq85rknucklehpr = rtq85rknuckle.getHpr()
        rtq85rknuckle.setHpr(rotiknuckle, rtq85rknucklehpr[1], rtq85rknucklehpr[2])
        rtq85rfgrtip = self.rtq85np.find("**/rtq85rfgrtip")
        rtq85rfgrtiphpr = rtq85rfgrtip.getHpr()
        rtq85rfgrtip.setHpr(-rotiknuckle, rtq85rfgrtiphpr[1], rtq85rfgrtiphpr[2])

        # left finger
        rtq85ilknuckle = self.rtq85np.find("**/rtq85ilknuckle")
        rtq85ilknucklehpr = rtq85ilknuckle.getHpr()
        rtq85ilknuckle.setHpr(-rotiknuckle, rtq85ilknucklehpr[1], rtq85ilknucklehpr[2])
        rtq85lknuckle = self.rtq85np.find("**/rtq85lknuckle")
        rtq85lknucklehpr = rtq85lknuckle.getHpr()
        rtq85lknuckle.setHpr(-rotiknuckle, rtq85lknucklehpr[1], rtq85lknucklehpr[2])
        rtq85lfgrtip = self.rtq85np.find("**/rtq85lfgrtip")
        rtq85lfgrtiphpr = rtq85rfgrtip.getHpr()
        rtq85lfgrtip.setHpr(-rotiknuckle, rtq85lfgrtiphpr[1], rtq85lfgrtiphpr[2])

    def plot(self, pandabase, nodepath=None, pos=None, ydirect=None, zdirect=None, rgba=None):
        '''
        plot the hand under the given nodepath

        ## input
        pandabase:
            a showbase instance
        nodepath:
            the parent node this hand is going to be attached to
        pos:
            the position of the hand
        ydirect:
            the y direction of the hand
        zdirect:
            the z direction of the hand
        rgba:
            the rgba color

        ## note:
            dot(ydirect, zdirect) must be 0

        date: 20160628
        author: weiwei
        '''

        if nodepath is None:
            nodepath = pandabase.render
        if pos is None:
            pos = Vec3(0,0,0)
        if ydirect is None:
            ydirect = Vec3(0,1,0)
        if zdirect is None:
            zdirect = Vec3(0,0,1)
        if rgba is None:
            rgba = Vec4(1,1,1,0.5)

        # assert(ydirect.dot(zdirect)==0)

        placeholder = nodepath.attachNewNode("rtq85holder")
        self.rtq85np.instanceTo(placeholder)
        xdirect = ydirect.cross(zdirect)
        transmat4 = Mat4()
        transmat4.setCol(0, xdirect)
        transmat4.setCol(1, ydirect)
        transmat4.setCol(2, zdirect)
        transmat4.setCol(3, pos)
        self.rtq85np.setMat(transmat4)
        placeholder.setColor(rgba)

if __name__=='__main__':

    def updateworld(world, task):
        world.doPhysics(globalClock.getDt())
        # result = base.world.contactTestPair(bcollidernp.node(), lftcollidernp.node())
        # result1 = base.world.contactTestPair(bcollidernp.node(), ilkcollidernp.node())
        # result2 = base.world.contactTestPair(lftcollidernp.node(), ilkcollidernp.node())
        # print result
        # print result.getContacts()
        # print result1
        # print result1.getContacts()
        # print result2
        # print result2.getContacts()
        # for contact in result.getContacts():
        #     cp = contact.getManifoldPoint()
        #     print cp.getLocalPointA()
        return task.cont

    base = ShowBase()
    rtq85hnd = designpattern.singleton(Rtq85)
    hndpos = Vec3(0,0,0)
    ydirect = Vec3(0,1,0)
    zdirect = Vec3(0,0,1)
    rtq85hnd.plot(base, pos=hndpos, ydirect=ydirect, zdirect=zdirect)
    pandactrl.setRenderEffect(base)
    pandactrl.setLight(base)
    pandactrl.setCam(base, 0, 500, 500, 'perspective')

    axis = loader.loadModel('zup-axis.egg')
    axis.reparentTo(base.render)
    axis.setPos(hndpos)
    axis.lookAt(hndpos+ydirect)

    bullcldrnp = base.render.attachNewNode("bulletcollider")
    base.world = BulletWorld()

    # hand base
    # rtq85hnd.rtq85np.find("**/rtq85base").showTightBounds()
    gbnp = rtq85hnd.rtq85np.find("**/rtq85base").find("**/+GeomNode")
    gb = gbnp.node().getGeom(0)
    gbts = gbnp.getTransform(base.render)
    gbmesh = BulletTriangleMesh()
    gbmesh.addGeom(gb)
    bbullnode = BulletRigidBodyNode('gb')
    bbullnode.addShape(BulletTriangleMeshShape(gbmesh, dynamic=True), gbts)
    bcollidernp=bullcldrnp.attachNewNode(bbullnode)
    base.world.attachRigidBody(bbullnode)
    bcollidernp.setCollideMask(BitMask32.allOn())

    # rtq85hnd.rtq85np.find("**/rtq85lfgrtip").showTightBounds()
    glftnp = rtq85hnd.rtq85np.find("**/rtq85lfgrtip").find("**/+GeomNode")
    glft = glftnp.node().getGeom(0)
    glftts = glftnp.getTransform(base.render)
    glftmesh = BulletTriangleMesh()
    glftmesh.addGeom(glft)
    # lftbullnode = BulletRigidBodyNode('glft')
    # lftbullnode.addShape(BulletTriangleMeshShape(glftmesh, dynamic=True), glftts)
    # lftcollidernp=bullcldrnp.attachNewNode(lftbullnode)
    # base.world.attachRigidBody(lftbullnode)
    # lftcollidernp.setCollideMask(BitMask32.allOn())
    # base.world.attachRigidBody(glftbullnode)

    # rtq85hnd.rtq85np.find("**/rtq85ilknuckle").showTightBounds()
    gilknp = rtq85hnd.rtq85np.find("**/rtq85ilknuckle").find("**/+GeomNode")
    gilk = gilknp.node().getGeom(0)
    gilkts = gilknp.getTransform(base.render)
    gilkmesh = BulletTriangleMesh()
    gilkmesh.addGeom(gilk)
    ilkbullnode = BulletRigidBodyNode('gilk')
    ilkbullnode.addShape(BulletTriangleMeshShape(gilkmesh, dynamic=True), gilkts)
    ilkbullnode.addShape(BulletTriangleMeshShape(glftmesh, dynamic=True), glftts)
    ilkcollidernp=bullcldrnp.attachNewNode(ilkbullnode)
    base.world.attachRigidBody(ilkbullnode)
    ilkcollidernp.setCollideMask(BitMask32.allOn())
    # rtq85hnd.rtq85np.find("**/rtq85ilknuckle").showTightBounds()
    # rtq85hnd.rtq85np.showTightBounds()

    base.taskMgr.add(updateworld, "updateworld", extraArgs=[base.world], appendTask=True)
    result = base.world.contactTestPair(bbullnode, ilkbullnode)
    print result
    print result.getContacts()
    import plot.pandageom as pandageom
    for contact in result.getContacts():
        cp = contact.getManifoldPoint()
        print cp.getLocalPointA()
        pandageom.plotSphere(base, pos=cp.getLocalPointA(), radius=1, rgba=Vec4(1,0,0,1))

    debugNode = BulletDebugNode('Debug')
    debugNode.showWireframe(True)
    debugNode.showConstraints(True)
    debugNode.showBoundingBoxes(False)
    debugNode.showNormals(False)
    debugNP = bullcldrnp.attachNewNode(debugNode)
    debugNP.show()

    base.world.setDebugNode(debugNP.node())

    base.run()