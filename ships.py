class ShipDefinitions:
    """
    Diese Klasse speichert alle festen Werte für die Schiffe und Fähigkeiten.
    So muss man Werte nur an einer Stelle ändern.
    """
    
    # Hier definieren wir die Formen der Schiffe.
    # (0,0) ist der Startpunkt, (1,0) ist ein Feld daneben usw.
    TYPES = {
        "2er": [(0,0), (1,0)],
        "3er": [(0,0), (1,0), (2,0)],
        "4er": [(0,0), (1,0), (2,0), (3,0)],
        "Z-Schiff": [(0,0), (1,0), (1,1), (2,1)], # Eine Z-Form
        "T-Schiff": [(0,0), (1,0), (2,0), (1,1), (1,2), (1,3)] # Eine T-Form
    }

    # Die Kosten für die Spezialfähigkeiten (Energiepunkte)
    COSTS = {
        "SCAN": 3,
        "MINE": 2,
        "BOMB": 5,
        "AIRSTRIKE": 9
    }