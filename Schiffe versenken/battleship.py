
# Funktionen:
# - 10x10 Spielfeld
# - Spieler platziert Schiffe
# - Computer Schiffe werden automatisch platziert
# - Spieler vs Computer
# - Treffer / Wasser
# - Siegbedingung

#----------------------------------------------------------------#

#----------------------------------------------------------------#

# Imports
import random #random wird für zufällige Schiffpositionen und Computerschüsse benötigt.
import player
import playingfield 

#----------------------------------------------------------------#

#----------------------------------------------------------------#

# Konfiguration
fieldsize = 7 # Größe des Spielfelds 10
number_of_ships = 2 # Anzahl der Schiffe 5

#----------------------------------------------------------------#

#----------------------------------------------------------------#

# Hauptklasse
class BattleShip:

    # Konstruktor
    def __init__(self):

        #Ausgabe Spielname                 
        print("\nSchiffe versenken Simulator")

        # Spielfeldgröße speichern
        self.fieldsize = fieldsize

        # Anzahl Schiffe speichern
        self.number_of_ships = number_of_ships

        # Spielfeld Objekt erstellen
        self.playingfield = (playingfield.PlayingField())

        # Spielfeldgröße weitergeben
        self.playingfield.fieldsize = (self.fieldsize)

        # Spieler erstellen
        self.player = player.Player("Spieler", self.fieldsize, self.number_of_ships)

        # Computer erstellen
        self.computer = player.Player("Computer", self.fieldsize, self.number_of_ships)

        # Spielfelder erstellen
        self.player.field = self.playingfield.create()
        self.computer.field = self.playingfield.create()

#----------------------------------------------------------------#

#----------------------------------------------------------------#

    # Positionen einlesen (Liest Benutzereingaben wie: A3, C4, usw.)
    def position_set(self, playingfield, text):
        while True:

             # Eingabe einlesen
            position = input(text).upper()

            # Spiel frühzeitig beenden
            if position == "EXIT":
                print("Spiel beendet")
                exit()

            # try/except um Fehler abfangen bei ungültigen Eingaben
            try:

                # Zahl aus Eingabe holen (Zeile) Bsp.: "A3" -> 3
                horizontal_line = (int(position[1:]) - 1)

                # Buchstaben in Zahl umwandeln (Spalte) Bsp.: "A" -> 0
                vertical_line = (ord(position[0]) - ord("A"))

            # try/except um Fehler abfangen bei ungültiger Eingabe
            except:
                print("Ungültige Eingabe")
                continue

            # Prüfen ob innerhalb des Spielfelds
            if 0 <= horizontal_line < self.fieldsize and 0 <= vertical_line < self.fieldsize:
               
                # Prüfen ob dort bereits geschossen wurde
                if playingfield[horizontal_line][vertical_line] in ["X", "~"]:
                    print("Hier wurde schon geschossen")
                    continue

                # Position zurückgeben
                return[horizontal_line, vertical_line]
            else:
                print("Position außerhalb des Spielfelds") 

#----------------------------------------------------------------#

#----------------------------------------------------------------#

    #Schiff plazierung Spieler
    def player_place_ships(self):

    # Alle Schiffe durchgehen
        for ship in self.player.ships:

            while True:

                print(f"\nPlatziere: {ship.name}")

                # Spielfeld anzeigen
                self.playingfield.output(self.player.field)

                # Position vom Spieler holen
                position = self.position_set(self.player.field, "Schiff platzieren: ")

                # Position setzen
                ship.horizontal_line = position[0]
                ship.vertical_line = position[1]

                # Rotation abfragen
                rotate = input("Schiff rotieren? (y/n): ").lower()

                # Schiff drehen
                if rotate == "y":
                    ship.rotate()

                # Kollision prüfen
                if self.playingfield.check_collision(ship,self.player.field):
                    print("Ungültige Position")
                    continue
                
                # Schiff platzieren
                self.playingfield.ships_place(ship,self.player.field)
                break

#----------------------------------------------------------------#

#----------------------------------------------------------------#

    # Computer Schiffe platzieren
    def computer_place_ships(self):

        # Alle Computer-Schiffe durchgehen
        for ship in self.computer.ships:

            while True:

                # Schiff zurücksetzen
                ship.shape = [line [:] for line in ship.original_shape]

                # Zufällige Position erzeugen
                ship.horizontal_line = random.randint(0,self.fieldsize - 1)

                ship.vertical_line = random.randint(0, self.fieldsize - 1)

                # Zufällige Rotation
                rotate = random.randint([0, 1])

                # Schiff rotieren
                if rotate == 1:
                    ship.rotate()

                # Kollision prüfen
                if self.playingfield.check_collision(ship, self.computer.field):
                    continue

                # Schiff platzieren
                self.playingfield.ships_place(ship, self.computer.field)
                break

#----------------------------------------------------------------#

#----------------------------------------------------------------#

    # Spiel starten (Hauptschleife Ablauf: Spieler schießt, Com schießt, Spielfelder aktualisieren, Sieg prüfen )
    def start(self):
        
        # Spieler platziert Schiffe
        self.player_place_ships()

        # Computer platziert Schiffe
        self.computer_place_ships()  

        # Computerfeld anzeigen
        self.playingfield.output(self.player.field)

        # Hauptschleife
        while True:

            print("\nDein Spielfeld:")
            self.playingfield.output(self.player.field)

            print("\nComputer Spielfeld:")
            self.playingfield.output(self.computer.field)

            # Spielerzug
            print("\nDu bist dran:")


            # Spieler Schussposition 
            player_shot = self.position_set(self.computer.field, "Schuss eingeben: ")

            # Treffer?
            if self.playingfield.check_hit(player_shot,self.computer.ships):
                print("Schiff getroffen")

                # Treffer markieren
                self.computer.field[player_shot[0]][player_shot[1]] = "X"

            else:
                print("Wasser")

                # Wasser markieren
                self.computer.field[player_shot[0]][player_shot[1]] = "~"

            # Siegüberprüfung Spieler
            if len(self.computer.ships) == 0:
                print("\nDu hast gewonnen")
                break

            # Computer Zug
            while True:

                # Zufälligen Schuss generieren
                computer_shot = [random.randint(0, self.fieldsize -1), random.randint(0, self.fieldsize - 1)]

                # Nur schießen, wenn dort noch nicht geschossen wurde
                if self.player.field[computer_shot[0]][computer_shot[1]] not in ["X", "~"]:
                    break
            
            # Computerschuss anzeigen
            print(f"Computer schiesst auf {chr(ord('A') + computer_shot[1])}{computer_shot[0] + 1}")

            # Treffer?
            if self.playingfield.check_hit(computer_shot, self.player.ships):
                print("Computer hat getroffen")

                # Treffer markieren
                self.player.field[computer_shot[0]][computer_shot[1]] = "X"

            else:
                print("Computer trifft Wasser")
                # Wasser markieren
                self.player.field[computer_shot[0]][computer_shot[1]] = "~"

            # Spielfelder ausgeben
            print("\n Dein Spielfeld:")
            self.playingfield.output(self.player.field)

            print("\n Computer Spielfeld: ")
            self.playingfield.output(self.computer.field)

             # Siegüberprüfung Computer
            if len(self.player.ships) == 0:
                print("Du hast verloren!")
                break

            # Punktestand anzeigen
            else: 
                print(f"Spielstand: Spieler: {self.number_of_ships - len(self.computer.ships)};" f" Computer: {self.number_of_ships - len(self.player.ships)}")

#----------------------------------------------------------------# 

#----------------------------------------------------------------#