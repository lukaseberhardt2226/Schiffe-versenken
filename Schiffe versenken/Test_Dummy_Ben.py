import serial
import time
from serial_controller import SerialController
from cursor import Cursor
from fähigkeiten import Skill_Show, Skills

# Dummy-Spielfeld (echtes kommt vom Kollegen)
class DummySpielfeld:
    def __init__(self):
        self.matrix = [["O"] * 10 for _ in range(10)]

# Verbindung zum Pico
pico = serial.Serial('/dev/tty.usbmodem1101', 115200)
time.sleep(2)  # kurz warten bis Verbindung steht

# Alles zusammenstecken
controller = SerialController(pico)
cursor = Cursor()
spielfeld = DummySpielfeld()
skill_show = Skill_Show(controller)
skills = Skills(controller, cursor, skill_show, spielfeld)

# Startpunkte zum Testen
skill_show.punkte_hinzufuegen(10)

# Zustand
zustand = "spielen"

print("=== TEST LÄUFT ===")
print("Bewegung: Pfeiltasten | B: Fähigkeiten | A: Schuss")
print("Punkte: 5 (LEDs sollten grün leuchten)")

while True:
    if pico.in_waiting:
        eingabe = pico.readline().decode().strip()
        
        # nur auf "gedrückt" reagieren
        if "gedrückt" not in eingabe:
            continue
        
        print(f"\n[{zustand}] Taste: {eingabe}")
        
        if zustand == "spielen":
            if "Rechts" in eingabe:
                cursor.move("Rechts")
                print("Cursor:", cursor.get_position())
            elif "Links" in eingabe:
                cursor.move("Links")
                print("Cursor:", cursor.get_position())
            elif "Oben" in eingabe:
                cursor.move("Oben")
                print("Cursor:", cursor.get_position())
            elif "Runter" in eingabe:
                cursor.move("Unten")
                print("Cursor:", cursor.get_position())
            elif "B" in eingabe:
                zustand = "menue"
                print(">>> Fähigkeiten-Menü offen. Skill:", skills.skills[skills.ausgewaehlt])
            elif "A" in eingabe:
                print("SCHUSS bei", cursor.get_position())
                controller.vibrate(0.5)
        
        elif zustand == "menue":
            ergebnis = skills.taste_im_menue(eingabe)
            if ergebnis == "fertig" or ergebnis == "abbruch":
                zustand = "spielen"
                print(">>> zurück ins Spiel")
            elif ergebnis == "airstrike":
                zustand = "airstrike"
                print(">>> Air-Strike Modus:", skills.modus)
        
        elif zustand == "airstrike":
            ergebnis = skills.air_strike_taste(eingabe)
            if ergebnis == "fertig":
                zustand = "spielen"
                print(">>> Air-Strike ausgeführt, zurück ins Spiel")
    
    time.sleep(0.02)