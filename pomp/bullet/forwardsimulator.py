import pybullet as p
import pybullet_data
import time
import math
from ..structures.toolfunc import *
import numpy as np

class forwardSimulationEL():
    def __init__(self, gui=False):
        self.visualShapeId = -1
        self.gui = gui
        if self.gui:
            p.connect(p.GUI) # p.GUI
        else:
            p.connect(p.DIRECT) # p.GUI
        self.g = -9.81
        # p.setAdditionalSearchPath(pybullet_data.getDataPath())
        # p.setGravity(0, 0, self.g)

        # self.set_params(params)
        # self.create_shapes()
    
    def set_params(self, params):
        # Kinodynamics
        self.mass_object = params[0]
        self.pos_object = [1000,0,0]
        self.quat_object = p.getQuaternionFromEuler([math.pi/2,0,0])
        self.vel_object = [.1,0,0]
        
        self.mass_gripper = params[1]
        self.moment_gripper = params[2] # moment of inertia
        self.pos_gripper = [1000,0,2]
        self.quat_gripper = p.getQuaternionFromEuler([0,0,0])
        self.vel_gripper = [0,0,0]
        self.vel_ang_gripper = [0,0,0]

        # Geometrics
        ydepth = 0.1
        self.half_extents_gripper = [params[3][0], ydepth/2, params[3][1]] # movement on x-z plane
        self.radius_object = params[4]
        self.height_object = ydepth

    def create_shapes(self):
        # Create an object
        objectId = p.createCollisionShape(p.GEOM_CYLINDER, radius=self.radius_object, height=self.height_object)
        self.objectUid = p.createMultiBody(self.mass_object, 
                                           objectId, 
                                           self.visualShapeId, 
                                           self.pos_object,
                                           self.quat_object)
        p.changeDynamics(self.objectUid, -1, lateralFriction=0, spinningFriction=0, 
                         rollingFriction=0, linearDamping=0, angularDamping=0)
        
        # Create a bar-gripper
        gripperId = p.createCollisionShape(p.GEOM_BOX, halfExtents=self.half_extents_gripper)
        self.gripperUid = p.createMultiBody(self.mass_gripper, 
                                       gripperId, 
                                       self.visualShapeId, 
                                       self.pos_gripper,
                                       self.quat_gripper)
        p.changeDynamics(self.gripperUid, -1, lateralFriction=0, spinningFriction=0, 
                         rollingFriction=0, linearDamping=0, angularDamping=0)

    def reset_states(self, states):
        xo, zo, vxo, vzo, xg, zg, thetag, vxg, vzg, omegag = states # 10 DoF

        # Object kinematics
        self.pos_object = [xo,0.0,zo]
        self.vel_object = [vxo,0.0,vzo]

        # Gripper kinematics
        self.pos_gripper = [xg,0.0,zg]
        self.quat_gripper = p.getQuaternionFromEuler([0,thetag,0])
        self.vel_gripper = [vxg,0.0,vzg]
        self.vel_ang_gripper = [0.0,omegag,0.0]

        # Reset the kinematics
        p.resetBasePositionAndOrientation(self.objectUid, self.pos_object, self.quat_object)
        p.resetBasePositionAndOrientation(self.gripperUid, self.pos_gripper, self.quat_gripper)
        p.resetBaseVelocity(self.objectUid, self.vel_object)
        p.resetBaseVelocity(self.gripperUid, self.vel_gripper, self.vel_ang_gripper) # linear and angular vels both in world coordinates

    def run_forward_sim_labeler(self, inputs, print_via_points=True, num_via_points=10):
        t, ax, az = inputs
        interval = int(int(t*240)/num_via_points)
        interval = 3 if interval==0 else interval
        
        # Step the simulation
        via_points = []
        force_on_object = [self.mass_object*ax, 0, self.mass_object*(az-0.0)]
        for i in range(int(t*240)):
            # Apply external force on object
            p.applyExternalForce(self.objectUid, -1, 
                                # [self.mass_object*ax, self.mass_object*(az-0.0), 0], # gravity compensated 
                                force_on_object, # gravity compensated 
                                self.pos_object, 
                                p.WORLD_FRAME)
            p.stepSimulation()
            self.pos_object,_ = p.getBasePositionAndOrientation(self.objectUid)

            # Print object via-points along the trajectory for visualization
            if print_via_points and (i % interval == 0 or i == int(t*240)-1):
                via_points.append([self.pos_object[0], self.pos_object[2]])

            if self.gui:
                time.sleep(10/240)

        # Get the object and gripper states
        self.pos_object,_ = p.getBasePositionAndOrientation(self.objectUid)
        self.vel_object,_ = p.getBaseVelocity(self.objectUid)
        self.pos_gripper,self.quat_gripper = p.getBasePositionAndOrientation(self.gripperUid)
        self.eul_gripper = p.getEulerFromQuaternion(self.quat_gripper)
        self.vel_gripper,self.vel_ang_gripper = p.getBaseVelocity(self.gripperUid)

        new_states = [self.pos_object[0], self.pos_object[2], self.vel_object[0], self.vel_object[2],
                      self.pos_gripper[0], self.pos_gripper[2], self.eul_gripper[1], 
                      self.vel_gripper[0], self.vel_gripper[2], self.vel_ang_gripper[1]
                      ]

        return new_states, via_points

    def finish_sim(self):
        # Clean up and close the simulation
        p.disconnect()


