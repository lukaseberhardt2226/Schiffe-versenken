#Fahigkeitspunkte:
# Pro Runde: 1 Punkt
# Pro eigenes Schiff getroffen: 1 Punkt
# LED gibt an wieviele Punkte man grade hat in Farbe Grün!!!!

# Fähigkeitstaste wird gededrückt:
#   - Danach kann eine Fähikeit ausgewählt werden (FALLS GENUG PUNKTE)          -->     mit Y kann die Fähigkeitenauswahl beendet werden
#   - mit der Taste A kann die kann die Fähikeit ausgewählt werden              -->     mit Y kann die Fähigkeitenauswahl beendet werden
#   - danach kann sie durch die Bewegungstaste den Ort festgelegt werden        -->     mit Y kann die Fähigkeitenauswahl beendet werden
#   - Folgend kann mit der Taste A die Fähikeit ausgeführt werden               -->     mit Y kann die Fähigkeitenauswahl beendet werden
from controller import Controller
from playingfield import PlayingField
from cursor import Cursor 
import time 


class Skill_Show:

    def __init__(self, controller):
        self.controller = controller
        self.punkte = 0
    
    def punkte_hinzufuegen(self, anzahl):
        self.punkte+=anzahl
        self.update_leds()
        # punkte erhöhen
        # LED updaten
    
    def punkte_abziehen(self, anzahl):
        self.punkte-=anzahl
        if self.punkte<0:
            self.punkte=0
        self.update_leds()
        # punkte abziehen
        # LED updaten
    
    def update_leds(self):
        for i in range(8):
            if i < self.punkte:
                self.controller.set_led_single(i, (0, 255, 0))  # grün an
            else:
                self.controller.set_led_single(i, (0, 0, 0))



class Skills:
    def __init__(self, controller, cursor, skill_show,spielfeld):
        self.controller = controller
        self.cursor = cursor
        self.skill_show = skill_show
        self.skills = ["Mine", "Scannen", "Air-Strike"]
        self.ausgewaehlt = 0
        self.spielfeld= spielfeld 

    def mine_legen(self):
        if self.skill_show.punkte>=2:
            self.skill_show.punkte_abziehen(2)
            x= self.cursor.x
            y= self.cursor.y
            self.spielfeld.matrix[y][x]= "M"

        else:
            print("zu wenig punkte")

    def scannen(self):
        objekte=0
        if self.skill_show.punkte>=3:
            self.skill_show.punkte_abziehen(3)
            x,y= self.cursor.x,self.cursor.y
            for dy in range(-1,2):
                for dx in range(-1,2):
                    nx= x+dx
                    ny= y+dy
                    if 0 <= nx < 10 and 0 <= ny < 10:
                        if self.spielfeld.matrix[ny][nx] != "O":  # nicht Wasser
                            objekte += 1
            print(f"{objekte} Objekte gefunden")
            self.controller.vibrate(0.5) 
                
        else:
            print("zu wenig punkte")

    def air_strike(self):
        if self.skill_show.punkte >= 5:
            self.skill_show.punkte_abziehen(5)

            modus = "zeile"
            while True:
                eingabe = self.controller.get_input()
                if eingabe == "X gedrückt":
                    if modus == "zeile":
                        modus = "spalte"
                    else:
                        modus = "zeile"
                    print(modus)  # anzeigen was gerade aktiv ist
                elif eingabe == "A gedrückt":
                    break
            x, y = self.cursor.x, self.cursor.y
            if modus == "zeile":
                for i in range(10):
                    self.spielfeld.matrix[y][i] = "X"
            else:
                for i in range(10):
                    self.spielfeld.matrix[i][x] = "X"
        else:
            print("zu wenig punkte")

    def select_skill(self):
        while True:
            eingabe = self.controller.get_input()
            if eingabe == "Rechts gedrückt":
                self.ausgewaehlt = (self.ausgewaehlt + 1) % 3
                print(self.skills[self.ausgewaehlt])
            elif eingabe == "Links gedrückt":
                self.ausgewaehlt = (self.ausgewaehlt - 1) % 3
                print(self.skills[self.ausgewaehlt])
            elif eingabe == "A gedrückt":
                # ausgewählte Fähigkeit ausführen
                if self.ausgewaehlt == 0:
                    self.mine_legen()
                elif self.ausgewaehlt == 1:
                    self.scannen()
                elif self.ausgewaehlt == 2:
                    self.air_strike()
                break
            elif eingabe == "Y gedrückt":
                return None  # abbrechen
            time.sleep(0.05)


# Fähigkeit: Mine            Kosten: 2 Puntke 
#Legt eine Mine in eigenes Spielfeld. 
#Wenn Mine getroffen:
#           Vibrationsmotor 2 sec und LED ROT 
#           hat man 2 Random- Schüsse beim Gegnerischen Spielfeld 


# Fähigekeit: Scannen        Kosten: 3 Punkte
#Scannt 3x3 Feld beim Gegner und gibt an wieviel Objekte(Schiffe & Minen) sich in dem Berreich befinden 
#Gibts aus z.B 3 Objekte 
# Ziegt an der LED an wieviele objekte sich in dem Berreich befinden 


# Fähigkeit: Air- Strike 5 Punkte
# Zerstört ganze Spalte oder Zeile 
# Drehung nach Azswahl möglich 
# 
# 


