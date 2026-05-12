import tkinter as tk

class Colors:
    """Eine Sammlung aller Farben für ein einheitliches Design."""
    BG = "#0b0d17"        # Sehr dunkles Blau für den Hintergrund
    PANEL = "#1c2230"     # Farbe für die Schaltflächen-Leiste
    WATER = "#1a2a6c"     # Dunkles Blau für das Meer
    SHIP = "#34495e"      # Grau-Blau für eigene Schiffe
    HIT = "#ff4b2b"       # Signal-Rot für Treffer
    SUNK = "#8e44ad"      # Lila für komplett versenkte Schiffe
    MISS = "#576574"      # Grau für Schüsse ins Wasser
    HOVER = "#00d2ff"     # Hellblau für die Maus-Vorschau
    MINE = "#2ecc71"      # Grün für die Minen
    TEXT = "#ecf0f1"      # Fast Weiß für Schrift
    ENERGY = "#f1c40f"    # Gelb für die Energieanzeige

class BoardUI(tk.LabelFrame):
    """
    Diese Klasse erstellt ein 10x10 Gitter aus Buttons.
    Sie erbt von tk.LabelFrame (ein Rahmen mit Beschriftung).
    """
    def __init__(self, master, title, callback=None, hover_cb=None, leave_cb=None):
        # Den Rahmen erstellen
        super().__init__(master, text=title, bg=Colors.BG, fg=Colors.TEXT, 
                         font=("Courier", 12, "bold"), bd=2, relief="flat")
        
        # 2D-Liste, um die Button-Objekte zu speichern
        self.buttons = [[None for _ in range(10)] for _ in range(10)]
        
        # Erstelle 100 Buttons in einer Schleife
        for y in range(10):
            for x in range(10):
                btn = tk.Button(self, width=3, height=1, bg=Colors.WATER, 
                               relief="flat", bd=0, highlightthickness=1, 
                               highlightbackground="#2c3e50")
                btn.grid(row=y, column=x, padx=1, pady=1)
                
                # Wenn man klickt:
                if callback: 
                    btn.config(command=lambda x=x, y=y: callback(x, y))
                
                # Wenn man mit der Maus drüberfährt (für Vorschau):
                if hover_cb: 
                    btn.bind("<Enter>", lambda e, x=x, y=y: hover_cb(x, y))
                
                # Wenn die Maus das Feld verlässt:
                if leave_cb: 
                    btn.bind("<Leave>", lambda e: leave_cb())
                
                self.buttons[y][x] = btn

    def update_cell(self, x, y, status, text=""):
        """Ändert die Farbe und den Text eines Feldes basierend auf dem Status."""
        # Übersetzung von Zahlen-Status in Farben
        mapping = {
            0: Colors.WATER, 
            1: Colors.SHIP, 
            2: Colors.HIT, 
            3: Colors.MISS, 
            4: Colors.MINE, 
            5: "#d35400",    # Orange für explodierte Mine
            "SUNK": Colors.SUNK
        }
        
        new_color = mapping.get(status, Colors.WATER)
        self.buttons[y][x].config(bg=new_color, text=text, fg="white")