class forwardSimulationPlanePush():
    def __init__(self, gui=False):
        self.visualShapeId = -1
        self.gui = gui
        if self.gui:
            p.connect(p.GUI) # p.GUI
        else:
            p.connect(p.DIRECT) # p.GUI
        p.setAdditionalSearchPath(pybullet_data.getDataPath()) # optionally
        self.g = -9.81
        p.setGravity(0, 0, self.g)

        # self.set_params(params)
        # self.create_shapes()
    
    def set_params(self, params):
        # Kinodynamics
        self.mass_object = params[0]
        self.moment_object = params[1] # moment of inertia
        self.pos_object = [1000,0,0]
        self.quat_object = p.getQuaternionFromEuler([math.pi/2,0,0])
        self.vel_object = [.1,0,0]
        
        self.mass_gripper = params[2]
        self.moment_gripper = params[3]
        self.pos_gripper = [1000,0,2]
        self.quat_gripper = p.getQuaternionFromEuler([0,0,0])
        self.vel_gripper = [0,0,0]
        self.vel_ang_gripper = [0,0,0]

        self.lateralFriction = 0.0

        # Geometrics
        self.z_bodies = .1

    def create_shapes(self):
        # Create a plane
        self.planeId = p.loadURDF("plane.urdf", basePosition=[0,0,-self.z_bodies])
        p.changeDynamics(self.planeId, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
                         rollingFriction=0, linearDamping=0, angularDamping=0)
        
        # Create an object # TODO import complex shapes from files
        objectId = p.createCollisionShape(p.GEOM_BOX, halfExtents=[.2, .6, self.z_bodies])
        self.objectUid = p.createMultiBody(self.mass_object, 
                                           objectId, 
                                           self.visualShapeId, 
                                           self.pos_object,
                                           self.quat_object)
        p.changeDynamics(self.objectUid, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
                         rollingFriction=0, linearDamping=0, angularDamping=0)
        
        # Create a robot
        gripperId = p.createCollisionShape(p.GEOM_BOX, halfExtents=[.5, .5, self.z_bodies])
        self.gripperUid = p.createMultiBody(self.mass_gripper, 
                                       gripperId, 
                                       self.visualShapeId, 
                                       self.pos_gripper,
                                       self.quat_gripper)
        p.changeDynamics(self.gripperUid, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
                         rollingFriction=0, linearDamping=0, angularDamping=0)

    def reset_states(self, states):
        xo, yo, thetao, vxo, vyo, omegao, xg, yg, thetag, vxg, vyg, omegag = states # 12 DoF

        # Object kinematics
        self.pos_object = [xo, yo, 0.0]
        self.quat_object = p.getQuaternionFromEuler([0.0, 0.0, thetao])
        self.vel_object = [vxo, vyo, 0.0]
        self.vel_ang_object = [0.0, 0.0, omegao]

        # Gripper kinematics
        self.pos_gripper = [xg, yg, 0.0]
        self.quat_gripper = p.getQuaternionFromEuler([0.0, 0.0, thetag])
        self.vel_gripper = [vxg, vyg, 0.0]
        self.vel_ang_gripper = [0.0, 0.0, omegag]

        # Reset the kinematics
        p.resetBasePositionAndOrientation(self.objectUid, self.pos_object, self.quat_object)
        p.resetBasePositionAndOrientation(self.gripperUid, self.pos_gripper, self.quat_gripper)
        p.resetBaseVelocity(self.objectUid, self.vel_object, self.vel_ang_object)
        p.resetBaseVelocity(self.gripperUid, self.vel_gripper, self.vel_ang_gripper) # linear and angular vels both in world coordinates

    def run_forward_sim_labeler(self, inputs, print_via_points=True, num_via_points=10):
        t, ax, ay, omega = inputs
        interval = int(int(t*240)/num_via_points)
        interval = 3 if interval==0 else interval

        # Step the simulation
        via_points = []
        force_on_object = [self.mass_object*ax, self.mass_object*ay, 0.0]
        torque_on_object = [0.0, 0.0, self.moment_object*omega]
        for i in range(int(t*240)):
            # Apply external force on object
            p.applyExternalForce(self.objectUid, -1, 
                                force_on_object, # gravity compensated 
                                self.pos_object, 
                                p.WORLD_FRAME)
            p.applyExternalTorque(self.objectUid, -1, 
                                torque_on_object,
                                p.WORLD_FRAME)
            p.stepSimulation()
            self.pos_object,_ = p.getBasePositionAndOrientation(self.objectUid)

            # Print object via-points along the trajectory for visualization

            if print_via_points and (i % interval == 0 or i == int(t*240)-1):
                via_points.append([self.pos_object[0], self.pos_object[1]])

            if self.gui:
                time.sleep(10/240)

        # Get the object and gripper states
        self.pos_object, self.quat_object = p.getBasePositionAndOrientation(self.objectUid)
        self.eul_object = p.getEulerFromQuaternion(self.quat_object) # rad
        self.vel_object, self.vel_ang_object = p.getBaseVelocity(self.objectUid)
        self.pos_gripper, self.quat_gripper = p.getBasePositionAndOrientation(self.gripperUid)
        self.eul_gripper = p.getEulerFromQuaternion(self.quat_gripper)
        self.vel_gripper,self.vel_ang_gripper = p.getBaseVelocity(self.gripperUid)

        new_states = [self.pos_object[0], self.pos_object[1], self.eul_object[2],
                      self.vel_object[0], self.vel_object[1], self.vel_ang_object[2],
                      self.pos_gripper[0], self.pos_gripper[1], self.eul_gripper[2], 
                      self.vel_gripper[0], self.vel_gripper[1], self.vel_ang_gripper[2]
                      ]

        return new_states, via_points

    def finish_sim(self):
        # Clean up and close the simulation
        p.disconnect()


