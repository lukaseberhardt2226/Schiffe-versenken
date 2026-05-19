import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
import random

from main import BattleShip
import ships

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
        
        # überschreibt listen mit leeren o für saubere platzierung
        self.game.player.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        self.game.computer.field = [["O"] * self.fieldsize for _ in range(self.fieldsize)]
        
        # index zählt welches schiff spieler platziert 0 ist erstes schiff
        self.current_ship_index = 0
        
        # referenz auf schiffsliste des spielers
        self.player_ships = self.game.player.ships
        
        # setzt gegnerische schiffe zufällig im hintergrund
        self.game.computer_place_ships()
        
        # listen speichern button objekte um text und farbe zu ändern
        self.player_buttons = []
        self.computer_buttons = []
        
        # aufruf der methode für visuelle steuerelemente
        self.create_widgets()
        
        # ersten hinweistext generieren und anzeigen
        self.update_status_text()


    # OBERFLÄCHEN AUFBAU WIDGETS UND LAYOUT
    def create_widgets(self):
        # erstellt alle visuellen komponenten
        
        # STATUS LABEL
        # ttk label erzeugt textfeld
        # schriftart schriftgröße fettdruck
        self.status_label = ttk.Label(self.main_window, text="", font=("Arial", 12, "bold"))
        
        # platziert label oben im fenster
        # sorgt für vertikalen abstand
        self.status_label.pack(pady=10)
        
        # rotations button
        # ttk button erzeugt schaltfläche
        # verknüpft klick mit rotation
        self.rotate_btn = ttk.Button(self.main_window, text="Schiff drehen", command=self.rotate_current_ship)
        
        # button unter label anordnen
        self.rotate_btn.pack(pady=5)
        
        # container frame
        # ttk frame erzeugt unsichtbaren container
        # rahmen verankert spielfelder nebeneinander
        fields_frame = ttk.Frame(self.main_window)
        fields_frame.pack(padx=15, pady=15) 
        
        # spieler spielfeld links
        # ttk labelframe erzeugt box mit rahmen und titel
        player_frame = ttk.LabelFrame(fields_frame, text="Dein Spielfeld (Schiffe platzieren)")
        
        # richtet rahmen im hauptcontainer links aus
        player_frame.pack(side=tk.LEFT, padx=15)
        
        # äußere schleife läuft durch zeilen des spielfelds
        for reihe in range(self.fieldsize):
            row_buttons = [] 
            
            # innere schleife läuft durch spalten der zeile
            for spalte in range(self.fieldsize):
                # erstellt button im spieler frame
                btn = ttk.Button(player_frame, text="O", width=5)
                
                # button bekommt zwei neue variablen
                # button speichert eigene koordinaten
                btn.reihe_pos = reihe
                btn.spalte_pos = spalte
                
                # bei klick wird spielfeld klick aufgerufen
                # button übergibt sich selbst als argument
                btn.config(command=lambda b=btn: self.player_field_click(b))
                
                # grid manager positioniert button in tabelle
                # erzeugt lücken zwischen feldern
                btn.grid(row=reihe, column=spalte, padx=2, pady=2)
                
                # button in zeilenliste einfügen
                row_buttons.append(btn)
                
            # fertige zeile in gesamtliste eintragen
            self.player_buttons.append(row_buttons)
            
        # computer spielfeld rechts
        # erstellt rechten rahmen für computer
        self.computer_frame = ttk.LabelFrame(fields_frame, text="Computer Spielfeld (Gesperrt)")
        
        # ordnet rahmen rechts im container an
        self.computer_frame.pack(side=tk.RIGHT, padx=15)
        
        # erstellt button matrix für gegner
        for reihe in range(self.fieldsize):
            row_buttons = []
            for spalte in range(self.fieldsize):
                # sperrt button für klicks
                # spieler darf während platzierung nicht drücken
                btn = ttk.Button(self.computer_frame, text="O", width=5, state="disabled")
                btn.reihe_pos = reihe
                btn.spalte_pos = spalte
                
                # positioniert im rechten grid
                btn.grid(row=reihe, column=spalte, padx=2, pady=2)
                row_buttons.append(btn)
            self.computer_buttons.append(row_buttons)


    # BEDIENUNG UND STATUS ANZEIGEN
    def update_status_text(self):
        # aktualisiert anweisungen im label
        # wenn nicht alle schiffe platziert sind
        if self.current_ship_index < len(self.player_ships):
            aktuelles_schiff = self.player_ships[self.current_ship_index]
            # ändert text des labels dynamisch
            self.status_label.config(text=f"Bitte platziere {aktuelles_schiff.name}")
        else:
            # wechselt phase wenn alle schiffe platziert sind
            self.start_battle_phase()

    def rotate_current_ship(self):
        # aufruf wenn schiff drehen geklickt wird
        # prüft ob noch schiffe übrig sind
        if self.current_ship_index < len(self.player_ships):
            # holt aktuelles schiff aus liste
            aktuelles_schiff = self.player_ships[self.current_ship_index]
            
            # dreht schiff um 90 grad
            aktuelles_schiff.rotate()
            
            # messagebox öffnet popup als feedback
            messagebox.showinfo("Drehung", f"{aktuelles_schiff.name} wurde gedreht!")


    # PHASE 1 LOGIK FÜR DAS PLATZIEREN DER SCHIFFE
    def player_field_click(self, clicked_button):
        # event handler bei klick auf eigenes feld
        # bricht ab wenn alle schiffe gesetzt sind
        if self.current_ship_index >= len(self.player_ships):
            return

        # liest koordinaten aus gedrücktem button
        reihe = clicked_button.reihe_pos
        spalte = clicked_button.spalte_pos

        # sucht aktuelles schiff objekt
        aktuelles_schiff = self.player_ships[self.current_ship_index]
        
        # speichert startkoordinaten im schiff objekt
        aktuelles_schiff.horizontal_line = reihe
        aktuelles_schiff.vertical_line = spalte

        # nutzt kollisionsprüfung
        # gibt true bei kollision oder randüberschreitung
        ist_kollision = self.game.playingfield.check_collision(aktuelles_schiff, self.game.player.field)

        if ist_kollision == True:
            # zeigt fehlermeldung im popup
            messagebox.showwarning("Kollision", "Ungültige Position! Schiff ragt heraus oder blockiert.")
            return 

        # trägt schiff ins backend spielfeld ein
        self.game.playingfield.ships_place(aktuelles_schiff, self.game.player.field)
        
        # macht schiff auf buttons sichtbar
        # liefert alle belegten koordinaten
        schiff_positionen = aktuelles_schiff.get_positions()
        for pos in schiff_positionen:
            r_pos = pos[0]
            s_pos = pos[1]
            # ändert button text auf schiffsymbol
            self.player_buttons[r_pos][s_pos].config(text="■")

        # erhöht index für nächstes schiff
        self.current_ship_index += 1
        
        # aktualisiert label oder startet kampf
        self.update_status_text()


    # PHASE 2 LOGIK FÜR DIE KAMPFPHASE DAS DUELL
    def start_battle_phase(self):
        # schaltet ui in kampfmodus um
        self.status_label.config(text="FEUER FREI! Klicke auf das gegnerische Feld.")
        
        # rotations button wird nicht mehr gebraucht
        # entfernt widget aus anzeige
        self.rotate_btn.pack_forget()
        
        # deaktiviert alle buttons des spielers
        # schiffe können nicht mehr verschoben werden
        for reihe in range(self.fieldsize):
            for spalte in range(self.fieldsize):
                self.player_buttons[reihe][spalte].config(state="disabled")
        
        # aktualisiert titel des gegnerischen rahmens
        self.computer_frame.config(text="Computer Spielfeld")
        
        # aktiviert computer spielfeld für schüsse
        for reihe in range(self.fieldsize):
            for spalte in range(self.fieldsize):
                # schaltet knöpfe wieder aktiv
                # verknüpft knopf mit schuss methode
                self.computer_buttons[reihe][spalte].config(
                    state="normal",
                    command=lambda b=self.computer_buttons[reihe][spalte]: self.player_shoot(b)
                )

    def player_shoot(self, clicked_button):
        # verarbeitet schuss des spielers auf gegner grid
        # liest koordinaten des buttons
        reihe = clicked_button.reihe_pos
        spalte = clicked_button.spalte_pos
        
        schuss = [reihe, spalte]
        
        # prüft ob schiff getroffen wurde
        # erhöht trefferzähler und löscht schiff falls nötig
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.computer.ships)

        if wurde_getroffen == True:
            # markiert als treffer im computerfeld
            self.game.computer.field[reihe][spalte] = "X"
            # ändert button text und deaktiviert ihn
            clicked_button.config(text="X", state="disabled")
        else:
            # markiert als wasser im computerfeld
            self.game.computer.field[reihe][spalte] = "~"
            clicked_button.config(text="~", state="disabled")

        # prüft siegbedingung für spieler
        # spieler gewinnt wenn computer schiffe leer sind
        if len(self.game.computer.ships) == 0:
            messagebox.showinfo("Sieg", "Herzlichen Glückwunsch! Du hast gewonnen!")
            self.main_window.quit() 
            return

        # verzögert aktion um halbe sekunde
        # startet automatisch gegenzug des computers
        self.main_window.after(500, self.computer_shoot)

    def computer_shoot(self):
        # computer ki schießt zufällig auf spielerfeld
        # schleife bis gültiges feld gefunden wird
        while True:
            reihe = random.randint(0, self.fieldsize - 1)
            spalte = random.randint(0, self.fieldsize - 1)
            # schuss ist gültig wenn feld leer ist
            if self.game.player.field[reihe][spalte] not in ["X", "~"]:
                break 

        schuss = [reihe, spalte]
        
        # prüft ob schuss spielerschiff trifft
        wurde_getroffen = self.game.playingfield.check_hit(schuss, self.game.player.ships)
        
        # sucht passenden button im spielerfeld
        target_button = self.player_buttons[reihe][spalte]

        if wurde_getroffen == True:
            # speichert treffer im spielerfeld
            self.game.player.field[reihe][spalte] = "X"
            # ändert text auf button
            target_button.config(text="X")
            self.status_label.config(text="Der Computer hat dein Schiff getroffen!")
        else:
            self.game.player.field[reihe][spalte] = "~"
            target_button.config(text="~")
            self.status_label.config(text="Wasser! Du bist wieder an der Reihe.")

        # prüft siegbedingung für computer
        # spiel verloren wenn keine eigenen schiffe übrig
        if len(self.game.player.ships) == 0:
            messagebox.showerror("Spiel vorbei", "Der Computer hat deine gesamte Flotte versenkt!")
            self.main_window.quit() 


# RAHMENPROGRAMM ZUM ANWENDUNGSSTART
if __name__ == "__main__":
    # erzeugt hauptfenster basisobjekt
    game = tk.Tk()
    
    # nimmt fensterkonfiguration vor (länge x breite)
    game.geometry("600x300")      
    
    # bildet gui instanz und übergibt root
    app = BattleShipGUI(game)
    
    # startet hauptschleife
    # wartet aktiv auf eingaben
    game.mainloop()