import board
import digitalio
import time
import neopixel

class Controller:
    def __init__(self):

    #Buttons instalieren !!!!    
        self.buttons = [
            {"pin": board.GP2, "name": "B"},
            {"pin": board.GP3, "name": "A"},
            {"pin": board.GP4, "name": "X"},
            {"pin": board.GP5, "name": "Y"},
            {"pin": board.GP6, "name": "Runter"},
            {"pin": board.GP7, "name": "Rechts"},
            {"pin": board.GP8, "name": "Oben"},
            {"pin": board.GP9, "name": "Links"},]
    #Objekt erzeugen
        for button in self.buttons:
            button["objekt"] = digitalio.DigitalInOut(button["pin"])    #Erstelllt Butoom Objekt
            button["objekt"].direction = digitalio.Direction.INPUT      #
            button["objekt"].pull = digitalio.Pull.UP
            button["letzter_zustand"] = True

    #Motor instalieren
        self.motor = digitalio.DigitalInOut(board.GP0)
        self.motor.direction = digitalio.Direction.OUTPUT
    
    #LED- Streifen instalieren 
        self.leds = neopixel.NeoPixel(board.GP15, 8)

        

    def get_input(self):
            for button in self.buttons:
                aktuell = button["objekt"].value
                if aktuell != button["letzter_zustand"]:
                    if aktuell == False:
                        button["letzter_zustand"] = aktuell
                        return (button["name"] + " losgelassen")
                    else:
                        button["letzter_zustand"] = aktuell
                        return(button["name"] + " gedrückt")
            time.sleep(0.05)


    def vibrate(self, duration):
        self.motor.value= True
        time.sleep(duration)
        self.motor.value=False
    

    def set_led_all(self, farbe):
        for i in range(8):
            self.leds[i]= farbe

    def set_led_single(self,index,farbe):
        self.leds[index]= farbe

    def help(self):
        print("Controller Funktionen:")
        print("get_input()              -> gibt gedrückten Button zurück")
        print("vibrate(duration)        -> Motor vibriert x Sekunden")
        print("set_led(farbe)           -> alle LEDs eine Farbe (R,G,B)")
        print("set_led_single(i, farbe) -> einzelne LED ansteuern")

if __name__ == "__main__":
    controller = Controller()
    controller.set_led_all((255, 0, 0))  # rot
    controller.vibrate(0.5)    # Motor vibriert 0.5 Sekunden
    controller.set_led_single(1,(0,255,0))
    controller.help()
    while True:
        eingabe = controller.get_input()
        if eingabe:
            print(eingabe)
        time.sleep(0.05)