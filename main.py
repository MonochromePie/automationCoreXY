import sys
import time
import uselect
import math
import utime

# import matplotlib.pyplot as plt

from lib.stepper import enable_all, home_axes, move_absolute, move_xy, draw_circle, step_motor
from lib.blink import set_brightness, potentiometer
try:
    enable_all(False)
    print("READY")
    home_axes()
    # go_center_from_home()>
    time.sleep(1)
    centerX = -100
    centerY = -100
    # move to center
    circle_radius = 1
    move_absolute(centerX, centerY)
    move_absolute(centerX + circle_radius, centerY)
    # time.sleep(1)
    # # draw circle
    # x_diff = 0
    # y_diff = 0 

    # time.sleep(1)
    # move_absolute(centerX + x_diff, centerY + y_diff, speed=10)
    # time.sleep(1)
    # move_absolute(centerX + 10, centerY + 0, speed=10)
    # time.sleep(1)
    # move_absolute(centerX + x_diff, centerY + y_diff, speed=10)
    # time.sleep(1)
    # move_absolute(centerX + 10, centerY + 0, speed=10)
    # time.sleep(1)
    # move_absolute(centerX + x_diff, centerY + y_diff, speed=10)
    # time.sleep(1)
    # move_absolute(centerX + 10, centerY + 0, speed=10)
    
    start_time = utime.ticks_ms()

    dt= 0 
    while True:
        speedVal = 5

        time_diff = utime.ticks_ms() - start_time # milliseconds since start


        time_startLoop = float(time_diff)
        x_diff = circle_radius * math.cos(time_diff / 1000) # Convert ms to seconds for smoother movement
        y_diff = circle_radius * math.sin(time_diff/ 1000)
        step_motor(x_diff, y_diff)
        print(f"X_diff: {x_diff:.2f} Y_diff: {y_diff:.2f}")
        # move_absolute(centerX - x_diff, centerY - y_diff)




        # print(centerX + x_diff*dt, centerY + y_diff*dt)


        # move_xy(0, -10, speed=50) # Move 50mm in X and Y at 100mm/s
        # move_xy(0, 10, speed=25) # Move 50mm in X and Y at 100mm/s
        # draw_circle(centerX, centerY, radius=10, speed=speedVal)}

        # time_endLoop = utime.ticks_ms() - start_time
        # dt = (time_endLoop - time_star3tLoop) / 1000
        
        time.sleep(0.001)

except KeyboardInterrupt:
    pass
finally:
    enable_all(False)
    print("BYE")