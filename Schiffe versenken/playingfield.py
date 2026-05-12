class PlayingField:

#----------------------------------------------------------------#  
     # Spielfeld erstellen (fieldsize = größe, O = unbeschossenes Feld)
    def create(self):
        return [["O"] * self.fieldsize for _ in range(self.fieldsize)]
#----------------------------------------------------------------#  

#----------------------------------------------------------------#  
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
#----------------------------------------------------------------#  
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
#----------------------------------------------------------------#

#----------------------------------------------------------------#
# Treffer prüfen
    def check_hit(self, shot_position, ships):

        # Alle Schiffe durchgehen
        for ship in ships:

            # Positionen des Schiffs holen
            positions = ship.get_positions()

            # Prüfen ob getroffen
            if shot_position in positions:

                # Treffer zählen
                ship.hits += 1

                # Schiff versenkt?
                if ship.hits == len(positions):

                    print(f"{ship.name} versenkt")

                    # Schiff entfernen
                    ships.remove(ship)

                # Treffer
                return True

        # Kein Treffer
        return False
#----------------------------------------------------------------#

#----------------------------------------------------------------#
    # Spielfeld ausgeben (Gibt das Spielfeld im Terminal aus)
    def output(self, playingfield):

        # Buchstaben oben ausgeben
        print("   " + " ".join([chr(ord("A") + i) for i in range(self.fieldsize)]))

         # Spielfeld Zeile für Zeile ausgeben
        for i, line in enumerate(playingfield):
            print(f"{i + 1:2} " + " ".join(line)) 
#----------------------------------------------------------------#