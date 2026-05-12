class Ship:

    def __init__(self, name, shape):

        # Name des Schiffs
        self.name = name

        # Schiffform speichern
        self.shape = shape

        # Originale Schiffform speichern
        self.original_shape = [line [:] for line in shape]

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

    # Schiffe rotieren (Dreht die Schiff-Form um 90 Grad nach rechts)
    def rotate(self):

        # Neue leere Form erstellen
        rotated_shape = []

        # Durch alle Spalten gehen
        for vertical_line in range(len(self.shape[0])):

            # Neue Zeile erstellen
            new_line = []

            # Von unten nach oben durch die Zeilen gehen
            for horizontal_line in range(

                len(self.shape) - 1,-1,-1):

                # Werte übernehmen
                new_line.append(self.shape[horizontal_line][vertical_line])

            # Neue Zeile speichern
            rotated_shape.append(new_line)

        # Alte Form ersetzen
        self.shape = rotated_shape


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

