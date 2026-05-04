import random

class SeaBattleLogic:
    def __init__(self):
        self.size = 10
        # 0=Wasser, 1=Schiff, 2=Treffer, 3=Fehlschuss
        self.player_board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.ai_board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        self.player_ships = {} 
        self.ai_ships = {}
        
        self.ship_types = {
            "2er": [(0,0), (1,0)],
            "3er": [(0,0), (1,0), (2,0)],
            "4er": [(0,0), (1,0), (2,0), (3,0)],
            "Z-Schiff": [(0,0), (1,0), (1,1), (2,1)],
            "T-Schiff": [(0,0), (1,0), (2,0), (1,1), (1,2), (1,3)]
        }
        self.ships_to_place = list(self.ship_types.keys())
        self.place_ai_ships()

    def can_place(self, board, x, y, shape, rotation):
        for dx, dy in shape:
            nx, ny = (x + dx, y + dy) if rotation == 'H' else (x + dy, y + dx)
            if not (0 <= nx < 10 and 0 <= ny < 10) or board[ny][nx] != 0:
                return False
        return True

    def place_ship(self, board, x, y, ship_name, rotation, is_player=True):
        shape = self.ship_types[ship_name]
        if self.can_place(board, x, y, shape, rotation):
            coords = []
            for dx, dy in shape:
                nx, ny = (x + dx, y + dy) if rotation == 'H' else (x + dy, y + dx)
                board[ny][nx] = 1
                coords.append((nx, ny))
            
            target_dict = self.player_ships if is_player else self.ai_ships
            target_dict[ship_name] = coords
            return True
        return False

    def place_ai_ships(self):
        for s_name in self.ship_types:
            placed = False
            while not placed:
                rx, ry = random.randint(0,9), random.randint(0,9)
                rot = random.choice(['H', 'V'])
                if self.place_ship(self.ai_board, rx, ry, s_name, rot, is_player=False):
                    placed = True

    def check_shot(self, x, y, target_board, target_ships):
        if target_board[y][x] == 1:
            target_board[y][x] = 2
            for name, coords in target_ships.items():
                if (x, y) in coords:
                    if all(target_board[cy][cx] == 2 for cx, cy in coords):
                        return "SUNK", name
            return "HIT", None
        elif target_board[y][x] == 0:
            target_board[y][x] = 3
            return "MISS", None
        return "ALREADY", None

    def ai_turn(self):
        while True:
            x, y = random.randint(0,9), random.randint(0,9)
            val = self.player_board[y][x]
            if val < 2:
                res, sunk_name = self.check_shot(x, y, self.player_board, self.player_ships)
                return x, y, res, sunk_name