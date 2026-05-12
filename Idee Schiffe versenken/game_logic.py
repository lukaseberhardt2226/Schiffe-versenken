import random
from ships import ShipDefinitions

class SeaBattleLogic:
    def __init__(self):
        # Das Spielfeld ist 10x10 groß.
        # 0 = Wasser, 1 = Schiff, 2 = Treffer, 3 = Fehlschuss, 4 = Mine, 5 = Explodierte Mine
        self.player_board = [[0 for _ in range(10)] for _ in range(10)]
        self.ai_board = [[0 for _ in range(10)] for _ in range(10)]
        
        # Wörterbücher, um zu speichern, welches Schiff an welchen Koordinaten liegt
        self.player_ships = {} 
        self.ai_ships = {}
        
        # Energie-Startwerte
        self.energy_player = 2
        self.energy_ai = 2
        
        # Das Gedächtnis der KI: Hier speichert sie getroffene, aber nicht versenkte Felder
        self.ai_target_stack = [] 
        
        # Liste der Schiffe, die noch platziert werden müssen
        self.ships_to_place = list(ShipDefinitions.TYPES.keys())
        
        # Die KI platziert ihre Schiffe direkt beim Start automatisch
        self._place_ai_ships_randomly()

    def _place_ai_ships_randomly(self):
        """Platziert alle KI-Schiffe an zufälligen Positionen."""
        for s_name in ShipDefinitions.TYPES:
            placed = False
            while not placed:
                rx = random.randint(0, 9)
                ry = random.randint(0, 9)
                rot = random.choice(['H', 'V'])
                # Versuchen zu platzieren, wenn es nicht klappt (wegen Rand/anderem Schiff), neue Zahlen
                if self.place_ship(self.ai_board, rx, ry, s_name, rot, is_player=False):
                    placed = True

    def place_ship(self, board, x, y, ship_name, rotation, is_player=True):
        """Prüft, ob ein Schiff passt, und setzt es dann auf das Feld."""
        shape = ShipDefinitions.TYPES[ship_name]
        coords = []
        
        # 1. Schritt: Alle Zielkoordinaten berechnen
        for dx, dy in shape:
            if rotation == 'H':
                nx, ny = x + dx, y + dy
            else:
                nx, ny = x + dy, y + dx # Koordinaten tauschen für vertikale Drehung
            
            # Prüfen: Ist das Feld noch auf dem 10x10 Gitter?
            if not (0 <= nx < 10 and 0 <= ny < 10):
                return False
            # Prüfen: Ist das Feld bereits durch ein anderes Schiff belegt?
            if board[ny][nx] != 0:
                return False
            
            coords.append((nx, ny))
        
        # 2. Schritt: Wenn alles passt, Schiff einzeichnen
        for nx, ny in coords:
            board[ny][nx] = 1 # 1 bedeutet "hier ist ein Schiffsteil"
            
        # In der Liste speichern, damit wir später wissen, wann ein Schiff versenkt ist
        target_dict = self.player_ships if is_player else self.ai_ships
        target_dict[ship_name] = coords
        return True

    def check_shot(self, x, y, target_board, target_ships):
        """Prüft, was passiert, wenn auf ein Feld (x,y) geschossen wird."""
        # Ist der Schuss außerhalb des Feldes?
        if not (0 <= x < 10 and 0 <= y < 10):
            return "OUT", None
            
        current_value = target_board[y][x]
        
        # Wurde hier schon einmal hingeschossen? (Status 2, 3 oder 5)
        if current_value in [2, 3, 5]:
            return "ALREADY", None
        
        # Fall 1: Treffer auf ein Schiff (1)
        if current_value == 1:
            target_board[y][x] = 2 # Markierung für Treffer
            # Prüfen, ob durch diesen Treffer das ganze Schiff versenkt wurde
            for name, coords in target_ships.items():
                if (x, y) in coords:
                    # Wenn alle Teile des Schiffs den Status 2 haben, ist es weg
                    if all(target_board[cy][cx] == 2 for cx, cy in coords):
                        return "SUNK", name
            return "HIT", None
            
        # Fall 2: Treffer auf eine Mine (4)
        elif current_value == 4:
            target_board[y][x] = 5 # Markierung für explodierte Mine
            return "MINE", None
            
        # Fall 3: Schuss ins Wasser (0)
        else:
            target_board[y][x] = 3 # Markierung für Fehlschuss
            return "MISS", None

    def use_scan(self, x, y):
        """Scannt einen 3x3 Bereich um das Ziel herum."""
        if self.energy_player < ShipDefinitions.COSTS["SCAN"]:
            return None
            
        self.energy_player -= ShipDefinitions.COSTS["SCAN"]
        count = 0
        # Gehe von -1 bis +1 um die Zielkoordinate herum
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 10 and 0 <= ny < 10:
                    if self.ai_board[ny][nx] == 1: # Wenn da ein Schiffsteil ist
                        count += 1
        return count

    def ai_decide_action(self):
        """Die Logik der KI: Was macht der Gegner in seinem Zug?"""
        
        # 1. Priorität: Hat die KI viel Energie? Dann Luftschlag!
        if self.energy_ai >= ShipDefinitions.COSTS["AIRSTRIKE"]:
            self.energy_ai -= ShipDefinitions.COSTS["AIRSTRIKE"]
            random_line = random.randint(0, 9)
            random_ori = random.choice(['H', 'V'])
            return "AIRSTRIKE", self._mass_shot(random_line, random_ori, "AIR")

        # 2. Priorität: Verfolgt die KI gerade ein getroffenes Schiff?
        while self.ai_target_stack:
            tx, ty = self.ai_target_stack[0] # Letztes getroffenes Feld
            # Probiere alle Nachbarfelder (Oben, Unten, Rechts, Links)
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = tx + dx, ty + dy
                # Schieße nur, wenn das Feld auf dem Brett ist und noch nicht beschossen wurde
                if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[ny][nx] in [0, 1, 4]:
                    res, sunk = self.check_shot(nx, ny, self.player_board, self.player_ships)
                    self._update_ai_memory(nx, ny, res)
                    return "NORMAL", [(nx, ny, res, sunk)]
            # Wenn keine Nachbarn mehr sinnvoll sind, lösche das Feld aus dem Jagd-Stapel
            self.ai_target_stack.pop(0)
        
        # 3. Priorität: Einfacher Zufallsschuss (Suche nach Schiffen)
        while True:
            rx, ry = random.randint(0, 9), random.randint(0, 9)
            if self.player_board[ry][rx] in [0, 1, 4]:
                res, sunk = self.check_shot(rx, ry, self.player_board, self.player_ships)
                self._update_ai_memory(rx, ry, res)
                return "NORMAL", [(rx, ry, res, sunk)]

    def _update_ai_memory(self, x, y, res):
        """Hilfsfunktion: Die KI merkt sich Treffer für den Jagd-Modus."""
        if res == "HIT":
            self.ai_target_stack.insert(0, (x, y)) # Treffer oben auf den Stapel
        elif res == "SUNK":
            self.ai_target_stack = [] # Wenn versenkt, Jagd beenden und neu suchen

    def _mass_shot(self, x, y, mode):
        """Führt Flächenangriffe aus (für Bombe oder Luftschlag)."""
        results = []
        # Koordinaten für Luftschlag berechnen
        for i in range(10):
            nx, ny = (i, x) if y == 'H' else (x, i)
            res, sunk = self.check_shot(nx, ny, self.player_board, self.player_ships)
            if res != "ALREADY":
                results.append((nx, ny, res, sunk))
                self._update_ai_memory(nx, ny, res)
        return results