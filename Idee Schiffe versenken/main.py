import tkinter as tk
from tkinter import messagebox
import random
from game_logic import SeaBattleLogic
from gui_components import BoardUI, Colors
from ships import ShipDefinitions

class GameController:
    def __init__(self):
        # Initialisierung des Hauptfensters
        self.root = tk.Tk()
        self.root.title("SEA BATTLE: TACTICAL COMMAND")
        self.root.configure(bg=Colors.BG) # Dunkler Hintergrund aus gui_components
        
        # Instanz der Spiellogik erstellen
        self.logic = SeaBattleLogic()
        
        # Spielstatus-Variablen
        self.phase = "PLACING"      # Startphase: Schiffe platzieren
        self.rotation = "H"         # Standard-Rotation: Horizontal
        self.active_ability = None  # Aktuell gewählte Spezialfähigkeit
        
        # Benutzeroberfläche aufbauen
        self._setup_ui()
        
        # Tastatur-Bindung: 'R' drücken zum Drehen der Schiffe
        self.root.bind('r', lambda e: self._toggle_rotation())
        self.root.bind('R', lambda e: self._toggle_rotation())
        
        # Hauptschleife starten
        self.root.mainloop()

    def _setup_ui(self):
        """Erstellt alle grafischen Elemente des Spiels."""
        # Header-Bereich für Titel und Status
        header = tk.Frame(self.root, bg=Colors.BG)
        header.pack(fill="x", pady=10)
        
        self.info_label = tk.Label(header, text="PLATZIERE DEINE FLOTTE", 
                                  bg=Colors.BG, fg=Colors.HOVER, font=("Courier", 16, "bold"))
        self.info_label.pack()

        # Energieanzeige für Spieler und KI
        self.energy_label = tk.Label(header, text="ENERGY | DU: 2 | KI: 2", 
                                    bg=Colors.BG, fg=Colors.ENERGY, font=("Courier", 12))
        self.energy_label.pack()

        # Hauptcontainer für die Spielfelder
        main_frame = tk.Frame(self.root, bg=Colors.BG)
        main_frame.pack(padx=20, pady=10)

        # Linkes Feld: Gegner (KI) - Hier klickt der Spieler zum Angreifen
        self.ui_ai = BoardUI(main_frame, "GEGNERISCHER RADAR", callback=self.handle_ai_click)
        self.ui_ai.pack(side="left", padx=10)
        
        # Rechtes Feld: Spieler - Hier platziert man Schiffe und sieht gegnerische Angriffe
        # Enthält Hover-Effekte für die Platzierungs-Vorschau
        self.ui_player = BoardUI(main_frame, "EIGENE BASIS", callback=self.handle_player_click, 
                                hover_cb=self.show_preview, leave_cb=self.clear_preview)
        self.ui_player.pack(side="left", padx=10)

        # Bereich für die Aktions-Buttons (Fähigkeiten)
        ab_frame = tk.Frame(self.root, bg=Colors.BG)
        ab_frame.pack(pady=20)
        
        for ab in ["SCAN", "MINE", "BOMB", "AIRSTRIKE"]:
            cost = ShipDefinitions.COSTS[ab]
            btn = tk.Button(ab_frame, text=f"{ab}\n({cost})", 
                            bg=Colors.PANEL, fg=Colors.TEXT, font=("Courier", 10, "bold"),
                            relief="flat", width=12, command=lambda a=ab: self._select_ability(a))
            btn.pack(side="left", padx=5)

    def _toggle_rotation(self):
        """Wechselt die Ausrichtung der Schiffe (H <-> V)."""
        self.rotation = "V" if self.rotation == "H" else "H"
        self.info_label.config(text=f"ROTATION: {self.rotation}")

    def _select_ability(self, ability):
        """Aktiviert eine Spezialfähigkeit, wenn genug Energie vorhanden ist."""
        if self.logic.energy_player >= ShipDefinitions.COSTS[ability]:
            self.active_ability = ability
            self.info_label.config(text=f"MODUS: {ability} AKTIV")
        else:
            messagebox.showwarning("Energie", "Nicht genug Energie für diese Aktion!")

    def handle_ai_click(self, x, y):
        """Wird aufgerufen, wenn der Spieler auf das gegnerische Feld klickt."""
        if self.phase != "BATTLE" or self.active_ability == "MINE": 
            return # Angriffe nur in der Kampfphase erlaubt
            
        executed = False # Marker, ob ein gültiger Zug gemacht wurde
        
        # 1. Fall: Fähigkeit SCAN
        if self.active_ability == "SCAN":
            count = self.logic.use_scan(x, y)
            if count is not None:
                # Hintergrund bleibt dezent (Status 3 = Grau/Miss-Farbe)
                self.ui_ai.update_cell(x, y, 3, text=str(count))
                executed = True
        
        # 2. Fall: Fähigkeit BOMBE (2x2 Bereich)
        elif self.active_ability == "BOMB":
            self.logic.energy_player -= ShipDefinitions.COSTS["BOMB"]
            for dy in range(2):
                for dx in range(2):
                    res, sunk = self.logic.check_shot(x+dx, y+dy, self.logic.ai_board, self.logic.ai_ships)
                    if res != "OUT": 
                        self._render_shot(self.ui_ai, x+dx, y+dy, res, sunk, self.logic.ai_ships)
            executed = True

        # 3. Fall: Fähigkeit AIRSTRIKE (Ganze Reihe oder Spalte)
        elif self.active_ability == "AIRSTRIKE":
            self.logic.energy_player -= ShipDefinitions.COSTS["AIRSTRIKE"]
            for i in range(10):
                # Wenn R auf H steht: schießt ganze Zeile. Wenn auf V: schießt Spalte.
                nx, ny = (i, y) if self.rotation == "H" else (x, i)
                res, sunk = self.logic.check_shot(nx, ny, self.logic.ai_board, self.logic.ai_ships)
                if res != "OUT": 
                    self._render_shot(self.ui_ai, nx, ny, res, sunk, self.logic.ai_ships)
            executed = True

        # 4. Fall: Normaler Schuss
        else:
            res, sunk = self.logic.check_shot(x, y, self.logic.ai_board, self.logic.ai_ships)
            if res != "ALREADY":
                self._render_shot(self.ui_ai, x, y, res, sunk, self.logic.ai_ships)
                executed = True
        
        # Wenn der Zug gültig war, Runde beenden und KI ziehen lassen
        if executed: 
            self._end_turn()

    def handle_player_click(self, x, y):
        """Wird aufgerufen, wenn der Spieler auf sein eigenes Feld klickt (Platzieren/Minen)."""
        # Phase 1: Schiffe platzieren
        if self.phase == "PLACING":
            name = self.logic.ships_to_place[0]
            if self.logic.place_ship(self.logic.player_board, x, y, name, self.rotation):
                self.logic.ships_to_place.pop(0)
                if not self.logic.ships_to_place:
                    self.phase = "BATTLE"
                    self.info_label.config(text="GEFECHT AKTIV")
                self.clear_preview()
        
        # Phase 2: Mine legen (während der Kampfphase)
        elif self.active_ability == "MINE":
            if self.logic.player_board[y][x] == 0: # Nur in Wasser platzierbar
                self.logic.player_board[y][x] = 4 # 4 = Status für Mine
                self.logic.energy_player -= ShipDefinitions.COSTS["MINE"]
                self.ui_player.update_cell(x, y, 4)
                self.active_ability = None
        self._update_ui()

    def _render_shot(self, ui, x, y, res, sunk_name, ship_dict):
        """Zentrale Funktion zur grafischen Darstellung von Treffern."""
        if res == "SUNK":
            # Wenn ein Schiff versenkt wurde, färbe alle Teile Lila (SUNK-Status)
            for sx, sy in ship_dict[sunk_name]:
                ui.update_cell(sx, sy, "SUNK")
        elif res in ["HIT", "MISS", "MINE"]:
            # Normaler Treffer (Rot) oder Fehlschuss (Grau) oder Mine getroffen (Orange)
            ui.update_cell(x, y, 2 if res in ["HIT", "MINE"] else 3)
        self._check_game_over()

    def _end_turn(self):
        """Beendet den Spielerzug und führt den KI-Zug aus."""
        self.active_ability = None
        self.logic.energy_player += 1 # Energie-Regeneration
        self.logic.energy_ai += 1
        
        # KI entscheidet über ihre Aktion (Gezielte Jagd oder Spezialangriff)
        action, results = self.logic.ai_decide_action()
        
        if action != "NORMAL":
            messagebox.showinfo("KI ANGRIFF", f"Die KI nutzt {action}!")
        
        # KI-Ergebnisse auf dem Spielerfeld anzeigen
        for x, y, res, sunk in results:
            self._render_shot(self.ui_player, x, y, res, sunk, self.logic.player_ships)
            
            # Falls die KI eine Mine des Spielers trifft
            if res == "MINE":
                messagebox.showinfo("MINE!", "Die KI ist auf deine Mine gefahren! 2 Bonus-Schüsse für dich!")
                for _ in range(2):
                    rx, ry = random.randint(0,9), random.randint(0,9)
                    r_res, r_sunk = self.logic.check_shot(rx, ry, self.logic.ai_board, self.logic.ai_ships)
                    self._render_shot(self.ui_ai, rx, ry, r_res, r_sunk, self.logic.ai_ships)
        
        self._update_ui()

    def _update_ui(self):
        """Aktualisiert die Labels (Energie, etc.)."""
        self.energy_label.config(text=f"ENERGY | DU: {self.logic.energy_player} | KI: {self.logic.energy_ai}")

    def _check_game_over(self):
        """Prüft, ob eine Seite keine Schiffe mehr hat."""
        # Alle Felder prüfen, ob noch ein Schiffsteil (Status 1) existiert
        if all(all(c != 1 for c in r) for r in self.logic.ai_board): 
            self._announce("SIEG - ALLE GEGNERISCHEN SCHIFFE ZERSTÖRT!")
        elif all(all(c != 1 for c in r) for r in self.logic.player_board): 
            self._announce("NIEDERLAGE - DEINE FLOTTE WURDE VERSENKT!")

    def _announce(self, msg):
        """Beendet das Spiel mit einer Nachricht."""
        messagebox.showinfo("SPIELENDE", msg)
        self.root.destroy()

    def show_preview(self, x, y):
        """Zeigt eine Vorschau, wo das Schiff platziert werden würde."""
        if self.phase == "PLACING" and self.logic.ships_to_place:
            shape = ShipDefinitions.TYPES[self.logic.ships_to_place[0]]
            for dx, dy in shape:
                nx, ny = (x + dx, y + dy) if self.rotation == 'H' else (x + dy, y + dx)
                if 0 <= nx < 10 and 0 <= ny < 10:
                    self.ui_player.buttons[ny][nx].config(bg=Colors.HOVER)

    def clear_preview(self):
        """Setzt die Farben des Spielerbretts zurück (löscht die Vorschau)."""
        for y in range(10):
            for x in range(10):
                self.ui_player.update_cell(x, y, self.logic.player_board[y][x])

if __name__ == "__main__":
    # Spiel starten
    GameController()