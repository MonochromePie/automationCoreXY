import sys
import time
import uselect
import math

from lib.stepper import enable_all, home_axes, move_absolute, step_motors, go_center_from_home, move_xy, draw_circle
from lib.blink import set_brightness, potentiometer
try:
    enable_all(False)
    print("READY")
    home_axes()
    # go_center_from_home()
    time.sleep(1)
    centerX = 70
    centerY = 70
    # move to center 
    circle_radius = 5
    move_absolute(centerX, centerY, speed=50)
    move_absolute(centerX + circle_radius, centerY, speed=50)
    time.sleep(1)
    # draw circle
    start_time = time.time()
    while True:
        speedVal = 50
        time_diff = time.time() - start_time # seconds since start
        x_diff = circle_radius * math.cos(time_diff)
        y_diff = circle_radius * math.sin(time_diff)
        print(f"Time: {time_diff:.2f}s | Speed: {speedVal} | X_diff: {x_diff:.2f} Y_diff: {y_diff:.2f}")
        move_absolute(centerX + x_diff, centerY + y_diff, speed=speedVal)
        

        # move_xy(0, -10, speed=50) # Move 50mm in X and Y at 100mm/s
        # move_xy(0, 10, speed=25) # Move 50mm in X and Y at 100mm/s
        # draw_circle(centerX, centerY, radius=10, speed=speedVal)

        
        time.sleep(0.001)

except KeyboardInterrupt:
    pass
finally:
    enable_all(False)
    print("BYE")