class Ship:

    def __init__(self, name, shape):

        # Name des Schiffs
        self.name = name

        # Schiffform speichern
        self.shape = shape

        # Trefferzähler
        self.hits = 0

        # Startposition
        self.horizontal_line = 0
        self.vertical_line = 0
    
    def get_positions(self):

        positions = []

         # Durch alle Zeilen der Form gehen
        for horizontal_line in range(len(self.shape)):

            # Durch alle Spalten der Form gehen
            for vertical_line in range(len(self.shape[horizontal_line])):

                # Prüfen ob dort ein Schiffsteil ist
                if self.shape[horizontal_line][vertical_line] == 1:

                     # Echte Spielfeldposition berechnen
                    real_horizontal_line = (self.horizontal_line + horizontal_line)
                    real_vertical_line = (self.vertical_line + vertical_line)

                    # Position speichern
                    positions.append([real_horizontal_line, real_vertical_line])

        return positions



two_ship = [
             [1,1]
                    ]


three_ship = [
                [1,1,1]
                        ]

four_ship = [
             [1,1,1,1]
                        ]

z_ship = [
            [1,1,0],
            [0,1,1]

                        ]
t_ship = [ 
            [1,1,1],
            [0,1,0],
            [0,1,0]

                        ]

