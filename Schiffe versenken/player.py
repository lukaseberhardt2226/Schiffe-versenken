import ships

# Player-Klasse

# Verwaltet alle Informationen eines Spielers:
# - Spielername
# - Spielfeld speicherung
# - Schiffsliste
# - Anzahl der verwendeten Schiffe

#----------------------------------------------------------------#

#----------------------------------------------------------------#
class Player:

    def __init__(self, name, fieldsize, number_of_ships):

        # Spielername
        self.name = name

        # Spielfeldgröße
        self.fieldsize = fieldsize

        # Speichert hier das Spielfeld des Spielers
        self.field = []

#----------------------------------------------------------------#

#----------------------------------------------------------------#

        # Schiffe erstellen
        all_ships = [

                        ships.Ship("2er Schiff", ships.two_ship),
                        ships.Ship("3er Schiff", ships.three_ship),
                        ships.Ship("4er Schiff", ships.four_ship),
                        ships.Ship("Z Schiff", ships.z_ship),
                        ships.Ship("T Schiff", ships.t_ship)
                                                                    ]

        # Nur gewünschte Anzahl nehmen
        self.ships = all_ships[:number_of_ships]

#----------------------------------------------------------------#
#----------------------------------------------------------------#