print("Hello World!")
import digitalio
import board
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.1)
    led.value = False
    time.sleep(0.1)
    break 

# Pin GP1 als Ausgang definieren
led_pin = board.GP1 

# Konfiguration
led = digitalio.DigitalInOut(led_pin)
led.direction = digitalio.Direction.OUTPUT

print(f"LED an {led_pin} blinkt jetzt...")

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
    print("LED")