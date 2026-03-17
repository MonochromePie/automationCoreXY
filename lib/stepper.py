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
MICROSTEPPING = 2
MOTOR_STEPS = 400
PULLEY_TEETH = 20 # Note: Changed from 60 to 20 (standard GT2) - adjust if yours is actually 60!
GT2_PITCH = 2.0

MM_PER_REV = PULLEY_TEETH * GT2_PITCH
STEPS_PER_MM = (MOTOR_STEPS * MICROSTEPPING) / MM_PER_REV

# --- CORE FUNCTIONS ---

def enable_all(state=True):
    val = 0 if state else 1
    nEN0.value(val)
    nEN1.value(val)

def step_motors(steps_a, steps_b, speed_mm_s):
    # Set Directions
    DIR0.value(1 if steps_a > 0 else 0)
    DIR1.value(1 if steps_b > 0 else 0)
    
    abs_a = abs(steps_a)
    abs_b = abs(steps_b)
    max_steps = max(abs_a, abs_b)
    
    if max_steps == 0: return

    # Calculate delay (Simplified - no acceleration)
    # Delay = 1 / (steps_per_mm * speed) / 2 (for high/low toggle)
    delay = 1.0 / (STEPS_PER_MM * speed_mm_s * 2)

    for i in range(max_steps):
        if i < abs_a: STEP0.value(1)
        if i < abs_b: STEP1.value(1)
        utime.sleep(delay)
        STEP0.value(0)
        STEP1.value(0)
        utime.sleep(delay)

def move_xy(dx_mm, dy_mm, speed=50):
    """Translates XY mm to CoreXY motor steps."""
    global current_x, current_y
    magnitude = (dx_mm**2 + dy_mm**2)**0.5
    direction = [dx_mm/ magnitude if magnitude != 0 else 0, dy_mm/ magnitude if magnitude != 0 else 0]
    speed_vector = [direction[0] * speed, direction[1] * speed]

    # CoreXY Kinematics
    steps_a = int((dx_mm - dy_mm) * STEPS_PER_MM) 
    steps_b = int((dx_mm + dy_mm) * STEPS_PER_MM) 
    
    time_needed = magnitude / speed if speed != 0 else 0
    print(f"{time_needed:.2f} seconds needed for move")
    print(f"Moving to: dX:{dx_mm}, dY:{dy_mm} | Steps A:{steps_a} B:{steps_b}")
    
    step_motors(steps_a, steps_b, speed)
    
    current_x += dx_mm
    current_y += dy_mm

def move_absolute(x_mm, y_mm, speed=50):
    """Moves to an absolute XY coordinate based on the home position."""
    global current_x, current_y
    dx = x_mm - current_x
    dy = y_mm - current_y
    move_xy(dx, dy, speed)



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
        step_motors(2, -2, 40) # Small steps in -Y direction
        
    
    # Home X (Moves until LX is 0)
    while not(LX.value()):
        step_motors(-2, -2, 40) # Small steps in -X direction
    
    current_x = 0.0
    current_y = 0.0
    print("Homing Complete.")

def go_center_from_home():
    start = time.time()
    timer = time.time() - start
    while timer < 1.5:
        set_brightness(0, 0, 1, 1) 
        step_motors(0, 2, 40)
        timer = time.time() - start

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