class forwardSimulationWaterSwing():
    def __init__(self, gui=False):
        self.visualShapeId = -1
        self.gui = gui
        if self.gui:
            p.connect(p.GUI) # p.GUI
        else:
            p.connect(p.DIRECT) # p.GUI
        p.setAdditionalSearchPath(pybullet_data.getDataPath()) # optionally
        self.g = -9.81
        # p.setGravity(0, 0, self.g)

        # self.set_params(params)
        # self.create_shapes()
    
    def set_params(self, params):
        # Kinodynamics
        self.mass_object = params[0]
        self.moment_object = params[1] # moment of inertia
        self.pos_object = [1000,0,0]
        self.quat_object = p.getQuaternionFromEuler([0,0,0])
        self.vel_object = [.1,0,0]
        
        self.mass_gripper = params[2]
        self.moment_gripper = params[3]
        self.pos_gripper = [1000,0,2]
        self.quat_gripper = p.getQuaternionFromEuler([0,0,0])
        self.vel_gripper = [0,0,0]
        self.vel_ang_gripper = [0,0,0]

        self.lateralFriction = 0.8

        # Geometrics
        self.y_bodies = .3

    def create_shapes(self):
        # Create a plane
        # self.planeId = p.loadURDF("plane.urdf", basePosition=[0,0,-self.z_bodies])
        # p.changeDynamics(self.planeId, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
        #                  rollingFriction=0, linearDamping=0, angularDamping=0)
        
        # Create an object # TODO import complex shapes from files
        objectId = p.createCollisionShape(p.GEOM_BOX, halfExtents=[.3, self.y_bodies, .3])
        self.objectUid = p.createMultiBody(self.mass_object, 
                                           objectId, 
                                           self.visualShapeId, 
                                           self.pos_object,
                                           self.quat_object)
        p.changeDynamics(self.objectUid, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
                         rollingFriction=0, linearDamping=0, angularDamping=0)
        
        # Create a robot
        # gripperId = p.createCollisionShape(p.GEOM_BOX, halfExtents=[.5, self.y_bodies, .5])
        # self.gripperUid = p.createMultiBody(self.mass_gripper, 
        #                                gripperId, 
        #                                self.visualShapeId, 
        #                                self.pos_gripper,
        #                                self.quat_gripper)
        self.gripperUid = p.loadURDF("asset/4face-bottle.urdf", self.pos_gripper, self.quat_gripper)
        p.changeDynamics(self.gripperUid, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
                         rollingFriction=0, linearDamping=0, angularDamping=0)

    def reset_states(self, states):
        xo, zo, thetao, vxo, vzo, omegao, xg, zg, thetag, vxg, vzg, omegag = states # 12 DoF

        # Object kinematics
        self.pos_object = [xo, 0.0, zo]
        self.quat_object = p.getQuaternionFromEuler([0.0, thetao, 0.0])
        self.vel_object = [vxo, 0.0, vzo]
        self.vel_ang_object = [0.0, omegao, 0.0]

        # Gripper kinematics
        self.pos_gripper = [xg, 0.0, zg]
        self.quat_gripper = p.getQuaternionFromEuler([0.0, thetag, 0.0])
        self.vel_gripper = [vxg, 0.0, vzg]
        self.vel_ang_gripper = [0.0, omegag, 0.0]

        # Reset the kinematics
        p.resetBasePositionAndOrientation(self.objectUid, self.pos_object, self.quat_object)
        p.resetBasePositionAndOrientation(self.gripperUid, self.pos_gripper, self.quat_gripper)
        p.resetBaseVelocity(self.objectUid, self.vel_object, self.vel_ang_object)
        p.resetBaseVelocity(self.gripperUid, self.vel_gripper, self.vel_ang_gripper) # linear and angular vels both in world coordinates

    def run_forward_sim(self, inputs, print_via_points=True, num_via_points=10):
        t, ax, az, omega = inputs
        interval = int(int(t*240)/num_via_points)
        interval = 3 if interval==0 else interval

        # Step the simulation
        via_points = []
        force_on_object = [self.mass_object*ax, 0.0, self.mass_object*az]
        torque_on_object = [0.0, self.moment_object*omega, 0.0]
        for i in range(int(t*240)):
            # Apply external force on object
            p.applyExternalForce(self.objectUid, -1, 
                                force_on_object, # gravity compensated 
                                self.pos_object, 
                                p.WORLD_FRAME)
            p.applyExternalTorque(self.objectUid, -1, 
                                torque_on_object,
                                p.WORLD_FRAME)
            p.stepSimulation()
            self.pos_object, _ = p.getBasePositionAndOrientation(self.objectUid)

            # Print object via-points along the trajectory for visualization
            if print_via_points and (i % interval == 0 or i == int(t*240)-1):
                via_points.append([self.pos_object[0], self.pos_object[2]])

            if self.gui:
                time.sleep(10/240)

        # Get the object and gripper states
        self.pos_object, self.quat_object = p.getBasePositionAndOrientation(self.objectUid)
        self.eul_object = p.getEulerFromQuaternion(self.quat_object) # rad
        self.vel_object, self.vel_ang_object = p.getBaseVelocity(self.objectUid)
        self.pos_gripper, self.quat_gripper = p.getBasePositionAndOrientation(self.gripperUid)
        self.eul_gripper = p.getEulerFromQuaternion(self.quat_gripper)
        self.vel_gripper,self.vel_ang_gripper = p.getBaseVelocity(self.gripperUid)

        new_states = [self.pos_object[0], self.pos_object[2], correct_euler(self.eul_object)[1],
                      self.vel_object[0], self.vel_object[2], self.vel_ang_object[1],
                      self.pos_gripper[0], self.pos_gripper[2], correct_euler(self.eul_gripper)[1], 
                      self.vel_gripper[0], self.vel_gripper[2], self.vel_ang_gripper[1]
                      ]
        return new_states, via_points

    def finish_sim(self):
        # Clean up and close the simulation
        p.disconnect()


