import board
import neopixel

pixels = neopixel.NeoPixel(board.GP1, 8)

pixels.fill((0, 0, 0)) #rot, grün blau
pixels.show()
print("test")
