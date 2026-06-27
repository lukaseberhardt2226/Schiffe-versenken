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
# Falls mehr Schiffe als Schiffstypen -> wiederholung der vorhandenen Schiffstypen

        ship_types = [

                        ("2er Schiff", ships.two_ship),
                        ("3er Schiff", ships.three_ship),
                        ("4er Schiff", ships.four_ship),
                        ("Z Schiff", ships.z_ship),
                        ("T Schiff", ships.t_ship)

                                                                ]

        # Leere Schiffsliste erstellen
        self.ships = []

        # Gewünschte Anzahl an Schiffen erzeugen
        for i in range(number_of_ships):

                # "%" (Modulo) sorgt dafür, dass nach dem letzten Schiff wieder beim ersten begonnen wird
                name, shape = ship_types[i % len(ship_types)]

                # Neues Schiff erzeugen und zur Liste hinzufügen
                self.ships.append(ships.Ship(f"{name} {i + 1}",shape))

#----------------------------------------------------------------#