class forwardSimulationBoxPivot():
    def __init__(self, gui=False):
        self.visualShapeId = -1
        self.gui = gui
        if self.gui:
            p.connect(p.GUI) # p.GUI
        else:
            p.connect(p.DIRECT) # p.GUI
        p.setAdditionalSearchPath(pybullet_data.getDataPath()) # optionally
        self.g = -9.81
        p.setGravity(0, 0, self.g)

        # self.set_params(params)
        # self.create_shapes()
    
    def set_params(self, params):
        # Kinodynamics
        self.mass_object = params[0]
        self.moment_object = params[1] # moment of inertia
        self.pos_object = [1000,0,0]
        self.quat_object = p.getQuaternionFromEuler([0,0,0])
        self.vel_object = [0,0,0]
        
        self.mass_gripper = params[2]
        self.moment_gripper = params[3]

        self.lateralFriction = 0.7
        self.rest_length = 3
        self.k = 2  # Spring constant

        self.height_spring = 3.7
        self.pos_gripper1 = [1000,0,self.height_spring]
        self.pos_gripper2 = [1000,0,self.height_spring]
        self.quat_gripper1 = p.getQuaternionFromEuler([0,0,0])
        self.quat_gripper2 = p.getQuaternionFromEuler([0,0,0])
        self.vel_gripper1 = [0,0,0]
        self.vel_gripper2 = [0,0,0]

    def create_shapes(self):
        planeId = p.loadURDF("plane.urdf")

        # Add spring base object
        gripperUid1 = p.createCollisionShape(p.GEOM_SPHERE, radius=.3)
        self.gripperUid1 = p.createMultiBody(self.mass_gripper, 
                                    gripperUid1, 
                                    -1, 
                                    [-3, 0, self.height_spring])

        # Add spring tip object
        gripperUid2 = p.createCollisionShape(p.GEOM_SPHERE, radius=.3)
        self.gripperUid2 = p.createMultiBody(self.mass_gripper, 
                                    gripperUid2, 
                                    -1, 
                                    [0, 0, self.height_spring])
        
        # Add box
        objectUid = p.createCollisionShape(p.GEOM_BOX, halfExtents=[2,2,2])
        self.objectUid = p.createMultiBody(self.mass_object, 
                                    objectUid, 
                                    -1, 
                                    [6,0,2])

        p.changeDynamics(self.gripperUid1, -1, lateralFriction=0, spinningFriction=0, 
                            rollingFriction=0, linearDamping=0, angularDamping=0)
        p.changeDynamics(self.gripperUid2, -1, lateralFriction=0, spinningFriction=0, 
                            rollingFriction=0, linearDamping=0, angularDamping=0)
        # p.changeDynamics(planeId, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
        #                     rollingFriction=0, linearDamping=0, angularDamping=0)
        p.changeDynamics(self.objectUid, -1, lateralFriction=self.lateralFriction, spinningFriction=0, 
                            rollingFriction=0, linearDamping=0, angularDamping=0)

        # Create a fixed joint between the cubes, acting like a spring
        self.c_spring = p.createConstraint(self.gripperUid1, -1, self.gripperUid2, -1, p.JOINT_FIXED, [1, 0, 0], [self.rest_length/2, 0, 0], [-self.rest_length/2, 0, 0])

        # Create point-to-point constraints to keep boxes along a line
        pivotInBox = [0, 0, 0] 
        pivotInWorld = [0, 0, self.height_spring]
        constraint1 = p.createConstraint(self.gripperUid1, -1, -1, -1, p.JOINT_PRISMATIC, [1, 0, 0], pivotInBox, pivotInWorld)
        constraint2 = p.createConstraint(self.gripperUid2, -1, -1, -1, p.JOINT_PRISMATIC, [1, 0, 0], pivotInBox, pivotInWorld)

    def reset_states(self, states):
        xo, zo, thetao, vxo, vzo, omegao, xg1, xg2, vg1, vg2 = states # 12 DoF

        # Object kinematics
        self.pos_object = [xo, 0.0, zo]
        self.quat_object = p.getQuaternionFromEuler([0.0, thetao, 0.0])
        self.vel_object = [vxo, 0.0, vzo]
        self.vel_ang_object = [0.0, omegao, 0.0]

        # Gripper kinematics
        self.pos_gripper1 = [xg1, 0.0, self.height_spring]
        self.pos_gripper2 = [xg2, 0.0, self.height_spring]
        self.quat_gripper1 = p.getQuaternionFromEuler([0.0, 0.0, 0.0])
        self.quat_gripper2 = p.getQuaternionFromEuler([0.0, 0.0, 0.0])
        self.vel_gripper1 = [vg1, 0.0, 0.0]
        self.vel_gripper2 = [vg2, 0.0, 0.0]
        self.vel_ang_gripper1 = [0.0, 0.0, 0.0]
        self.vel_ang_gripper2 = [0.0, 0.0, 0.0]

        # Reset the kinematics
        p.resetBasePositionAndOrientation(self.objectUid, self.pos_object, self.quat_object)
        p.resetBaseVelocity(self.objectUid, self.vel_object, self.vel_ang_object)
        p.resetBasePositionAndOrientation(self.gripperUid1, self.pos_gripper1, self.quat_gripper1)
        p.resetBasePositionAndOrientation(self.gripperUid2, self.pos_gripper2, self.quat_gripper2)
        p.resetBaseVelocity(self.gripperUid1, self.vel_gripper1, self.vel_ang_gripper1) # linear and angular vels both in world coordinates
        p.resetBaseVelocity(self.gripperUid2, self.vel_gripper2, self.vel_ang_gripper2)

    def run_forward_sim(self, inputs, print_via_points=True, num_via_points=10):
        # print('!!!run_forward_sim', inputs, p.getEulerFromQuaternion(self.quat_object))
        t, ax, omega = inputs
        interval = int(int(t*240)/num_via_points)
        interval = 3 if interval==0 else interval

        # Step the simulation
        via_points = []
        force_on_object = [self.mass_object*ax, 0.0, 0.0]
        torque_on_object = [0.0, self.moment_object*omega, 0.0]
        for i in range(int(t*240)):
            # Apply external force on object
            self.pos_object, _ = p.getBasePositionAndOrientation(self.objectUid)
            p.applyExternalForce(self.objectUid, -1, 
                                force_on_object, # gravity compensated 
                                self.pos_object, 
                                p.WORLD_FRAME)
            p.applyExternalTorque(self.objectUid, -1, 
                                torque_on_object,
                                p.WORLD_FRAME)
            
            # Get positions of the boxes
            self.pos_gripper1, _ = p.getBasePositionAndOrientation(self.gripperUid1)
            self.pos_gripper2, _ = p.getBasePositionAndOrientation(self.gripperUid2)
            
            # Update the maxForce for the spring constraint
            maxForce = self.k * np.abs(np.linalg.norm(np.array(self.pos_gripper2) - np.array(self.pos_gripper1)) - self.rest_length)
            p.changeConstraint(self.c_spring, maxForce=maxForce)

            p.stepSimulation()

            # Print object via-points along the trajectory for visualization
            if print_via_points and (i % interval == 0 or i == int(t*240)-1):
                via_points.append([self.pos_object[0], self.pos_object[2]])

            if self.gui:
                time.sleep(10/240)

        # Get the object and gripper states
        self.pos_object, self.quat_object = p.getBasePositionAndOrientation(self.objectUid)
        self.eul_object = p.getEulerFromQuaternion(self.quat_object) # rad
        self.vel_object, self.vel_ang_object = p.getBaseVelocity(self.objectUid)
        self.pos_gripper1, _ = p.getBasePositionAndOrientation(self.gripperUid1)
        self.pos_gripper2, _ = p.getBasePositionAndOrientation(self.gripperUid2)
        self.vel_gripper1,_ = p.getBaseVelocity(self.gripperUid1)
        self.vel_gripper2,_ = p.getBaseVelocity(self.gripperUid2)
        # print('!!!run_forward_sim!!!!!!!!', self.eul_object)

        new_states = [self.pos_object[0], self.pos_object[2], self.eul_object[1],
                      self.vel_object[0], self.vel_object[2], self.vel_ang_object[1],
                      self.pos_gripper1[0], self.pos_gripper2[0],  
                      self.vel_gripper1[0], self.vel_gripper2[0], 
                      ]
        return new_states, via_points

    def finish_sim(self):
        # Clean up and close the simulation
        p.disconnect()


