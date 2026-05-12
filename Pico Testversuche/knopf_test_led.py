import board
import neopixel
import digitalio
import time

# 🔌 LED-Streifen
NUM_LEDS = 8
pixels = neopixel.NeoPixel(board.GP1, NUM_LEDS, brightness=0.3, auto_write=False)

# 🔘 Button
button = digitalio.DigitalInOut(board.GP2)
button.direction = digitalio.Direction.INPUT

# Zustand
led_on = False
last_state = True

while True:
    current = button.value

    # Button gedrückt → Zustand wechseln
    if current == False and last_state == True:
        led_on = not led_on
        time.sleep(0.2)  # Entprellen

    last_state = current

    # LEDs setzen
    if led_on:
        # jede LED andere Farbe
        pixels[0] = (0, 255, 0)
        pixels[1] = (0, 255, 0)
        pixels[2] = (0, 255, 0)
        pixels[3] = (255, 255, 255)
        pixels[4] = (255, 255, 255)
        pixels[5] = (255, 0, 0)
        pixels[6] = (255, 0, 0)
        pixels[7] = (255, 0, 0)
    else:
        pixels.fill((0, 0, 0))  # alles aus

    pixels.show()