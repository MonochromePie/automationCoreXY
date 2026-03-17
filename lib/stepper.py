import machine
import utime
import time
from lib.blink import set_brightness, potentiometer
import math

# --- PIN DEFINITIONS ---
nEN0 = machine.Pin(9, machine.Pin.OUT)
STEP0 = machine.Pin(7, machine.Pin.OUT)
DIR0 = machine.Pin(8, machine.Pin.OUT)

nEN1 = machine.Pin(12, machine.Pin.OUT)
STEP1 = machine.Pin(10, machine.Pin.OUT)
DIR1 = machine.Pin(11, machine.Pin.OUT)

# Limit switches (Active Low)
LX = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
LY = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)

# --- GLOBAL POSITION ---
current_x = 0.0
current_y = 0.0



# --- CONFIGURATION ---

# Motor and pulley configuration
MICROSTEPPING = 16
MOTOR_STEPS = 200
PULLEY_TEETH = 60
GT2_PITCH = 2.0  # mm per tooth

# Derived values
MM_PER_REV = PULLEY_TEETH * GT2_PITCH
PULSES_PER_REV = MOTOR_STEPS * MICROSTEPPING
MM_PER_PULSE = MM_PER_REV / PULSES_PER_REV

DEFAULT_SPEED_MM = 100  # mm/sec
HOMING_SPEED_MM = 100  # mm/sec  

M0Inv = 1
M1Inv = 1

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def step_motor(dx, dy, speed_mm=DEFAULT_SPEED_MM, monitorLX=False, monitorLY=False):
    # CoreXY kinematics
    # dx, dy in mm
    # speed_mm: desired speed in mm/sec
    # Invert X direction
    #dx = -dx
    pulses_x = int(abs(dx) / MM_PER_PULSE)
    pulses_y = int(abs(dy) / MM_PER_PULSE)
    # CoreXY equations
    pulses_A = abs(pulses_x - pulses_y)
    pulses_B = abs(pulses_x + pulses_y)
    dir_A = 1-M0Inv if (dx - dy) >= 0 else M0Inv
    dir_B = 1-M1Inv if (dx + dy) >= 0 else M1Inv
    # Convert speed_mm to pulses/sec
    speed_pulses = speed_mm / MM_PER_PULSE
    delay = int(1_000_000 / speed_pulses / 2)
    # Set directions
    DIR0.value(dir_A)
    DIR1.value(dir_B)
    # Step A and B motors
    
    max_step = max(pulses_A, pulses_B)
    for i in range(max_step):
        # Check limit switches if monitoring
        pulse_A = map_range(i, 0, max_step, 0, pulses_A) if pulses_A > 0 else 0
        pulse_B = map_range(i, 0, max_step, 0, pulses_B) if pulses_B > 0 else 0
        if monitorLX and LX.value() == 1:
            print("Limit X triggered, aborting move.")
            return
        if monitorLY and LY.value() == 1:
            print("Limit Y triggered, aborting move.")
            return
        if i < pulses_A:
            STEP0.value(1)
        if i < pulses_B:
            STEP1.value(1)
        time.sleep_us(delay)
        STEP0.value(0)
        STEP1.value(0)
        time.sleep_us(delay)

def enable_all(state=True):
    val = 0 if state else 1
    nEN0.value(val)
    nEN1.value(val)

def move_xy(dx_mm, dy_mm, speed_mm=DEFAULT_SPEED_MM):
    """Translates XY mm to CoreXY motor steps."""
    global current_x, current_y
    # magnitude = (dx_mm**2 + dy_mm**2)**0.5
    # direction = [dx_mm/ magnitude if magnitude != 0 else 0, dy_mm/ magnitude if magnitude != 0 else 0]
    # speed_vector = [direction[0] * speed, direction[1] * speed]

    # # CoreXY Kinematics
    # steps_a = int((dx_mm - dy_mm) * STEPS_PER_MM / 100) 
    # steps_b = int((dx_mm + dy_mm) * STEPS_PER_MM / 100) 
    
    # time_needed = magnitude / speed if speed != 0 else 0
    # start = time.time()
    # timer = time.time() - start 
    # print(time_needed, "seconds needed for move")
    # print(f"Moving to: dX:{dx_mm}, dY:{dy_mm} | Steps A:{steps_a} B:{steps_b}")
    # while timer < time_needed:
    #     step_motors(steps_a, steps_b, speed)
    #     # print(f"X:{current_x:.2f} Y:{current_y:.2f} | Steps A:{steps_a} B:{steps_b}")
    #     timer = time.time() - start
    # step_motors(0, 0, 0)
    step_motor(dx_mm, dy_mm, speed_mm=speed_mm)
    current_x += dx_mm
    current_y += dy_mm

def move_absolute(x_mm, y_mm, speed_mm=DEFAULT_SPEED_MM):
    """Moves to an absolute XY coordinate based on the home position."""
    global current_x, current_y
    dx = x_mm - current_x
    dy = y_mm - current_y
    move_xy(dx, dy, speed_mm=speed_mm)


def X_switch():
    return LX.value()

def Y_switch():
    return LY.value()

def home_axes():
    """Simple Homing: Moves toward switches until triggered."""
    global current_x, current_y
    enable_all(True)
    print("Homing...")
    set_brightness(1, 0, 0, 1) # Red during homing

    # Home Y (Moves until LY is 0)
    while not(LY.value()):
        # step_motors(2, -2, 2) # Small steps in -Y direction
        step_motor(0, 1, speed_mm=HOMING_SPEED_MM, monitorLY=True) # Move in -Y direction until switch triggered
        
    
    # Home X (Moves until LX is 0)
    while not(LX.value()):
        # step_motors(-2, -2, 2) # Small steps in -X direction
        step_motor(1, 0, speed_mm=HOMING_SPEED_MM, monitorLX=True) # Move in -X direction until switch triggered
    current_x = 0.0
    current_y = 0.0
    print("Homing Complete.")

# def go_center_from_home():
#     start = time.time()
#     timer = time.time() - start
#     while timer < 1.5:
#         set_brightness(0, 0, 1, 1) 
#         step_motors(0, 2, 40)
#         timer = time.time() - start

def draw_circle(centerX, centerY, radius, speed=50, turn=1): #counterclockwise by default clockwise = 0
    steps = 10
    cx = centerX
    cy = centerY
    for i in range(steps):
        angle = (i / steps) * 2 * math.pi
        if turn == 0:
            angle = 2 * math.pi - angle
        targetX = centerX + radius * math.cos(angle)
        targetY = centerY + radius * math.sin(angle)
        move_xy(targetX - cx, targetY - cy, speed)
        cx = targetX
        cy = targetY