class forwardSimulationHerding():
    def __init__(self, gui=False):
        pass

    def set_params(self, params):
        # Kinodynamics
        # self.num_robots = 5
        self.dim = 2
        self.mass_object = params[0]
        self.mass_gripper = params[1]
        self.num_robots = params[2]

    def create_shapes(self):
        pass

    def get_repulsive_force(self, pos_object, pos_gripper, k=5.0):
        # Get the repulsive force
        pos_object_g = np.array(pos_object) - np.array(pos_gripper)
        dist = np.linalg.norm(pos_object_g)
        force_norm_direction = pos_object_g / dist
        if dist <= 0.2:
            force = 5.0 * k * self.mass_gripper * force_norm_direction
        else:
            force = 1.0 * k / dist * self.mass_gripper * force_norm_direction
        return force
    
    def reset_states(self, states):
        xo, yo, vxo, vyo = states[:4] # 4+10+10 DoF

        # Object kinematics
        self.pos_object = np.asarray([xo, yo])
        self.vel_object = np.asarray([vxo, vyo])

        # # Gripper kinematics
        self.pos_gripper = np.asarray(states[4:4+self.dim*self.num_robots])
        self.vel_gripper = np.asarray(states[4+self.dim*self.num_robots:4+2*self.dim*self.num_robots])

    def run_forward_sim(self, inputs, print_via_points=True, num_via_points=10):
        t, ax, ay = inputs
        dt = t / float(num_via_points)

        # Step the simulation
        via_points = []
        for i in range(num_via_points):
            # Calculate the repulsive force
            force_on_object = np.zeros(self.dim)
            for j in range(self.num_robots):
                force_on_object += self.get_repulsive_force(self.pos_object, self.pos_gripper[2*j:2*j+2])

            # Apply the force on the object
            acc_object = force_on_object / self.mass_object
            acc_object += np.asarray([ax, ay])
            self.pos_object += self.vel_object * dt + 0.5 * acc_object * dt * dt
            self.vel_object += acc_object * dt
                        
            # Update robots position
            self.pos_gripper += self.vel_gripper * dt

            # Print object via-points along the trajectory for visualization
            new_states = np.concatenate([self.pos_object, self.vel_object, self.pos_gripper]).tolist()
            if print_via_points:
                via_points.append(new_states[:2])

        return new_states, via_points

    def finish_sim(self):
        pass


