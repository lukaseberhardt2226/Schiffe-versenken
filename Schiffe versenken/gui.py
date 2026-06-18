import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
import random
from battleship import BattleShip

#
# FARBEN
#

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
    CURSOR = "yellow"           # cursor

#
# DIE STEUERUNGS
#

class InputController:
    # initialisierung der steuerung
    def __init__(self, gui_app):
        # referenz auf gui speichern
        self.gui = gui_app
        self.root = gui_app.main_window
        
        # cursor start bei 0,0
        self.cursor_r = 0
        self.cursor_c = 0
        
        # tastatur belegungen
        self._bind_keyboard()

    def _bind_keyboard(self):
        # bewegungstasten binden (reihe, spalte)
        self.root.bind("<Up>", lambda e: self.move(-1, 0))
        self.root.bind("<Down>", lambda e: self.move(1, 0))
        self.root.bind("<Left>", lambda e: self.move(0, -1))
        self.root.bind("<Right>", lambda e: self.move(0, 1))
        
        # aktionstasten binden (return=enter)
        self.root.bind("<Return>", lambda e: self.action())
        self.root.bind("r", lambda e: self.rotate())
        self.root.bind("R", lambda e: self.rotate())

    def move(self, dr, dc):
        # alte cursor grafik entfernen
        self.gui.clear_cursor_visuals(self.cursor_r, self.cursor_c)

        # neue koordinaten berechnen (bleibt im spielfeld)
        self.cursor_r = max(0, min(self.gui.fieldsize - 1, self.cursor_r + dr))
        self.cursor_c = max(0, min(self.gui.fieldsize - 1, self.cursor_c + dc))

        # neue cursor grafik anzeigen
        self.gui.draw_cursor_visuals(self.cursor_r, self.cursor_c)

    def set_cursor(self, r, c):
        # cursor wird zurückgesetzt (start oder phasenwechsel)
        self.gui.clear_cursor_visuals(self.cursor_r, self.cursor_c)
        self.cursor_r = r
        self.cursor_c = c
        self.gui.draw_cursor_visuals(self.cursor_r, self.cursor_c)

    def action(self):
        # schaut ob wir noch in der platzierphase sind falls ja platziert schiff
        if self.gui.current_ship_index < len(self.gui.player_ships):
            self.gui.place_ship_at_cursor(self.cursor_r, self.cursor_c)
        # in kampfphase führt schuss aus
        else:
            self.gui.shoot_at_cursor(self.cursor_r, self.cursor_c)

    def rotate(self):
        # wenn in platzierphase dreht schiff (rotiert und ändert anzeige)
        if self.gui.current_ship_index < len(self.gui.player_ships):
            self.gui.player_ships[self.gui.current_ship_index].rotate()
            self.gui.draw_cursor_visuals(self.cursor_r, self.cursor_c)


#
# DIE GUI-KLASSE
#

