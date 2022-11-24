"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 4B - LIDAR Wall Following
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

speed = 0
angle = 0
image = 0
depth_image = 0
counter = 0
red_center = 0
blue_center = 0
red_depth = 0
blue_depth = 0

rc = racecar_core.create_racecar()

# Add any global variables here
#HSV Values
BLUE = ((100, 150, 150), (130, 255, 255))  # The HSV range for the color blue
RED  = ((165, 0, 0),(179, 255, 255)) 

MIN_CONTOUR_AREA = 800

#Distance threshold before turning
dist = 100
# Cone recovery
r_red = False
r_blue = False
#Speed constants
a_speed = 1
t_speed = 0.7
#Angle constants
r_angle = 0.95
t_angle =  1
#Time constants
f_time = 0.85
s_time = 1

########################################################################################
# Functions
########################################################################################
class State(IntEnum):
    search = 0
    to_red = 1
    to_blue = 2
    turn_red = 3
    turn_blue = 4
    stop = 5

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
    
    global speed, angle, r_blue, r_red
    global cur_state, counter

    # Search for contours in the current color image
    update_contour()

    if cur_state == State.search:
        if r_red:
            angle = -r_angle
        if r_blue:
            angle = r_angle
        if red_depth < blue_depth and red_depth != 0:
            cur_state = State.to_red
        if blue_depth < red_depth and blue_depth != 0:
            cur_state = State.to_blue
        elif red_depth != 0:
            cur_state = State.to_red
        elif blue_depth != 0:
            cur_state = State.to_blue

    elif cur_state == State.to_red:
        if r_blue:
            r_blue = False
        if red_depth == 0.0:
            cur_state = State.search
        elif red_depth < dist:
            cur_state = State.turn_red
        else:
            rc_utils.draw_circle(image, red_center)
            angle = rc_utils.remap_range(red_center[1], 0,
                rc.camera.get_width(), -1, 1, True)

    elif cur_state == State.to_blue:
        if r_red:
            r_red = False
        if blue_depth == 0.0:
            cur_state = State.search
        elif blue_depth < dist:
            cur_state = State.turn_blue
        else:
            rc_utils.draw_circle(image, blue_center)
            angle = rc_utils.remap_range(blue_center[1], 0,
                rc.camera.get_width(), -1, 1, True)

    elif cur_state == State.turn_red:
        counter += rc.get_delta_time()
        if counter < f_time:
            angle = t_angle
        elif counter < s_time:
            angle = 0
        else:
            counter = 0
            r_red = True 
            cur_state = State.search

    elif cur_state == State.turn_blue:
        counter += rc.get_delta_time()
        if counter < f_time:
            angle = -t_angle
        elif counter < s_time:
            angle = 0
        else:
            counter = 0
            r_blue = True 
            cur_state = State.search

    if cur_state == (State.to_blue or State.to_red or State.search):
        speed = a_speed
    else:
        speed = t_speed

    #rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    #lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    #speed = rt - lt
    #angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    global cur_state, angle, r_red, r_blue, red_depth, blue_depth
    """
    After start() is run, this function is run at a constant rate that is slower
    than update().  By default, update_slow() is run once per second
    """
    print(f"S:{cur_state} V{speed:.2f} Angle: {angle:.2f} Rec R:{r_red} Rec B:{r_blue}")
    print(f"Red depth:{red_depth:.2F} Blue depth:{blue_depth:.2F}")



########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
