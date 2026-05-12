# Schiffe versenken main 

# Funktionen:
# - 10x10 Spielfeld
# - Zufällige Schiffplatzierung
# - Spieler vs Computer
# - Treffer / Wasser
# - Siegbedingung

# Imports
import random #random wird für zufällige Schiffpositionen und Computerschüsse benötigt.
import ships


# Konfiguration
fieldsize = 10 # Größe des Spielfelds
number_of_ships = 5 # Anzahl der Schiffe


# Hauptklasse
class BattleShip:

    # Konstruktor
    def __init__(self):

        # Spielfeldgröße und Anzahl der Schiffe speichern
        self.fieldsize = fieldsize 
        self.number_of_ships = number_of_ships 

        # Spielfelder erstellen
        self.player_field = self.playingfield_create()
        self.computer_field = self.playingfield_create()

        
        # Schiffe erstellen
        self.player_ships = [

                                ships.Ship("Two Ship", ships.two_ship),
                                ships.Ship("Three Ship", ships.three_ship),
                                ships.Ship("Four Ship", ships.four_ship),
                                ships.Ship("Z Ship", ships.z_ship),
                                ships.Ship("T Ship", ships.t_ship)

                                                                                ]
        # Testpositionen setzen
        self.player_ships[0].horizontal_line = 0
        self.player_ships[0].vertical_line = 0

        self.player_ships[1].horizontal_line = 2
        self.player_ships[1].vertical_line = 2

        self.player_ships[2].horizontal_line = 4
        self.player_ships[2].vertical_line = 1

        self.player_ships[3].horizontal_line = 6
        self.player_ships[3].vertical_line = 3

        self.player_ships[4].horizontal_line = 1
        self.player_ships[4].vertical_line = 6

        # Alle Schiffe platzieren
        for ship in self.player_ships:

            self.ships_place(ship,self.player_field)


    # Spielfeld erstellen (fieldsize = größe, O = unbeschossenes Feld)
    def playingfield_create(self):
        return [["O"] * self.fieldsize for _ in range(self.fieldsize)]


    # Schiffe platzieren
    def ships_place(self, ship, playingfield):

        # Alle Positionen des Schiffs holen
        positions = ship.get_positions()

        # Alle Positionen durchgehen
        for position in positions:

            # Positionen aufteilen
            horizontal_line = position[0]
            vertical_line = position[1]

            # Schiff ins Spielfeld setzen
            playingfield[horizontal_line][vertical_line] = "■"
           
    
    #Kollisionen prüfen (liegt Schiff außerhalb?, überschneidung anderer Schiffe?)

    def check_collision(self, ship, playingfield):

        # Alle Positionen des Schiffs holen
        positions = ship.get_positions()

        # Alle Positionen prüfen
        for position in positions:

            # Positionen aufteilen
            horizontal_line = position[0]
            vertical_line = position[1]

            #Prüfung ob Schiff bei pos kleiner 0 oder größer 10 
            if (horizontal_line < 0 or horizontal_line >= self.fieldsize or vertical_line < 0 or vertical_line >= self.fieldsize):

                return True

            # Prüfen ob dort bereits ein Schiff liegt
            if playingfield[horizontal_line][vertical_line] == "■":

                return True

        # Keine Kollision gefunden? schiff darf plaziert werden
        return False

    # Spielfeld ausgeben (Gibt das Spielfeld im Terminal aus)
    def playingfield_output(self, playingfield):

        # Buchstaben oben ausgeben
        print("   " + " ".join([chr(ord("A") + i) for i in range(self.fieldsize)]))

         # Spielfeld Zeile für Zeile ausgeben
        for i, line in enumerate(playingfield):
            print(f"{i + 1:2} " + " ".join(line)) 


    # Positionen einlesen (Liest Benutzereingaben wie: A3, C4, usw.)
    def position_set(self, playingfield):
        while True:

             # Eingabe einlesen
            position = input("Setze das Schiff: ").upper()


            # Spiel frühzeitig beenden
            if position == "EXIT":
                print("Spiel beendet")
                exit()


            # Eingabe zu kurz?
            if len(position) < 2:
                continue

            # Zeile bestimmen
            horizontal_line = int(position[1:]) - 1

            # Spalte bestimmen
            vertical_line = ord(position[0]) - ord("A")

            # Prüfen ob innerhalb des Spielfelds
            if 0 <= horizontal_line < self.fieldsize and 0 <= vertical_line < self.fieldsize:

                # Prüfen ob dort bereits geschossen wurde
                if playingfield[horizontal_line][vertical_line] in ["X", "~"]:
                    print("Hier wurde schon geschossen")
                    continue

                # Position zurückgeben
                return[horizontal_line, vertical_line]


    # Spiel starten (Hauptschleife Ablauf: Spieler schießt, Com schießt, Spielfelder aktualisieren, Sieg prüfen )
    def start(self):
        print("Schiffe versenken Simulator")

        # Computerfeld anzeigen
        self.playingfield_output(self.player_field)


        # Hauptschleife
        while True:

            # Spielerzug
            print("\n Du bist dran:")

            # Spieler Schussposition 
            player_shot = self.position_set(self.computer_field)

            # Treffer?
            if player_shot in self.computer_ships:
                print("Schiff getroffen")

                # Treffer markieren
                self.computer_field[player_shot[0]][player_shot[1]] = "X"

                # Schiff entfernen
                self.computer_ships.remove(player_shot)

            else:
                print("Wasser")

                # Wasser markieren
                self.computer_field[player_shot[0]][player_shot[1]] = "~"

            # Siegüberprüfung Spieler
            if len(self.computer_ships) == 0:
                print("Du hast gewonnen")
                break

            # Computer Zug
            while True:

                # Zufälligen Schuss generieren
                computer_shot = [random.randint(0, self.fieldsize -1), random.randint(0, self.fieldsize - 1)]

                # Nur schießen, wenn dort noch nicht geschossen wurde
                if self.player_field[computer_shot[0]][computer_shot[1]] not in ["X", "~"]:
                    break
            
            # Computerschuss anzeigen
            print(f"Computer schiesst auf {chr(ord('A') + computer_shot[1])}{computer_shot[0] + 1}")

            # Treffer?
            if computer_shot in self.player_ships:

                 # Treffer markieren
                self.player_field[computer_shot[0]][computer_shot[1]] = "X"

                # Schiff entfernen
                self.player_ships.remove(computer_shot)

            else:
                # Wasser markieren
                self.player_field[computer_shot[0]][computer_shot[1]] = "~"

            # Spielfelder ausgeben
            print("\n Dein Spielfeld:")
            self.playingfield_output(self.player_field)

            print("\n Computer Spielfeld: ")
            self.playingfield_output(self.computer_field)

             # Siegüberprüfung Computer
            if len(self.player_ships) == 0:
                print("Du hast verloren!")
                break

            # Punktestand anzeigen
            else: 
                print(f"Spielstand: Spieler: {self.number_of_ships - len(self.player_ships)};" f"Computer: {self.number_of_ships - len(self.computer_ships)}")

# Programmstart
if __name__ == "__main__":

    # Spielobjekt erstellen
    game = BattleShip()

    # Spiel starten
    game.start()

