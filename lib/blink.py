
from machine import Pin, ADC, PWM
from utime import sleep
import time

red = PWM(Pin(2, Pin.OUT))
red.freq(1000)
green = PWM(Pin(3, Pin.OUT))
green.freq(1000)
blue = PWM(Pin(4, Pin.OUT))
blue.freq(1000)
button1 = Pin(0, Pin.IN, Pin.PULL_UP) # Turn on LED and change colors
button2 = Pin(1, Pin.IN, Pin.PULL_UP) # TUrn off LED


potentiometer = ADC(28) # Assuming a potentiometer is connected to ADC0 for brightness control

colors = [(1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1), (0,1,1), (1,1,1)]
color_index = 0

def set_pin_duty(pin, value):
    # Convert 0-1 range to 0-65535 for duty_u16
    duty_value = int(value * 65535)
    pin.duty_u16(duty_value)

def set_brightness(r, g, b, brightness):
    # Scale the RGB values by the brightness (0.0 to 1.0)
    r = r * brightness # 0-1
    g = g * brightness
    b = b * brightness
    set_pin_duty(red, r)
    set_pin_duty(green, g)
    set_pin_duty(blue, b)

# def on_switch():
#     return not button1.value() or switch1.value()

# def off_switch():
#     return not button2.value() or switch2.value()

# print("LED starts flashing...")
# r, g, b = colors[color_index]
# button_pushed_timer = 0
# while True:
#     try:
#         brightness = potentiometer.read_u16() / 65535  # Read potentiometer value and normalize to 0.0-1.0
#         if on_switch() and time.ticks_ms() - button_pushed_timer > 200: # Button 1 pressed
#             button_pushed_timer = time.ticks_ms()
#             color_index = (color_index + 1) % len(colors)
#             r, g, b = colors[color_index]
#         elif off_switch(): # Button 2 pressed
#             r, g, b = (0, 0, 0) # Turn off LED
#         set_brightness(r, g, b, brightness)
#     except KeyboardInterrupt:
#         break
# print("Finished.")
