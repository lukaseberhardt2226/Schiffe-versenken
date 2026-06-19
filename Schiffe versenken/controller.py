
###### DATEI FÜR PICO  ----> in Pico Ornder code.py
## Wenn fehler -> in Console eingeben: py -m pip install pyserial

import board
import digitalio
import time
import neopixel
import supervisor
import sys

#
# HARDWARE CONTROLLER (PICO)
#

class Controller:
    # initialisierung der hardware
    def __init__(self):
        
        #
        # BUTTONS
        #
        
        # buttons definieren (dictionary für pin und klare namen)
        self.buttons = [
            {"pin": board.GP2, "name": "B"},
            {"pin": board.GP3, "name": "A"},
            {"pin": board.GP4, "name": "X"},
            {"pin": board.GP5, "name": "Y"},
            {"pin": board.GP6, "name": "DOWN"},
            {"pin": board.GP7, "name": "RIGHT"},
            {"pin": board.GP8, "name": "UP"},
            {"pin": board.GP9, "name": "LEFT"}
        ]
        
        # button objekte erzeugen und konfigurieren
        for button in self.buttons:
            button["objekt"] = digitalio.DigitalInOut(button["pin"])
            button["objekt"].direction = digitalio.Direction.INPUT
            button["objekt"].pull = digitalio.Pull.UP
            button["letzter_zustand"] = True # pull-up bedeutet True = nicht gedrückt

        #
        # FEEDBACK (MOTOR & LED)
        #

        # vibrationsmotor installieren
        self.motor = digitalio.DigitalInOut(board.GP0)
        self.motor.direction = digitalio.Direction.OUTPUT
        
        # led-streifen installieren (8 leds an pin 15)
        self.leds = neopixel.NeoPixel(board.GP15, 8, brightness=0.1)

    def get_input(self):
        # schaut ob ein knopf gedrückt wurde
        for button in self.buttons:
            aktuell = button["objekt"].value
            # zustandswechsel erkennen
            if aktuell != button["letzter_zustand"]:
                button["letzter_zustand"] = aktuell
                # wenn wert False ist, wurde der knopf gedrückt
                if aktuell == False:
                    return button["name"]
        return None

    def vibrate(self, duration):
        # motor an
        self.motor.value = True
        time.sleep(duration)
        # motor aus
        self.motor.value = False
    
    def set_led_all(self, r, g, b):
        # alle leds auf eine farbe setzen
        for i in range(8):
            self.leds[i] = (r, g, b)

    def set_led_single(self, index, r, g, b):
        # eine einzelne led ansteuern
        self.leds[index] = (r, g, b)

    def check_serial(self):
        # prüft ob der pc über usb einen befehl geschickt hat
        if supervisor.runtime.serial_bytes_available:
            befehl = sys.stdin.readline().strip()
            return befehl
        return None

#
# HAUPTPROGRAMM AUF DEM PICO
#

if __name__ == "__main__":
    pico_controller = Controller()
    
    # start-animation (kurzes blaues leuchten und vibrieren)
    pico_controller.set_led_all(0, 0, 50) 
    pico_controller.vibrate(0.2)
    pico_controller.set_led_all(0, 0, 0) 
    
    # endlos-schleife auf dem mikrocontroller
    while True:
        # 1. tasten prüfen und an pc senden
        tasten_druck = pico_controller.get_input()
        if tasten_druck:
            # schickt z.b. "UP" oder "A" als reinen text an den pc
            print(tasten_druck)
            time.sleep(0.05) # entprellen (verhindert mehrfach-auslösung)
            
        # 2. pc befehle empfangen und ausführen
        pc_befehl = pico_controller.check_serial()
        if pc_befehl:
            # befehl zerlegen (z.b. "led_all 255 0 0")
            teile = pc_befehl.split()
            if len(teile) > 0:
                kommando = teile[0]
                
                # befehle verarbeiten
                if kommando == "vibrate":
                    pico_controller.vibrate(0.35)
                elif kommando == "led_all" and len(teile) == 4:
                    pico_controller.set_led_all(int(teile[1]), int(teile[2]), int(teile[3]))
                elif kommando == "led_single" and len(teile) == 5:
                    pico_controller.set_led_single(int(teile[1]), int(teile[2]), int(teile[3]), int(teile[4]))


#------- Weilche Tasten Gibt es ---------#
# Aktionstasten:
#   A ist normaler Schuss / Bestätigung
#   Y Fähikeit beenden / Spiel beenden
#   B Fähikeitentaste
#   X Dreht Schiffe/ Fähikeiten
# 
# Bewegungstasten:
#   <-  Bewegung nach Links 
#   ->  Bewegung nach Rechts
#   ⬇️   Bewegung nach Unten
#   ⬆️   Bewegung nach rechts 