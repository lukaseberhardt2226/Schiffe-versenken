# Schiffe versenken main 
import tkinter as tk
from battleship import BattleShip
from gui import BattleShipGUI


if __name__ == "__main__":

    # Einstellungen
    fieldsize = 10          # Standart 10
    number_of_ships = 5     # Standart 5

    # Spielobjekt erstellen
    game = BattleShip(fieldsize, number_of_ships)

    # GUI starten
    root = tk.Tk()
    app = BattleShipGUI(root, game)
    root.mainloop()