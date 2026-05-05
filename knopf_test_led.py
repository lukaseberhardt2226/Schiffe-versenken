import board
import neopixel
import digitalio

# LED
pixels = neopixel.NeoPixel(board.GP1, 5, brightness=0.3, auto_write=False)

# Button
button = digitalio.DigitalInOut(board.GP2)
button.direction = digitalio.Direction.INPUT

while True:
    if button.value == False:   # gedrückt (meist LOW)
        pixels.fill((0, 255, 0))   # grün AN
    else:
        pixels.fill((0, 0, 0))     # AUS

    pixels.show()