class forwardSimulationGripper():
    def __init__(self, gui=False):
        self.visualShapeId = -1
        self.gui = gui
        if self.gui:
            p.connect(p.GUI) # p.GUI
        else:
            p.connect(p.DIRECT) # p.GUI
        p.setAdditionalSearchPath(pybullet_data.getDataPath()) # optionally
        self.g = -9.81
        p.setGravity(0, 0, self.g)
    
    def set_params(self, params):
        # Kinodynamics
        self.mass_object, self.moment_object, self.length_object, self.movable_joints, self.start_gripper_pos = params[0], params[1], params[2], params[3], params[4]
        self.num_movable_joints = len(self.movable_joints)
        self.num_joints = 12
        self.non_movable_joints = [i for i in range(self.num_joints) if i not in self.movable_joints]
        self.pos_object = [0,0,1.]
        self.quat_object = p.getQuaternionFromEuler([0,0,0])
        self.vel_object = [0,0,0]

        self.dim_workspace = 3
        self.lateralFriction = 0.7
        self.stiffness = [1e-2,] * self.num_movable_joints  # P gain for each joint
        self.damping = [1e-1,] * self.num_movable_joints  # D gain for each joint

        self.pos_gripper_base = [0,0,0]
        self.quat_gripper_base = p.getQuaternionFromEuler([math.pi/2,0,0])

    def create_shapes(self):
        # Add a box
        boxId = p.createCollisionShape(p.GEOM_BOX, halfExtents=[self.length_object,]*3)
        self.objectUid = p.createMultiBody(self.mass_object, boxId, -1, self.pos_object)

        # Add a 3-finger gripper
        self.gripperUid = p.loadURDF(fileName='asset/robotiq_3f_gripper_visualization/cfg/robotiq-3f-gripper_articulated.urdf', 
                                basePosition=self.pos_gripper_base, 
                                baseOrientation=self.quat_gripper_base,
                                globalScaling=10,
                                )
        p.changeDynamics(self.gripperUid, -1, mass=0) # fix the base link

    def reset_states(self, states):
        """states: 6+6+9+9 DoF"""
        # Object kinematics
        pos = states[:self.dim_workspace]
        self.pos_object = [pos[0], pos[2], pos[1]] # pos: x,z,y
        self.quat_object = p.getQuaternionFromEuler(states[self.dim_workspace:2*self.dim_workspace])
        self.vel_object = states[2*self.dim_workspace:3*self.dim_workspace]
        self.vel_ang_object = states[3*self.dim_workspace:4*self.dim_workspace]

        # Gripper kinematics
        self.pos_gripper = states[4*self.dim_workspace:4*self.dim_workspace+self.num_movable_joints]
        self.vel_gripper = states[4*self.dim_workspace+self.num_movable_joints:]

        # Reset the kinematics of the object and the gripper
        p.resetBasePositionAndOrientation(self.objectUid, self.pos_object, self.quat_object)
        p.resetBaseVelocity(self.objectUid, self.vel_object, self.vel_ang_object)
        for i, jid in enumerate(self.movable_joints):
            p.resetJointState(self.gripperUid, jid, targetValue=self.pos_gripper[i], targetVelocity=self.vel_gripper[i])

        # Reset joints of the gripper that is not movable
        for i, jid in enumerate(self.non_movable_joints):
            p.resetJointState(self.gripperUid, jid, targetValue=0.0, targetVelocity=0.0)

    def run_forward_sim(self, inputs, print_via_points=True, num_via_points=10):
        t = inputs[0]
        interval = int(int(t*240)/num_via_points)
        interval = 3 if interval==0 else interval

        # Step the simulation
        via_points = []
        force_on_object = [self.mass_object*acc for acc in inputs[1:4]]
        torque_on_object = np.dot(np.diag(self.moment_object), np.asarray(inputs[4:7])).tolist()
        for i in range(int(t*240)):
            # Apply the calculated torques to all joints at once  
            p.setJointMotorControlArray(bodyUniqueId=self.gripperUid,
                                        jointIndices=self.movable_joints,
                                        # controlMode=p.VELOCITY_CONTROL,
                                        # targetVelocities=[.1,]*self.num_movable_joints,
                                        # forces=target_torques)
                                        controlMode=p.POSITION_CONTROL,
                                        targetPositions=self.start_gripper_pos,
                                        targetVelocities=[0,]*self.num_movable_joints,
                                        positionGains=self.stiffness,
                                        velocityGains=self.damping,
                                        forces=[10,]*self.num_movable_joints,)
            
            # Apply external force on object
            self.pos_object, _ = p.getBasePositionAndOrientation(self.objectUid)
            p.applyExternalForce(self.objectUid, -1, 
                                force_on_object,
                                self.pos_object, 
                                p.WORLD_FRAME)
            p.applyExternalTorque(self.objectUid, -1, 
                                torque_on_object,
                                p.WORLD_FRAME)
            
            p.stepSimulation()

            # Print object via-points along the trajectory for visualization
            if print_via_points and (i % interval == 0 or i == int(t*240)-1):
                via_points.append([self.pos_object[0], self.pos_object[2]])
            if self.gui:
                time.sleep(3/240)

        # Get the object and gripper states
        pos, self.quat_object = p.getBasePositionAndOrientation(self.objectUid)
        pos_object_GL = [pos[0], pos[2], pos[1]] # x,z,y
        self.eul_object = p.getEulerFromQuaternion(self.quat_object) # rad
        self.vel_object, self.vel_ang_object = p.getBaseVelocity(self.objectUid)
        joint_states = p.getJointStates(self.gripperUid, self.movable_joints)
        self.pos_gripper = [state[0] for state in joint_states]

        new_states = pos_object_GL + list(self.eul_object) + list(self.vel_object) + list(self.vel_ang_object) + self.pos_gripper
        return new_states, via_points

    def finish_sim(self):
        # Clean up and close the simulation
        p.disconnect()
