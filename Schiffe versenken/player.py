import ships

class Player:

    def __init__(self, name, fieldsize, number_of_ships):

        # Spielername
        self.name = name

        # Spielfeldgröße
        self.fieldsize = fieldsize

        # Spielfeld erstellen
        self.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]

        # Schiffe erstellen
        all_ships = [

                        ships.Ship("Two Ship", ships.two_ship),
                        ships.Ship("Three Ship", ships.three_ship),
                        ships.Ship("Four Ship", ships.four_ship),
                        ships.Ship("Z Ship", ships.z_ship),
                        ships.Ship("T Ship", ships.t_ship)
                                                                    ]

        # Nur gewünschte Anzahl nehmen
        self.ships = all_ships[:number_of_ships]