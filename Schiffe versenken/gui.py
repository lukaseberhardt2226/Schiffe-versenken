import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
import random

from battleship import BattleShip
import ships

# FARB PALETTE FÜR DAS SPIELFELD
class Colors:

    TEXT = "navyblue"      # textfarbe

    BG = "lightblue"        # hintergrund des canvas
    GRID = "white"          # rahmen der einzelnen felder
    
    WATER = "blue"          # leeres wasser
    MISS = "darkblue"       # fehlschuss ins wasser
    SHIP = "gray"           # eigenes platziertes schiff
    
    HIT = "red"             # getroffenes schiffsteil
    SUNK = "purple"         # komplett versenktes schiff

    PREVIEW = "lightgreen"      # vorschau für gültige platzierung
    PREVIEW_ERROR = "salmon"    # vorschau für ungültige platzierung


class BattleShipGUI:
    
    # DAS GRUNDGERÜST UND DIE LOGIK
    def __init__(self, master):
        self.main_window = master
        
        # setzt text in oberer fensterleiste
        self.main_window.title("Schiffe versenken")
        
        # INITIALISIERUNG DER SPIELLOGIK MODELL
        self.game = BattleShip()
        self.fieldsize = self.game.fieldsize
        self.cell_size = 40
        self.battle_phase = False 
        
        # überschreibt listen mit leeren O für saubere platzierung
        self.game.player.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        self.game.computer.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        
        # index zählt, welches schiff der spieler gerade platziert
        self.current_ship_index = 0
        self.player_ships = self.game.player.ships
        
        # setzt gegnerische schiffe zufällig im hintergrund
        self.game.computer_place_ships()
        
        # listen speichern canvas rechteck ids, um farben zu ändern
        self.player_rects = []
        self.computer_rects = []

        # SPEICHER FÜR DIE VORSCHAU-LOGIK
        self.preview_positions = [] # Speichert die aktuell eingefärbten Vorschau-Felder
        self.last_hover_reihe = -1  # Speichert die letzte Mausposition
        self.last_hover_spalte = -1
        
        self.create_widgets()
        self.update_status_text()


    # OBERFLÄCHEN AUFBAU WIDGETS UND LAYOUT
    def create_widgets(self):
        # UI STYLING
        style = ttk.Style()
        style.configure("TLabelframe.Label", font=("Arial", 15), foreground=Colors.TEXT)
        style.configure("TLabel", font=("Arial", 18, "bold"), foreground=Colors.TEXT)
        style.configure("Rotate.TButton", font=("Arial", 11, "bold"))

        # STATUS LABEL
        self.status_label = ttk.Label(self.main_window, text="")
        self.status_label.pack(pady=10)
        
        # rotations button
        self.rotate_btn = ttk.Button(self.main_window, 
                                     text="Schiff drehen (R)", 
                                     command=self.rotate_current_ship,
                                     style="Rotate.TButton",   # Verbindet den Button mit dem Design oben
                                     width=20)                 # Mindestbreite (in Buchstaben/Zeichen)
        self.rotate_btn.pack(pady=0, ipadx=0, ipady=5)
        self.main_window.bind("r", lambda event: self.rotate_current_ship())

        # container frame
        fields_frame = ttk.Frame(self.main_window)
        fields_frame.pack(padx=15, pady=15) 
        
        # spieler spielfeld links
        player_frame = ttk.LabelFrame(fields_frame, text="Dein Spielfeld")
        player_frame.pack(side=tk.LEFT, padx=15)
        
        # canvas für das spielerfeld
        canvas_width = self.fieldsize * self.cell_size
        self.player_canvas = tk.Canvas(player_frame, width=canvas_width, height=canvas_width, bg=Colors.BG)
        self.player_canvas.pack(padx=10, pady=10)
        
        # EVENT BINDINGS (klicken und mausbewegung für vorschau)
        self.player_canvas.bind("<Button-1>", self.player_field_click)
        self.player_canvas.bind("<Motion>", self.player_field_hover)    # Maus bewegt sich
        self.player_canvas.bind("<Leave>", self.clear_preview)          # Maus verlässt Feld
        
        # zeichnet das raster für den spieler
        for reihe in range(self.fieldsize):
            row_rects = [] 
            for spalte in range(self.fieldsize):
                x1 = spalte * self.cell_size
                y1 = reihe * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect_id = self.player_canvas.create_rectangle(x1, y1, x2, y2, fill=Colors.WATER, outline=Colors.GRID)
                row_rects.append(rect_id)
            self.player_rects.append(row_rects)
            
        # computer spielfeld rechts
        self.computer_frame = ttk.LabelFrame(fields_frame, text="Computer Spielfeld (Gesperrt)")
        self.computer_frame.pack(side=tk.RIGHT, padx=15)
        
        self.computer_canvas = tk.Canvas(self.computer_frame, width=canvas_width, height=canvas_width, bg=Colors.BG)
        self.computer_canvas.pack(padx=10, pady=10)
        self.computer_canvas.bind("<Button-1>", self.computer_field_click)
        
        # zeichnet das raster für den computer
        for reihe in range(self.fieldsize):
            row_rects = []
            for spalte in range(self.fieldsize):
                x1 = spalte * self.cell_size
                y1 = reihe * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect_id = self.computer_canvas.create_rectangle(x1, y1, x2, y2, fill=Colors.WATER, outline=Colors.GRID)
                row_rects.append(rect_id)
            self.computer_rects.append(row_rects)


    # VORSCHAU LOGIK
    def clear_preview(self, event=None):
        # setzt alle aktuellen vorschau felder wieder auf Wasser zurück
        for r, c in self.preview_positions:
            # nur zurücksetzen wenn da nicht schon ein echtes platziertes Schiff liegt
            if self.game.player.field[r][c] == "O":
                self.player_canvas.itemconfig(self.player_rects[r][c], fill=Colors.WATER)
        self.preview_positions.clear()

    def player_field_hover(self, event):
        # wird ausgelöst wenn die maus über das feld bewegt wird
        if self.current_ship_index >= len(self.player_ships) or self.battle_phase:
            return

        spalte = event.x // self.cell_size
        reihe = event.y // self.cell_size
        
        self.update_preview(reihe, spalte)

    def update_preview(self, reihe, spalte):
        # wenn maus außerhalb des rasters ist vorschau löschen
        if reihe >= self.fieldsize or spalte >= self.fieldsize or reihe < 0 or spalte < 0:
            self.clear_preview()
            self.last_hover_reihe = -1
            self.last_hover_spalte = -1
            return
            
        # alte Vorschau löschen bevor die neue gezeichnet wird
        self.clear_preview()
        
        self.last_hover_reihe = reihe
        self.last_hover_spalte = spalte
        
        # holt das objekt des aktuell zu platzierenden schiffs
        aktuelles_schiff = self.player_ships[self.current_ship_index]
        aktuelles_schiff.horizontal_line = reihe
        aktuelles_schiff.vertical_line = spalte
        
        # kollision prüfen um farbe zu bestimmen
        ist_kollision = self.game.playingfield.check_collision(aktuelles_schiff, self.game.player.field)
        vorschau_farbe = Colors.PREVIEW_ERROR if ist_kollision else Colors.PREVIEW
        
        # neue vorschau zeichnen
        for pos in aktuelles_schiff.get_positions():
            r_pos = pos[0]
            s_pos = pos[1]
            
            # prüfen ob die position im spielfeld liegt
            if 0 <= r_pos < self.fieldsize and 0 <= s_pos < self.fieldsize:
                if self.game.player.field[r_pos][s_pos] == "O":
                    self.player_canvas.itemconfig(self.player_rects[r_pos][s_pos], fill=vorschau_farbe)
                    self.preview_positions.append((r_pos, s_pos))


    # BEDIENUNG UND STATUS ANZEIGEN
    def update_status_text(self):
        # prüft ob der spieler noch schiffe setzen muss
        if self.current_ship_index < len(self.player_ships):
            aktuelles_schiff = self.player_ships[self.current_ship_index]
            self.status_label.config(text=f"Bitte platziere {aktuelles_schiff.name}")
        else:
            # wenn alle gesetzt sind geht es in phase 2
            self.start_battle_phase()

    def rotate_current_ship(self):
        # dreht das schiff nur wenn wir noch im platzierungsmodus sind
        if self.current_ship_index < len(self.player_ships):
            aktuelles_schiff = self.player_ships[self.current_ship_index]
            aktuelles_schiff.rotate()
            
            # aktualisiert die vorschau sofort an der aktuellen mausposition nach dem drehen
            if self.last_hover_reihe != -1:
                self.update_preview(self.last_hover_reihe, self.last_hover_spalte)


    # PHASE 1 LOGIK FÜR DAS PLATZIEREN DER SCHIFFE
    def player_field_click(self, event):
        # bricht ab wenn kampf läuft oder alle schiffe gesetzt sind
        if self.current_ship_index >= len(self.player_ships) or self.battle_phase:
            return

        # rechnet mauskoordinaten in raster koordinaten um
        spalte = event.x // self.cell_size
        reihe = event.y // self.cell_size

        # ignoriert klicks außerhalb des fensters
        if reihe >= self.fieldsize or spalte >= self.fieldsize:
            return

        aktuelles_schiff = self.player_ships[self.current_ship_index]
        aktuelles_schiff.horizontal_line = reihe
        aktuelles_schiff.vertical_line = spalte

        # prüft backend logik ob schiff hier erlaubt ist
        ist_kollision = self.game.playingfield.check_collision(aktuelles_schiff, self.game.player.field)

        if ist_kollision == True:
            # blockiert das setzen wenn es ungültig ist
            return 

        # vor dem eintragen ins backend löschen wir die vorschau farben
        self.clear_preview()

        # trägt schiff ins backend spielfeld ein
        self.game.playingfield.ships_place(aktuelles_schiff, self.game.player.field)
        
        # macht schiff auf canvas als festes Schiff sichtbar
        schiff_positionen = aktuelles_schiff.get_positions()
        for pos in schiff_positionen:
            r_pos = pos[0]
            s_pos = pos[1]
            self.player_canvas.itemconfig(self.player_rects[r_pos][s_pos], fill=Colors.SHIP)

        # rückt zum nächsten schiff in der liste vor
        self.current_ship_index += 1
        self.update_status_text()
        
        # sofort die vorschau für das nächste schiff
        if self.current_ship_index < len(self.player_ships):
            self.update_preview(reihe, spalte)


    # PHASE 2 LOGIK FÜR DIE KAMPFPHASE DAS DUELL
    def start_battle_phase(self):
        # schaltet um auf spielmodus klicks aufs eigene feld sind nun wirkungslos
        self.battle_phase = True
        self.status_label.config(text="FEUER FREI! Klicke auf das gegnerische Feld.")
        
        # blendet den rotations button aus
        self.rotate_btn.pack_forget()
        self.computer_frame.config(text="Computer Spielfeld")
        
        # letzte vorschau reste bereinigen
        self.clear_preview()

    def computer_field_click(self, event):
        # blockiert klicks wenn der spieler gerade nicht am zug ist
        if not self.battle_phase:
            return
            
        spalte = event.x // self.cell_size
        reihe = event.y // self.cell_size
        
        if reihe >= self.fieldsize or spalte >= self.fieldsize:
            return
            
        # blockiert klicks auf felder auf die schon geschossen wurde
        if self.game.computer.field[reihe][spalte] in ["X", "~"]:
            return
            
        # führt den eigentlichen schuss aus
        self.player_shoot(reihe, spalte)



    def player_shoot(self, reihe, spalte):
        # formatiert koordinate für die backend übergabe
        schuss = [reihe, spalte]
        
        # merkt sich alle computer-schiffe VOR dem schuss, um sinken zu prüfen
        schiffe_vorher = list(self.game.computer.ships)
        
        # fragt backend ob schuss ein ziel trifft
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.computer.ships)

        if wurde_getroffen == True:
            # markiert treffer im backend und frontend
            self.game.computer.field[reihe][spalte] = "X"
            self.computer_canvas.itemconfig(self.computer_rects[reihe][spalte], fill=Colors.HIT)
            
            # vergleicht schiffsliste wenn sie kürzer ist, ist ein schiff gesunken
            if len(self.game.computer.ships) < len(schiffe_vorher):
                # identifiziert das gesunkene schiff
                versenktes_schiff = [s for s in schiffe_vorher if s not in self.game.computer.ships][0]
                
                # färbt alle teile des gesunkenen schiffs
                for pos in versenktes_schiff.get_positions():
                    self.computer_canvas.itemconfig(self.computer_rects[pos[0]][pos[1]], fill=Colors.SUNK)
        else:
            # markiert fehlschuss im backend und frontend
            self.game.computer.field[reihe][spalte] = "~"
            self.computer_canvas.itemconfig(self.computer_rects[reihe][spalte], fill=Colors.MISS)

        # prüft siegbedingung für spieler
        if len(self.game.computer.ships) == 0:
            messagebox.showinfo("Sieg", "Herzlichen Glückwunsch! Du hast gewonnen!")
            self.main_window.quit() 
            return

        # spieler muss warten, computer ist an der reihe
        self.battle_phase = False 
        
        # nach x millisekunden verzögerung schießt der computer
        self.main_window.after(300, self.computer_shoot)




    def computer_shoot(self):
        # schleife sucht solange bis ein noch nicht beschossenes feld gefunden wird
        while True:
            reihe = random.randint(0, self.fieldsize - 1)
            spalte = random.randint(0, self.fieldsize - 1)
            if self.game.player.field[reihe][spalte] not in ["X", "~"]:
                break 

        schuss = [reihe, spalte]
        
        # merkt sich spielernschiffe vor dem gegnerischen schuss
        schiffe_vorher = list(self.game.player.ships)
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.player.ships)

        if wurde_getroffen == True:
            # markiert treffer beim spieler
            self.game.player.field[reihe][spalte] = "X"
            self.player_canvas.itemconfig(self.player_rects[reihe][spalte], fill=Colors.HIT)
            self.status_label.config(text="Der Computer hat dein Schiff getroffen!")
            
            # prüft ob ein spieler schiff komplett gesunken ist
            if len(self.game.player.ships) < len(schiffe_vorher):
                versenktes_schiff = [s for s in schiffe_vorher if s not in self.game.player.ships][0]
                for pos in versenktes_schiff.get_positions():
                    self.player_canvas.itemconfig(self.player_rects[pos[0]][pos[1]], fill=Colors.SUNK)
        else:
            # markiert gegnerischen fehlschuss
            self.game.player.field[reihe][spalte] = "~"
            self.player_canvas.itemconfig(self.player_rects[reihe][spalte], fill=Colors.MISS)
            self.status_label.config(text="Wasser! Du bist wieder an der Reihe.")

        # prüft siegbedingung für computer
        if len(self.game.player.ships) == 0:
            messagebox.showerror("Spiel vorbei", "Der Computer hat deine gesamte Flotte versenkt!")
            self.main_window.quit() 
        else:
            # gibt spielfeld für den nächsten klick des spielers frei
            self.battle_phase = True


# RAHMENPROGRAMM ZUM ANWENDUNGSSTART
if __name__ == "__main__":
    game = tk.Tk()
    
    # fensterkonfiguration (lxb)
    game.geometry()      
    
    app = BattleShipGUI(game)
    game.mainloop()