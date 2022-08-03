#!/usr/bin/env python3
from nicegui import ui

from rosys.driving import KeyboardControl, Odometer, RobotObject, Steerer
from rosys.geometry import Prism
from rosys.hardware import RobotBrain, SerialCommunication, WheelsHardware, WheelsSimulation, communication

# setup
shape = Prism.default_robot_shape()
if SerialCommunication.is_possible():
    communication = SerialCommunication()
    robot_brain = RobotBrain(communication)
    wheels = WheelsHardware(robot_brain)
else:
    wheels = WheelsSimulation()
odometer = Odometer(wheels)
steerer = Steerer(wheels)

# ui
KeyboardControl(steerer)
with ui.scene():
    RobotObject(shape, odometer)
ui.label('hold SHIFT to steer with the keyboard arrow keys')

# start
ui.run(title='RoSys')