class BattleShipGUI:
    def __init__(self, master):
        self.main_window = master
        self.main_window.title("Schiffe versenken")
        
        # spiellogik (übernahme aus battleship.py)
        self.game = BattleShip()
        self.fieldsize = self.game.fieldsize
        self.cell_size = 40 #in pixel
        self.battle_phase = False #beginn in platzierphase
        
        # spielfelder (gitter mit 0 für wasser)
        self.game.player.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        self.game.computer.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        
        # schiff status verwalten
        self.current_ship_index = 0
        self.player_ships = self.game.player.ships
        self.game.computer_place_ships()
        
        # listen für grafiken
        self.player_rects = []
        self.computer_rects = []
        self.preview_positions = [] 
        
        # controller wird in GUI eingebunden
        self.controller = InputController(self)
        
        # widgets aufbauen
        self.create_widgets()
        
        # startwerte
        self.controller.set_cursor(0, 0) # start position
        self.update_status_text() # anweisung titel oben

    def create_widgets(self):
        # design festlegen
        style = ttk.Style()
        style.configure("TLabelframe.Label", font=("Arial", 17), foreground=Colors.TEXT)
        style.configure("TLabel", font=("Arial", 18, "bold"), foreground=Colors.TEXT)
        style.configure("Rotate.TButton", font=("Arial", 11, "bold"))

        # status textfeld
        self.status_label = ttk.Label(self.main_window, text="")
        self.status_label.pack(pady=10)
        
        # rotations button definieren
        self.rotate_btn = ttk.Button(self.main_window, 
                                     text="Schiff drehen R", 
                                     command=self.controller.rotate,
                                     style="Rotate.TButton", 
                                     width=20) 
        self.rotate_btn.pack(pady=0, ipadx=0, ipady=5)
        
        # haupt container für spielfelder
        fields_frame = ttk.Frame(self.main_window)
        fields_frame.pack(padx=15, pady=15) 
        
        # (spielerfeld)
        # spieler feld rahmen (links angeordnet)
        player_frame = ttk.LabelFrame(fields_frame, text="Dein Spielfeld")
        player_frame.pack(side=tk.LEFT, padx=15)
        
        # berechnet spieler spielfeld größe
        canvas_width = self.fieldsize * self.cell_size
        # zeichnet spieler spielfeld
        self.player_canvas = tk.Canvas(player_frame, width=canvas_width, height=canvas_width, bg=Colors.BG)
        self.player_canvas.pack(padx=10, pady=10) # abstand rahmen
        
        # grid für spieler festlegen
        for reihe in range(self.fieldsize):
            row_rects = [] 
            for spalte in range(self.fieldsize):
                # oben links
                x1, y1 = spalte * self.cell_size, reihe * self.cell_size
                # unten rechts
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                # IDs der kästchen werden in canvas rechtecken gespeichert
                rect_id = self.player_canvas.create_rectangle(x1, y1, x2, y2, fill=Colors.WATER, outline=Colors.GRID)
                row_rects.append(rect_id) # IDs kommen in liste für die zeile
            self.player_rects.append(row_rects)
            
        # (gleiches für computer spielfeld)
        self.computer_frame = ttk.LabelFrame(fields_frame, text="Computer Spielfeld (gesperrt)")
        self.computer_frame.pack(side=tk.RIGHT, padx=15)
        
        self.computer_canvas = tk.Canvas(self.computer_frame, width=canvas_width, height=canvas_width, bg=Colors.BG)
        self.computer_canvas.pack(padx=10, pady=10)
        
        for reihe in range(self.fieldsize):
            row_rects = []
            for spalte in range(self.fieldsize):
                x1, y1 = spalte * self.cell_size, reihe * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                rect_id = self.computer_canvas.create_rectangle(x1, y1, x2, y2, fill=Colors.WATER, outline=Colors.GRID)
                row_rects.append(rect_id)
            self.computer_rects.append(row_rects)

    #
    # VISUELLES FEEDBACK CURSOR
    #

    # anzeige cursor
    def clear_cursor_visuals(self, zeile, spalte):
        # wenn platzierphase clear preview
        if self.current_ship_index < len(self.player_ships):
            self.clear_preview()
        # wenn kampfphase verschwindet cursor von platzierphase
        else:
            self.computer_canvas.itemconfig(self.computer_rects[zeile][spalte], outline=Colors.GRID, width=1)

    def draw_cursor_visuals(self, zeile, spalte):
        # wenn platzierphase zeichnet schiff mit jeweiliger farbe ein
        if self.current_ship_index < len(self.player_ships):
            self.update_preview(zeile, spalte)
        # wenn kampfphase cursor auf computer spielfeld
        else:
            self.computer_canvas.itemconfig(self.computer_rects[zeile][spalte], outline=Colors.CURSOR, width=3)

    def clear_preview(self):
        # gui merk sich eingefärbe felder
        for zeile, spalte in self.preview_positions:
            # wenn feld leer wird es zu wasser
            if self.game.player.field[zeile][spalte] == "O":
                # farbe zu wasser
                self.player_canvas.itemconfig(self.player_rects[zeile][spalte], fill=Colors.WATER)
        # liste leeren
        self.preview_positions.clear()


    # update der vorschau
    def update_preview(self, reihe, spalte):
        # vorschau leeren
        self.clear_preview()
        
        # schiffdaten des platzierenden schiffes übernehmen
        aktuelles_schiff = self.player_ships[self.current_ship_index]
        # schiff wird auf cursor gesetzt
        aktuelles_schiff.horizontal_line = reihe
        aktuelles_schiff.vertical_line = spalte
        
        # prüft ob gerade das schiff in kollision ist
        ist_kollision = self.game.playingfield.check_collision(aktuelles_schiff, self.game.player.field)
        vorschau_farbe = Colors.PREVIEW_ERROR if ist_kollision else Colors.PREVIEW
        
        # schiffsform wird in koordinaten übergeben die das schiff belegt
        for pos in aktuelles_schiff.get_positions():
            r_pos, s_pos = pos[0], pos[1]
            # prüft on schiff position in feld liegt
            if 0 <= r_pos < self.fieldsize and 0 <= s_pos < self.fieldsize:
                # ausgewähltes schiff kann nur wasser einfärben
                if self.game.player.field[r_pos][s_pos] == "O":
                    # feld wird eingefärbt je nachdem ob kollsion vorhanden oder nicht
                    self.player_canvas.itemconfig(self.player_rects[r_pos][s_pos], fill=vorschau_farbe)
                    # speicherung der koordinaten um später zurückzusetzen
                    self.preview_positions.append((r_pos, s_pos))

    #
    # SPIEL STATUS
    #

    def update_status_text(self):
        # wenn noch nicht alle schiffe platziert (platzierphase)
        if self.current_ship_index < len(self.player_ships):
            # jeweilige schiff aus liste
            aktuelles_schiff = self.player_ships[self.current_ship_index]
            # passt überschrift an
            self.status_label.config(text=f"Bitte platziere {aktuelles_schiff.name} Pfeiltasten und Enter")
        # startet nach letztem schiff kampfphase
        else:
            self.start_battle_phase()

    #
    # PHASE 1: PLATZIEREN
    #

    def place_ship_at_cursor(self, r, c):
        # sicherheit (überprüft ob alle schiff platziert oder kampfphase schon sind)
        if self.current_ship_index >= len(self.player_ships) or self.battle_phase:
            return

        # schiff wird ausgewählt
        aktuelles_schiff = self.player_ships[self.current_ship_index]
        # schiff wird in jeweilige zeile/reihe geschrieben
        aktuelles_schiff.horizontal_line = r
        aktuelles_schiff.vertical_line = c

        # sicherheits kollision abfrage
        ist_kollision = self.game.playingfield.check_collision(aktuelles_schiff, self.game.player.field)
        # schiff kann nicht in kollision platziert werden
        if ist_kollision:
            return 

        # vorschau farbe wird gelöscht
        self.clear_preview()
        # schiff wird in koordinaten player.field gitter geschrieben
        self.game.playingfield.ships_place(aktuelles_schiff, self.game.player.field)
        

        schiff_positionen = aktuelles_schiff.get_positions()
        # koordianten aller segemente des schiffs
        for pos in schiff_positionen:
            r_pos, s_pos = pos[0], pos[1]
            # schiff wird nun dauerhaft platziert
            self.player_canvas.itemconfig(self.player_rects[r_pos][s_pos], fill=Colors.SHIP)

        # nächstes schiff
        self.current_ship_index += 1
        # textfeld update
        self.update_status_text()
        
        # wenn nächstes schiff cursor für nächstes schiff anzeigen
        if self.current_ship_index < len(self.player_ships):
            self.draw_cursor_visuals(r, c)

    #
    # PHASE 2: SCHIESSEN
    #

    def start_battle_phase(self):
        # kampfphase starten
        self.battle_phase = True
        # überschrift anpassen
        self.status_label.config(text="Feuer Frei wähle ein Ziel")
        
        # blendet rotationsbutton aus
        self.rotate_btn.pack_forget()
        # akualisiert computer spielfeld überschrift
        self.computer_frame.config(text="Computer Spielfeld")
        
        # entfernt reste von farben der letzten schiffplazierung
        self.clear_preview()
        # postioniert cursor zum start oben rechts
        self.controller.set_cursor(0, 0)

    def shoot_at_cursor(self, r, c):
        # sicherheit prüft ob in kampfphase
        if not self.battle_phase:
            return
        # prüft felder X Treffer / ~ Wasser
        if self.game.computer.field[r][c] in ["X", "~"]:
            return
        # wenn kampfphase und wasser schuss möglich    
        self.player_shoot(r, c)



    def player_shoot(self, reihe, spalte):
        # schuss ausführung
        # koordinaten des schuss in liste
        schuss = [reihe, spalte]
        # kopie schiff liste zum vergleich ob versenkt
        schiffe_vorher = list(self.game.computer.ships)
        # prüft ob auf jeweiligem feld ein schiff ist
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.computer.ships)

        # treffer
        if wurde_getroffen:
            # feld wir mit X für treffer maktiert
            self.game.computer.field[reihe][spalte] = "X"
            # einfärbung des feldes
            self.computer_canvas.itemconfig(self.computer_rects[reihe][spalte], fill=Colors.HIT)
            
            # versenktes schiff markieren
            # wenn schiffanzahl kleiner
            if len(self.game.computer.ships) < len(schiffe_vorher):
                # vergleicht alte mit neuer liste aller schiff
                versenktes_schiff = [s for s in schiffe_vorher if s not in self.game.computer.ships][0]
                # geht koordinaten des versenkten schiffs durch und färbt felder ein
                for pos in versenktes_schiff.get_positions():
                    self.computer_canvas.itemconfig(self.computer_rects[pos[0]][pos[1]], fill=Colors.SUNK)
        # daneben
        else:
            # feld wird mit ~ für wasser makiert
            self.game.computer.field[reihe][spalte] = "~"
            # einfärbung in verfehlt
            self.computer_canvas.itemconfig(self.computer_rects[reihe][spalte], fill=Colors.MISS)

        # abbruchbedinung
        # wenn liste der schiffe leer
        if len(self.game.computer.ships) == 0:
            # pop up
            messagebox.showinfo("Sieg", "Herzlichen Glückwunsch")
            # beendet programm
            self.main_window.quit()
            # nach letztem schiff abbruch 
            return

        # computer zug
        # wenn computer schießt keine aktionen mehr möglich
        self.battle_phase = False 
        # wartet x-millisekungen dann wird computer schuss ausgeführt
        self.main_window.after(300, self.computer_shoot)

    def computer_shoot(self):
        # schleife für schusse des computer
        while True:
            # generiert zufällige reihe/spalte
            reihe = random.randint(0, self.fieldsize - 1)
            spalte = random.randint(0, self.fieldsize - 1)
            # schaut ob auf das feld schon geschossen wurde falls ja schleife erneut
            if self.game.player.field[reihe][spalte] not in ["X", "~"]:
                break 

        # computer feuert auf die gefunden koordinaten
        schuss = [reihe, spalte]
        # (nun selber ablauf wie bei spieler schuss)
        schiffe_vorher = list(self.game.player.ships)
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.player.ships)

        # treffer verarbeiten
        if wurde_getroffen:
            self.game.player.field[reihe][spalte] = "X"
            self.player_canvas.itemconfig(self.player_rects[reihe][spalte], fill=Colors.HIT)
            self.status_label.config(text="computer hat getroffen")
            
            if len(self.game.player.ships) < len(schiffe_vorher):
                versenktes_schiff = [s for s in schiffe_vorher if s not in self.game.player.ships][0]
                for pos in versenktes_schiff.get_positions():
                    self.player_canvas.itemconfig(self.player_rects[pos[0]][pos[1]], fill=Colors.SUNK)
        else:
            self.game.player.field[reihe][spalte] = "~"
            self.player_canvas.itemconfig(self.player_rects[reihe][spalte], fill=Colors.MISS)
            self.status_label.config(text="wasser")

        # wenn computer letztes schiff versenkt
        if len(self.game.player.ships) == 0:
            # pop up
            messagebox.showerror("Spiel vorbei", "Computer hat gewonnen")
            # schließt fenster
            self.main_window.quit() 
        # falls nicht alle versenkt spieler ist wieder dran
        else:
            self.battle_phase = True

# hauptprogramm starten
if __name__ == "__main__":
    game = tk.Tk()
    app = BattleShipGUI(game)
    game.mainloop()