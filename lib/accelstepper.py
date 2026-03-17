import time
import machine

class Stepper:
    def __init__(self, step_pin, dir_pin):
        self.step_pin = machine.Pin(step_pin, machine.Pin.OUT)
        self.dir_pin = machine.Pin(dir_pin, machine.Pin.OUT)
        self.current_pos = 0
        self.target_pos = 0
        self.speed = 0.0
        self.max_speed = 1000.0  # steps per second
        self.acceleration = 500.0 # steps per second^2
        
        self._last_step_time = time.ticks_us()
        self._step_interval = 0

    def move_to(self, absolute):
        self.target_pos = absolute
        self.compute_new_speed()

    def move(self, relative):
        self.move_to(self.current_pos + relative)

    def set_max_speed(self, speed):
        self.max_speed = speed

    def set_acceleration(self, acceleration):
        self.acceleration = acceleration

    def distance_to_go(self):
        return self.target_pos - self.current_pos

    def compute_new_speed(self):
        # simplified trapezoidal profile check
        distance_to = self.distance_to_go()
        if distance_to == 0:
            self._step_interval = 0
            self.speed = 0.0
            return
            
        # Simplified constant speed for now to ensure CoreXY sync
        # CoreXY requires synchronized movement, so we drive speed externally
        pass 

    def run_speed(self):
        # Stepping at constant speed for synchronized CoreXY
        if self._step_interval == 0:
            return False

        time_now = time.ticks_us()
        if time.ticks_diff(time_now, self._last_step_time) >= self._step_interval:
            self.step_pin.value(1)
            self.current_pos += 1 if self.dir_pin.value() else -1
            self.step_pin.value(0)
            self._last_step_time = time_now
            return True
        return False

    def set_speed(self, speed):
        if speed == self.speed:
            return
        self.speed = speed
        if speed == 0.0:
            self._step_interval = 0
        else:
            self._step_interval = abs(1000000.0 / speed)
            self.dir_pin.value(1 if speed > 0 else 0)

class CoreXYKinematics:
    def __init__(self, stepper_a, stepper_b, steps_per_mm):
        self.motor_a = stepper_a
        self.motor_b = stepper_b
        self.steps_per_mm = steps_per_mm
        self.x = 0.0
        self.y = 0.0

    def move_to(self, x_mm, y_mm, speed_mm_s):
        dx = x_mm - self.x
        dy = y_mm - self.y
        
        # CoreXY equations
        steps_a = (dx - dy) * self.steps_per_mm
        steps_b = (dx + dy) * self.steps_per_mm
        
        time_to_move = (math.sqrt(dx**2 + dy**2) / speed_mm_s) if speed_mm_s > 0 else 0.1
        
        speed_a = steps_a / time_to_move if time_to_move else 0
        speed_b = steps_b / time_to_move if time_to_move else 0
        
        self.motor_a.move(steps_a)
        self.motor_b.move(steps_b)
        
        self.motor_a.set_speed(speed_a)
        self.motor_b.set_speed(speed_b)

        # Blocking run for synchronized start (a Timer or uasyncio would be non-blocking)
        while self.motor_a.distance_to_go() != 0 or self.motor_b.distance_to_go() != 0:
            # We would need a more robust Bresenham line algorithm for perfect sync,
            # this is a foundational translation for basic moves.
            pass
            
        self.x = x_mm
        self.y = y_mm
