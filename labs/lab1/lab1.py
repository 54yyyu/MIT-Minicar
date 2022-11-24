"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 1 - Driving in Shapes
"""

########################################################################################
# Imports
########################################################################################

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Put any global variables here

########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """

    #From demo

    global counter
    global isDriving
    global shape

    #Set the initial value
    counter = 0
    isDriving = False
    shape = 0

    # Begin at a full stop
    rc.drive.stop()

    # Print start message
    # TODO (main challenge): add a line explaining what the Y button does
    print(
        ">> Lab 1 - Driving in Shapes\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = drive in a circle\n"
        "    B button = drive in a square\n"
        "    X button = drive in a figure eight\n"
        "    Y button = drive in a s shape\n"
    )


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global counter
    global isDriving
    global shape

    # TODO (warmup): Implement acceleration and steering

    speed = 0
    angle = 0

    speed += rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    speed -= rc.controller.get_trigger(rc.controller.Trigger.LEFT)

    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    rc.drive.set_speed_angle(speed,angle)

    

    if rc.controller.was_pressed(rc.controller.Button.A):
        print("Driving in a circle...")
        counter = 0
        shape = 1
        isDriving = True

        # TODO (main challenge): Drive in a circle



    # TODO (main challenge): Drive in a square when the B button is pressed
    if rc.controller.was_pressed(rc.controller.Button.B):
        print("Driving in a square...")
        counter = 0
        shape = 2
        isDriving = True
        # TODO (main challenge): Drive in a circle
    
    

    # TODO (main challenge): Drive in a figure eight when the X button is pressed
    if rc.controller.was_pressed(rc.controller.Button.X):
        print("Driving in a figure eight...")
        counter = 0
        shape = 3
        isDriving = True
        # TODO (main challenge): Drive in a circle
    
    
    # TODO (main challenge): Drive in a shape of your choice when the Y button
    # is pressed
    if rc. controller.was_pressed(rc.controller.Button.Y):
        print("Driving in a S shape...")
        counter = 0
        shape = 4
        isDriving = True
        # TODO (main challenge): Drive in a circle
    

    if isDriving:

        if shape == 1:
            counter += rc.get_delta_time()
            if counter < 5.5:
                rc.drive.set_speed_angle(1, 1)
            else:
                rc.drive.set_speed_angle(0, 1)
                rc.drive.stop()
                isDriving = False

        if shape == 2:
            counter += rc.get_delta_time()
            if counter < 1.5:
                rc.drive.set_speed_angle(1, 0)
            elif counter < 5.5:
                rc.drive.set_speed_angle(0.1, 1)
            elif counter < 7:
                rc.drive.set_speed_angle(1, 0)
            elif counter < 11.5:
                rc.drive.set_speed_angle(0.1, 1)
            elif counter < 13:
                rc.drive.set_speed_angle(1, 0)
            elif counter < 17.5:
                rc.drive.set_speed_angle(0.1, 1)
            elif counter < 19:
                rc.drive.set_speed_angle(1, 0)
            elif counter < 23:
                rc.drive.set_speed_angle(0.1, 1)

            else:

                rc.drive.stop()
                isDriving = False

        if shape == 3:
            counter += rc.get_delta_time()
            if counter < 3.25:
                rc.drive.set_speed_angle(1, 0)
            elif counter < 6.75:
                rc.drive.set_speed_angle(1, 1)
            elif counter < 8.75:
                rc.drive.set_speed_angle(1, 0)
            elif counter < 11:
                rc.drive.set_speed_angle(1, -1)
            else:
                rc.drive.stop()
                isDriving = False


        if shape == 4:
            counter += rc.get_delta_time()
            if counter < 6.5:
                rc.drive.set_speed_angle(1, 1)
            else:
                rc.drive.stop()
                isDriving = False

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
