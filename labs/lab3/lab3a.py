"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3A - Depth Camera Safety Stop
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
from enum import IntEnum
sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Add any global variables here

########################################################################################
# Functions
########################################################################################
class State(IntEnum):
    speeding = 0
    stopping = 1
    special = 2

cur_state: State = State.speeding


def start():

    global cur_state

    cur_state = State.speeding

    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(
        ">> Lab 3A - Depth Camera Safety Stop\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Right bumper = override safety stop\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = print current speed and angle\n"
        "    B button = print the distance at the center of the depth image"
    )


def update():

    global cur_state
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # Use the triggers to control the car's speed
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = rt - lt

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    #depth_image = cv.GaussianBlur(depth_image, (3, 3), 0)
    depth_image = (depth_image - 0.01) % 10000
    center_distance = rc_utils.get_depth_image_center_distance(depth_image)

    # TODO (warmup): Prevent forward movement if the car is about to hit something.
    # Allow the user to override safety stop by holding the right bumper.
    
    cropped_view_height = (rc.camera.get_height() // 3) * 2
    #top_left_inclusive = (0, rc.camera.get_width() // 4)
    #bottom_right_exclusive = (cropped_view_height, (rc.camera.get_width() // 4) * 3)

    top_left_inclusive = (rc.camera.get_height() // 3, rc.camera.get_width() // 4)
    bottom_right_exclusive = (cropped_view_height, (rc.camera.get_width() // 4) * 3)

    depth_image = rc_utils.crop(depth_image, top_left_inclusive, bottom_right_exclusive)
    #depth_image = cv.GaussianBlur(depth_image, (3, 3), 0)

    x, y = rc_utils.get_closest_pixel(depth_image)
    distance = depth_image[x, y]
    further_x = rc_utils.clamp(x - 40, 0, cropped_view_height)

    further_distance = depth_image[further_x, y]

    print(distance, further_distance)
    
    if cur_state == State.speeding:
        if rc.controller.is_down(rc.controller.Button.RB):
            print("Override")
            pass
        else:
            if distance > 4000 or further_distance > 4000:
                #speed = 
                pass
            else:
                if distance < 65 and distance > 0:
                    if not further_distance > distance + 5:
                        print("Stop at:", further_distance - distance)
                        speed = -1
                        cur_state = State.stopping
                        
    elif cur_state == State.stopping:
        print("Stopping Mode")
        speed = -1
        if further_distance > distance + 500:
            cur_state = State.speeding

        d = further_distance - distance

        if further_distance < 10000 and distance < 30:
                            speed = 0
                            rc.drive.stop()
                            print("Stop")
        if d <250 and d>200:
            speed = 0
            print("Special")
            cur_state = State.special


    elif cur_state == State.special:
        speed = 0
        if further_distance > distance + 500:
            cur_state = State.speeding


    # Use the left joystick to control the angle of the front wheels
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    #if rc.controller.is_down(rc.controller.Button.A):
    #print("Speed:", speed, "Angle:", angle)

    # Print the depth image center distance when the B button is held down
    #if rc.controller.is_down(rc.controller.Button.B):
    #print("Center distance:", center_distance)

    # Display the current depth image
    rc.display.show_depth_image(depth_image, points=[(x, y), (further_x, y)])

    # TODO (stretch goal): Prevent forward movement if the car is about to drive off a
    # ledge.  ONLY TEST THIS IN THE SIMULATION, DO NOT TEST THIS WITH A REAL CAR.

    # TODO (stretch goal): Tune safety stop so that the car is still able to drive up
    # and down gentle ramps.
    # Hint: You may need to check distance at multiple points.



########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
