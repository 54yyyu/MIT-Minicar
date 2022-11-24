"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Phase 1 Challenge - Cone Slaloming
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
from enum import IntEnum
sys.path.insert(1, "../../library")
sys.path.insert(0, "../../library")
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
BLUE = ((100, 150, 150), (130, 255, 255))  # The HSV range for the color blue
RED  = ((165, 0, 0),(179, 255, 255)) 

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
red_center = None
blue_center = None  # The (pixel row, pixel column) of contour
red_depth = 0.0
blue_depth = 0.0
image = 0
depth_image = 0

# Add any global variables here

########################################################################################
# Functions
########################################################################################
class State(IntEnum):
    search = 0
    red_cone = 1
    blue_cone = 2

cur_state: State = State.search

def get_contour(HSV):
    global image
    global depth_image

    image = rc.camera.get_color_image()
    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    #depth_image = cv.GaussianBlur(depth_image, (3, 3), 0)
    depth_image = (depth_image - 0.01) % 10000

    if image is None:
        red_center = None
        red_depth = 0.0
        blue_center = None
        blue_depth = 0.0
    else:
        # Find all of the orange contours
        contours = rc_utils.find_contours(image, HSV[0], HSV[1])
        # Select the largest contour
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
        if contour is not None:
            center = rc_utils.get_contour_center(contour)
            depth = depth_image[center]
        else:
            center = None
            depth = 0.0
        return contour, center, depth

def update_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global red_center, blue_center, red_depth, blue_depth

    global depth_image
    global image 

    image = rc.camera.get_color_image()
    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    #depth_image = cv.GaussianBlur(depth_image, (3, 3), 0)
    depth_image = (depth_image - 0.01) % 10000

    # Find all of the red, blue contours and find their largest
    red_contour, red_center, red_depth = get_contour(RED)
    blue_contour, blue_center, blue_depth = get_contour(BLUE)

    if red_contour is not None:
        # Draw contour onto the image
        rc_utils.draw_contour(image, red_contour)
        rc_utils.draw_circle(image, red_center)

    else:
        red_center = None
        red_depth = 0.0
        blue_center = None
        blue_depth = 0.0

    # Display the image to the screen
    rc.display.show_color_image(image)

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
    print(">> Phase 1 Challenge: Cone Slaloming")


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Slalom between red and blue cones.  The car should pass to the right of
    # each red cone and the left of each blue cone.
    
    global speed
    global angle
    global cur_state

    # Search for contours in the current color image
    update_contour()

    if cur_state == State.search:

    elif: cur_state == State.red_cone:



    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = rt - lt
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    """
    After start() is run, this function is run at a constant rate that is slower
    than update().  By default, update_slow() is run once per second
    """



########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
