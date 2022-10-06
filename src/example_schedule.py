#!/usr/bin/env python3
from nicegui import ui
from rosys.automation import Automator, Schedule, automation_controls
from rosys.driving import Driver, Odometer, robot_object
from rosys.geometry import Point, Prism
from rosys.hardware import WheelsSimulation


async def drive_around() -> None:
    while True:
        await driver.drive_to(Point(x=1, y=0))
        await driver.drive_to(Point(x=0, y=0))


async def drive_home() -> None:
    await driver.drive_to(Point(x=-3, y=0))


shape = Prism.default_robot_shape()
wheels = WheelsSimulation()
odometer = Odometer(wheels)
driver = Driver(wheels, odometer)
automator = Automator(wheels, None, default_automation=drive_around)

locations = {
    (52.520008, 13.404954): 'Berlin',
    (40.730610, 73.935242): 'New York',
    None: 'no location',
}
schedule = Schedule(automator, on_activate=drive_around, on_deactivate=drive_home,
                    location=None, locations=locations, is_enabled=True)
schedule.fill(False)  # disable at all times so the user can enable it manually
schedule.is_enabled = True  # the schedule must be enabled to take any effect

with ui.row().classes('items-end'):
    schedule.ui()
    with ui.column().classes('items-end'):
        with ui.row():
            automation_controls(automator)
        with ui.scene(height=360):
            robot_object(shape, odometer)

ui.run(title='RoSys')
