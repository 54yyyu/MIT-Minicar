"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 2B - Color Image Cone Parking
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
from enum import IntEnum
import time
sys.path.insert(1, "../../library")
sys.path.insert(0, '../library')
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# >> Constants
# The smallest contour we will recognize as a valid contour
MIN_CONTOUR_AREA = 30

# The HSV range for the color orange, stored as (hsv_min, hsv_max)
ORANGE = ((10, 100, 100), (20, 255, 255))

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour

########################################################################################
# Functions
########################################################################################
class State(IntEnum):
    search = 0
    approach = 1
    stop = 2
    back = 3

cur_state: State = State.search


def update_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global contour_center
    global contour_area

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # Find all of the orange contours
        contours = rc_utils.find_contours(image, ORANGE[0], ORANGE[1])

        # Select the largest contour
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            # Calculate contour information
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_center)

        else:
            contour_center = None
            contour_area = 0

        # Display the image to the screen
        #rc.display.show_color_image(image)


def start():
    """
    This function is run once every time the start button is pressed
    """
    global speed
    global angle
    global cur_state

    cur_state = State.search

    # Initialize variables
    speed = 0
    angle = 0

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(speed, angle)

    # Set update_slow to refresh every half second
    rc.set_update_slow_time(0.5)

    # Print start message
    print(">> Lab 2B - Color Image Cone Parking")


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global speed
    global angle
    global cur_state

    # Search for contours in the current color image
    update_contour()

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    #depth_image = cv.GaussianBlur(depth_image, (3, 3), 0)
    depth_image = (depth_image - 0.01) % 10000
    center_distance = rc_utils.get_depth_image_center_distance(depth_image)

    # TODO (warmup): Prevent forward movement if the car is about to hit something.
    # Allow the user to override safety stop by holding the right bumper.

    x, y = contour_center
    distance = depth_image[contour_center]

    print(distance, contour_area)

    # TODO: Park the car 30 cm away from the closest orange cone
    

    if cur_state == State.search:
        speed, angle = 1, 1

        if contour_area != 0:
            cur_state = State.approach

    elif cur_state == State.approach:
        if contour_center is not None:
            angle = (rc_utils.remap_range(contour_center[1],
                0, rc.camera.get_width(), -1, 1))

        if contour_area != 0:
            if distance > 30:
                speed = 0.30
            else:
                speed = 3 * (distance - 30)
                if speed > 0.30: speed = 0.30
                elif speed < -0.30: speed = -0.30 

            if distance < 31 and distance > 29 and speed < 0.02:
                if abs(angle) > 0.20 and distance < 25:
                    cur_state = State.back
                    print(angle)
                else:
                    cur_state = State.stop
        else:
            cur_state = State.search


    elif cur_state == State.stop:
        speed, angle = 0, 0
        if distance < 29 or distance > 31:
            cur_state = State.approach

    elif cur_state == State.back:
        speed, angle = -0.1, 0

        if distance < 50:
            cur_state = State.approach

    rc.drive.set_speed_angle(speed, angle)

    # Display the current depth image
    rc.display.show_depth_image(depth_image, points=[(x, y)])


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
