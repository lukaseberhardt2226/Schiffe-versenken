import tkinter as tk
from tkinter import messagebox
from game_logic import SeaBattleLogic
from gui_components import BoardUI, COLOR_SUNK

class GameController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Schiffe versenken - MK Projekt")
        self.root.configure(bg="#73abe3")
        self.logic = SeaBattleLogic()
        self.phase = "PLACING"
        self.rotation = "H"
        
        self.info_label = tk.Label(self.root, text="PLATZIERE DEINE SCHIFFE (R zum Drehen)", 
                                  bg="#73abe3", fg="white", font=("Arial", 14, "bold"))
        self.info_label.pack(pady=10)

        self.frame = tk.Frame(self.root, bg="#73abe3")
        self.frame.pack()

        # Linkes Feld (KI)
        self.ui_ai = BoardUI(self.frame, "GEGNER (KI)", callback=self.handle_shot)
        self.ui_ai.pack(side="left", padx=20)
        
        # Rechtes Feld (Spieler)
        self.ui_player = BoardUI(self.frame, "DEINE BASIS", 
                                 callback=self.handle_placement,
                                 hover_callback=self.show_preview,
                                 leave_callback=self.clear_preview)
        self.ui_player.pack(side="right", padx=20)
        
        # Tastatur-Bindings
        self.root.bind('r', lambda e: self.toggle_rotation())
        self.root.bind('R', lambda e: self.toggle_rotation())
        self.root.mainloop()

    def toggle_rotation(self):
        self.rotation = "V" if self.rotation == "H" else "H"
        self.update_status()

    def update_status(self):
        if self.phase == "PLACING":
            ship = self.logic.ships_to_place[0] if self.logic.ships_to_place else "Fertig"
            self.info_label.config(text=f"Platziere: {ship} ({self.rotation})")

    def show_preview(self, x, y):
        if self.phase != "PLACING" or not self.logic.ships_to_place: return
        shape = self.logic.ship_types[self.logic.ships_to_place[0]]
        for dx, dy in shape:
            nx, ny = (x + dx, y + dy) if self.rotation == 'H' else (x + dy, y + dx)
            if 0 <= nx < 10 and 0 <= ny < 10 and self.logic.player_board[ny][nx] == 0:
                self.ui_player.buttons[ny][nx].config(bg="#f1c40f")

    def clear_preview(self):
        for y in range(10):
            for x in range(10):
                val = self.logic.player_board[y][x]
                self.ui_player.update_cell(x, y, val)

    def handle_placement(self, x, y):
        if self.phase != "PLACING": return
        ship_name = self.logic.ships_to_place[0]
        if self.logic.place_ship(self.logic.player_board, x, y, ship_name, self.rotation):
            self.logic.ships_to_place.pop(0)
            self.clear_preview()
            if not self.logic.ships_to_place:
                self.phase = "BATTLE"
                self.info_label.config(text="GEFECHT BEGINNT!", fg="#f1c40f")
            else:
                self.update_status()

    def handle_shot(self, x, y):
        if self.phase != "BATTLE": return
        res, sunk_name = self.logic.check_shot(x, y, self.logic.ai_board, self.logic.ai_ships)
        
        if res == "SUNK":
            messagebox.showinfo("Versenkt!", f"Du hast das {sunk_name} der KI versenkt!")
            for sx, sy in self.logic.ai_ships[sunk_name]:
                self.ui_ai.update_cell(sx, sy, "SUNK")
            self.check_game_over()
        elif res != "ALREADY":
            self.ui_ai.update_cell(x, y, 2 if res == "HIT" else 3)
            self.ai_turn()

    def ai_turn(self):
        ax, ay, res, sunk_name = self.logic.ai_turn()
        if res == "SUNK":
            for sx, sy in self.logic.player_ships[sunk_name]:
                self.ui_player.update_cell(sx, sy, "SUNK")
        else:
            self.ui_player.update_cell(ax, ay, 2 if res == "HIT" else 3)
        self.check_game_over()

    def check_game_over(self):
        # Prüfen, ob alle KI-Schiffe versenkt sind
        if all(all(c != 1 for c in row) for row in self.logic.ai_board):
            self.end_game("SIEG! Die KI wurde besiegt.")
        # Prüfen, ob alle Spieler-Schiffe versenkt sind
        elif all(all(c != 1 for c in row) for row in self.logic.player_board):
            self.end_game("NIEDERLAGE! Deine Basis wurde zerstört.")

    def end_game(self, msg):
        if messagebox.askyesno("Spielende", f"{msg}\nNochmal spielen?"):
            self.root.destroy()
            GameController()
        else:
            self.root.destroy()

if __name__ == "__main__":
    GameController()