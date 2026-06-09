import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
import random

from main import BattleShip
import ships

# FARB PALETTE FÜR DAS SPIELFELD
class Colors:

    TEXT = "#172148"      # textfarbe

    BG = "lightblue"        # hintergrund des canvas
    GRID = "white"          # rahmen der einzelnen felder
    
    WATER = "blue"          # leeres wasser
    MISS = "darkblue"       # fehlschuss ins wasser
    SHIP = "gray"           # eigenes platziertes schiff
    
    HIT = "red"             # getroffenes schiffsteil
    SUNK = "purple"         # komplett versenktes schiff

class BattleShipGUI:
    
    # DAS GRUNDGERÜST UND DIE LOGIK
    def __init__(self, master):
        self.main_window = master
        
        # setzt text in oberer fensterleiste
        self.main_window.title("Schiffe versenken")
        
        # INITIALISIERUNG DER SPIELLOGIK MODELL
        # erstellt instanz der hauptklasse
        self.game = BattleShip()
        
        # spielfeldgröße wird in gui übertragen
        self.fieldsize = self.game.fieldsize
        
        # pixelgröße für jedes quadrat im canvas
        self.cell_size = 40 
        # steuert in welcher phase sich das spiel befindet
        self.battle_phase = False 
        
        # überschreibt listen mit leeren o für saubere platzierung
        self.game.player.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        self.game.computer.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        
        # index zählt welches schiff spieler platziert 0 ist erstes schiff
        self.current_ship_index = 0
        
        # referenz auf schiffsliste des spielers
        self.player_ships = self.game.player.ships
        
        # setzt gegnerische schiffe zufällig im hintergrund
        self.game.computer_place_ships()
        
        # listen speichern canvas rechteck ids um farben zu ändern
        self.player_rects = []
        self.computer_rects = []
        
        # aufruf der methode für visuelle steuerelemente
        self.create_widgets()
        
        # ersten hinweistext generieren und anzeigen
        self.update_status_text()


    # OBERFLÄCHEN AUFBAU WIDGETS UND LAYOUT
    def create_widgets(self):
        # erstellt alle visuellen komponenten

        # UI STYLING
        style = ttk.Style()
        # text über spielfeld
        style.configure("TLabelframe.Label", 
                        font=("Arial", 15),      # schriftart, größe, einstellung
                        foreground=Colors.TEXT)
        # überschrift
        style.configure("TLabel",
                        font=("Arial", 18, "bold"),
                        foreground=Colors.TEXT)

        # STATUS LABEL
        # ttk label erzeugt textfeld
        # schriftart schriftgröße fettdruck
        self.status_label = ttk.Label(self.main_window, text="")
        self.status_label.pack(pady=10)
        
        # rotations button
        self.rotate_btn = ttk.Button(self.main_window,
                                     text="Schiff drehen (R)", 
                                     command=self.rotate_current_ship)
        self.rotate_btn.pack(pady=5)
        # bindet die taste 'r' an die methode, die auch der button nutzt
        self.main_window.bind("r", lambda event: self.rotate_current_ship())


        # container frame
        fields_frame = ttk.Frame(self.main_window)
        fields_frame.pack(padx=15, pady=15) 
        
        # spieler spielfeld links
        player_frame = ttk.LabelFrame(fields_frame, text="Dein Spielfeld")
        player_frame.pack(side=tk.LEFT, padx=15)
        
        # canvas für das spielerfeld erstellen
        canvas_width = self.fieldsize * self.cell_size
        self.player_canvas = tk.Canvas(player_frame, width=canvas_width, height=canvas_width, bg=Colors.BG)
        self.player_canvas.pack(padx=10, pady=10)
        
        # linksklick auf das canvas löst methode aus
        self.player_canvas.bind("<Button-1>", self.player_field_click)
        
        # äußere schleife läuft durch zeilen des spielfelds
        for reihe in range(self.fieldsize):
            row_rects = [] 
            # innere schleife läuft durch spalten der zeile
            for spalte in range(self.fieldsize):
                # berechnet pixelkoordinaten für das rechteck
                x1 = spalte * self.cell_size
                y1 = reihe * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # zeichnet rechteck für leeres wasser und speichert id
                rect_id = self.player_canvas.create_rectangle(x1, y1, x2, y2, fill=Colors.WATER, outline=Colors.GRID)
                row_rects.append(rect_id)
                
            # fertige zeile in gesamtliste eintragen
            self.player_rects.append(row_rects)
            
        # computer spielfeld rechts
        self.computer_frame = ttk.LabelFrame(fields_frame, text="Computer Spielfeld (Gesperrt)")
        self.computer_frame.pack(side=tk.RIGHT, padx=15)
        
        # canvas für das computerfeld erstellen
        self.computer_canvas = tk.Canvas(self.computer_frame, width=canvas_width, height=canvas_width, bg=Colors.BG)
        self.computer_canvas.pack(padx=10, pady=10)
        
        # linksklick auf computer canvas binden
        self.computer_canvas.bind("<Button-1>", self.computer_field_click)
        
        # erstellt rechteck matrix für gegner
        for reihe in range(self.fieldsize):
            row_rects = []
            for spalte in range(self.fieldsize):
                x1 = spalte * self.cell_size
                y1 = reihe * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # gegnerisches wasser zeichnen
                rect_id = self.computer_canvas.create_rectangle(x1, y1, x2, y2, fill=Colors.WATER, outline=Colors.GRID)
                row_rects.append(rect_id)
            self.computer_rects.append(row_rects)


    # BEDIENUNG UND STATUS ANZEIGEN
    def update_status_text(self):
        # aktualisiert anweisungen im label
        if self.current_ship_index < len(self.player_ships):
            aktuelles_schiff = self.player_ships[self.current_ship_index]
            self.status_label.config(text=f"Bitte platziere {aktuelles_schiff.name}")
        else:
            self.start_battle_phase()

    def rotate_current_ship(self):
        # aufruf wenn schiff drehen geklickt wird
        if self.current_ship_index < len(self.player_ships):
            aktuelles_schiff = self.player_ships[self.current_ship_index]
            aktuelles_schiff.rotate()
            messagebox.showinfo("Drehung", f"{aktuelles_schiff.name} wurde gedreht!")


    # PHASE 1 LOGIK FÜR DAS PLATZIEREN DER SCHIFFE
    def player_field_click(self, event):
        # event handler bei klick auf eigenes feld
        # bricht ab wenn alle schiffe gesetzt sind oder kampf läuft
        if self.current_ship_index >= len(self.player_ships) or self.battle_phase:
            return

        # rechnet klick koordinaten in raster spalte und reihe um
        spalte = event.x // self.cell_size
        reihe = event.y // self.cell_size

        # verhindert klicks außerhalb des rasters
        if reihe >= self.fieldsize or spalte >= self.fieldsize:
            return

        # sucht aktuelles schiff objekt
        aktuelles_schiff = self.player_ships[self.current_ship_index]
        
        # speichert startkoordinaten im schiff objekt
        aktuelles_schiff.horizontal_line = reihe
        aktuelles_schiff.vertical_line = spalte

        # nutzt kollisionsprüfung
        ist_kollision = self.game.playingfield.check_collision(aktuelles_schiff, self.game.player.field)

        if ist_kollision == True:
            messagebox.showwarning("Kollision", "Ungültige Position! Schiff ragt heraus oder blockiert.")
            return 

        # trägt schiff ins backend spielfeld ein
        self.game.playingfield.ships_place(aktuelles_schiff, self.game.player.field)
        
        # macht schiff auf canvas sichtbar
        schiff_positionen = aktuelles_schiff.get_positions()
        for pos in schiff_positionen:
            r_pos = pos[0]
            s_pos = pos[1]
            # ändert farbe des platzierten schiffs
            self.player_canvas.itemconfig(self.player_rects[r_pos][s_pos], fill=Colors.SHIP)

        # erhöht index für nächstes schiff
        self.current_ship_index += 1
        self.update_status_text()


    # PHASE 2 LOGIK FÜR DIE KAMPFPHASE DAS DUELL
    def start_battle_phase(self):
        # schaltet ui in kampfmodus um
        self.battle_phase = True
        self.status_label.config(text="FEUER FREI! Klicke auf das gegnerische Feld.")
        
        # entfernt rotations widget aus anzeige
        self.rotate_btn.pack_forget()
        
        # aktualisiert titel des gegnerischen rahmens
        self.computer_frame.config(text="Computer Spielfeld")

    def computer_field_click(self, event):
        # verarbeitet klicks auf das computerfeld
        # blockiert wenn nicht in kampfphase
        if not self.battle_phase:
            return
            
        spalte = event.x // self.cell_size
        reihe = event.y // self.cell_size
        
        if reihe >= self.fieldsize or spalte >= self.fieldsize:
            return
            
        # ignoriert klick wenn feld schon beschossen wurde
        if self.game.computer.field[reihe][spalte] in ["X", "~"]:
            return
            
        self.player_shoot(reihe, spalte)

    def player_shoot(self, reihe, spalte):
        schuss = [reihe, spalte]
        
        # speichert zustand der schiffe vor dem schuss um sinken zu prüfen
        schiffe_vorher = list(self.game.computer.ships)
        
        # prüft ob schiff getroffen wurde
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.computer.ships)

        if wurde_getroffen == True:
            self.game.computer.field[reihe][spalte] = "X"
            # färbt getroffenes feld entsprechend ein
            self.computer_canvas.itemconfig(self.computer_rects[reihe][spalte], fill=Colors.HIT)
            
            # prüft ob ein schiff komplett versenkt wurde
            if len(self.game.computer.ships) < len(schiffe_vorher):
                # sucht das schiff das gerade versenkt wurde
                versenktes_schiff = [s for s in schiffe_vorher if s not in self.game.computer.ships][0]
                # färbt alle positionen des versenkten schiffs um
                for pos in versenktes_schiff.get_positions():
                    self.computer_canvas.itemconfig(self.computer_rects[pos[0]][pos[1]], fill=Colors.SUNK)
        else:
            self.game.computer.field[reihe][spalte] = "~"
            # markiert fehlschuss
            self.computer_canvas.itemconfig(self.computer_rects[reihe][spalte], fill=Colors.MISS)

        # prüft siegbedingung für spieler
        if len(self.game.computer.ships) == 0:
            messagebox.showinfo("Sieg", "Herzlichen Glückwunsch! Du hast gewonnen!")
            self.main_window.quit() 
            return

        # blockiert klicks des spielers während computer überlegt
        self.battle_phase = False 
        # verzögert gegenzug des computers
        self.main_window.after(500, self.computer_shoot)

    def computer_shoot(self):
        # computer ki schießt zufällig auf spielerfeld
        while True:
            reihe = random.randint(0, self.fieldsize - 1)
            spalte = random.randint(0, self.fieldsize - 1)
            if self.game.player.field[reihe][spalte] not in ["X", "~"]:
                break 

        schuss = [reihe, spalte]
        
        # zustand vorher speichern für sinken prüfung auf spielerseite
        schiffe_vorher = list(self.game.player.ships)
        
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.player.ships)

        if wurde_getroffen == True:
            self.game.player.field[reihe][spalte] = "X"
            self.player_canvas.itemconfig(self.player_rects[reihe][spalte], fill=Colors.HIT)
            self.status_label.config(text="Der Computer hat dein Schiff getroffen!")
            
            # färbt komplett zerstörte spielerschiffe um
            if len(self.game.player.ships) < len(schiffe_vorher):
                versenktes_schiff = [s for s in schiffe_vorher if s not in self.game.player.ships][0]
                for pos in versenktes_schiff.get_positions():
                    self.player_canvas.itemconfig(self.player_rects[pos[0]][pos[1]], fill=Colors.SUNK)
        else:
            self.game.player.field[reihe][spalte] = "~"
            self.player_canvas.itemconfig(self.player_rects[reihe][spalte], fill=Colors.MISS)
            self.status_label.config(text="Wasser! Du bist wieder an der Reihe.")

        # prüft siegbedingung für computer
        if len(self.game.player.ships) == 0:
            messagebox.showerror("Spiel vorbei", "Der Computer hat deine gesamte Flotte versenkt!")
            self.main_window.quit() 
        else:
            # schaltet eingaben für spieler wieder frei
            self.battle_phase = True


# RAHMENPROGRAMM ZUM ANWENDUNGSSTART
if __name__ == "__main__":
    game = tk.Tk()
    
    # fensterkonfiguration für das neue layout
    game.geometry()      
    
    app = BattleShipGUI(game)
    game.mainloop()