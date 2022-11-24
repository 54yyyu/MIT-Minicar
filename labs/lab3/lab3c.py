"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3C - Depth Camera Wall Parking
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
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
avg_d = 0
differ =0


########################################################################################
# Functions
########################################################################################
class State(IntEnum):
    search = 0
    approach = 1
    stop = 2
    special = 3

cur_state: State = State.search


def start():
    """
    This function is run once every time the start button is pressed
    """
    global speed
    global angle
    global cur_state
    global avg_d
    global differ

    cur_state = State.search

    # Initialize variables
    speed = 0
    angle = 0

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(speed, angle)

    # Have the car begin at a stop
    #rc.drive.stop()

    rc.set_update_slow_time(0.5)

    # Print start message
    print(">> Lab 3C - Depth Camera Wall Parking..................")


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Park the car 20 cm away from the closest wall with the car directly facing
    # the wall
    global speed
    global angle
    global cur_state
    global avg_d
    global differ

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    depth_image = cv.GaussianBlur(depth_image, (1, 1), 0)
    depth_image = (depth_image - 0.01) % 10000
    center_distance = rc_utils.get_depth_image_center_distance(depth_image)


    x, y = rc.camera.get_height() // 2, rc.camera.get_width() * 1//8
    distance = depth_image[x, y]
    further_y = rc.camera.get_width() * 7//8

    further_distance = depth_image[x, further_y]

    differ = distance - further_distance
    avg_d = (distance + further_distance) // 2


    if cur_state == State.search:

        angle = rc_utils.remap_range(rc_utils.clamp(differ, -100, 100), -100, 100, 1, -1)

        speed = -abs(angle)

        if abs(differ) < 20 or center_distance > 100:
            cur_state = State.approach


    elif cur_state == State.approach:
        if avg_d < 4000:
            speed = rc_utils.remap_range((avg_d - 20), -100, 100, -0.5, 0.5)

            if avg_d < 25:
                cur_state = State.stop

            if avg_d < 31 and abs(differ) > 2:
                cur_state = State.search
            speed = rc_utils.clamp(speed, -0.5, 0.5)
            angle = angle = rc_utils.remap_range(rc_utils.clamp(differ, -30, 30), -30, 30, -1, 1)
        else:
            cur_state = State.special


    elif cur_state == State.stop:
        if avg_d < 4000:
            if abs(differ) < 1:
                if avg_d > 20:
                    speed = 0
                else:
                    speed = rc_utils.remap_range(rc_utils.clamp(avg_d, 10, 20), 10, 20, -1, 0)
            else:
                cur_state = State.search

        
    elif cur_state == State.special:
        print("SPECIAL!!!!!!!!!!!")
        speed = -1
        if avg_d < 4000:
            cur_state = State.search


    rc.drive.set_speed_angle(speed, angle)

    rc.display.show_depth_image(depth_image, points=[(x,y), (x, further_y)])

def update_slow():
    global avg_d
    global differ
    print("Speed:", speed)
    print("Distance:", avg_d)
    print("Differ:", differ)  

    if cur_state == State.search:
        print("Adjusting Angle")
    elif cur_state == State.approach:
        print("Approaching")
    elif cur_state == State.stop:
        print("Stopping")



########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
