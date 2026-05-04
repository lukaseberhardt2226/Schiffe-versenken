import tkinter as tk

# Farbpalette
COLOR_WATER = "#2853ff"
COLOR_SHIP = "#2D2D2F"
COLOR_HIT = "#e74c3c"
COLOR_SUNK = "#8e44ad"
COLOR_MISS = "#ecf0f1"
COLOR_HOVER = "#f1c40f"

class BoardUI(tk.LabelFrame):
    def __init__(self, master, title, callback=None, hover_callback=None, leave_callback=None):
        super().__init__(master, text=title, bg="#73abe3", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        self.buttons = [[None for _ in range(10)] for _ in range(10)]
        
        for y in range(10):
            for x in range(10):
                btn = tk.Button(self, width=3, height=1, bg=COLOR_WATER, relief="flat")
                btn.grid(row=y, column=x, padx=1, pady=1)
                
                if callback:
                    btn.config(command=lambda x=x, y=y: callback(x, y))
                if hover_callback:
                    btn.bind("<Enter>", lambda e, x=x, y=y: hover_callback(x, y))
                if leave_callback:
                    btn.bind("<Leave>", lambda e: leave_callback())
                self.buttons[y][x] = btn

    def update_cell(self, x, y, status):
        # Mappt den Logik-Status auf Farben
        colors = {0: COLOR_WATER, 1: COLOR_SHIP, 2: COLOR_HIT, 3: COLOR_MISS, "SUNK": COLOR_SUNK}
        self.buttons[y][x].config(bg=colors.get(status, COLOR_WATER))