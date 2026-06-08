import board
import neopixel
import digitalio
import time
import random

# ----------------------------
# LED Strip (8 LEDs an GP15)
# ----------------------------
pixels = neopixel.NeoPixel(board.GP15, 8, brightness=0.3, auto_write=False)

# ----------------------------
# TASTER INITIALISIERUNG (3.3V mit Pull-Down)
# ----------------------------
btn_down   = digitalio.DigitalInOut(board.GP6)   # Runter
btn_right  = digitalio.DigitalInOut(board.GP7)   # Rechts
btn_left   = digitalio.DigitalInOut(board.GP9)   # Links
btn_up     = digitalio.DigitalInOut(board.GP8)   # Oben
btn_fire   = digitalio.DigitalInOut(board.GP2)   # "B" / Normal Schießen oder Abbrechen

# Spezialfähigkeiten
btn_airstrike = digitalio.DigitalInOut(board.GP3) # GP3 = Airstrike (Reihe)
btn_scan      = digitalio.DigitalInOut(board.GP4) # GP4 = Scan (3x3)
btn_column    = digitalio.DigitalInOut(board.GP5) # GP5 = Spaltenschlag

alle_taster = [btn_down, btn_right, btn_left, btn_up, btn_fire, btn_airstrike, btn_scan, btn_column]
for btn in alle_taster:
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.DOWN

# ----------------------------
# Vibrationsmotor (an GP0)
# ----------------------------
motor = digitalio.DigitalInOut(board.GP0)
motor.direction = digitalio.Direction.OUTPUT

# ----------------------------
# Variablen & Spielfeld-Optionen
# ----------------------------
FIELD_SIZE = 8  
cursor_x = 0
cursor_y = 0

player_field = [["O" for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)]
secret_field = [[0 for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)]

TOTAL_SHIP_PARTS = 16
treffer_zaehler = 0

# Modi: "NORMAL", "AIRSTRIKE_PREVIEW", "SCAN_PREVIEW", "COLUMN_PREVIEW"
current_mode = "NORMAL"

def platziere_schiff(groesse):
    platziert = False
    while not platziert:
        ausrichtung = random.choice(["H", "V"])
        if ausrichtung == "H":
            rx = random.randint(0, FIELD_SIZE - groesse)
            ry = random.randint(0, FIELD_SIZE - 1)
            if sum(secret_field[ry][rx + i] for i in range(groesse)) == 0:
                for i in range(groesse): secret_field[ry][rx + i] = 1
                platziert = True
        else:
            rx = random.randint(0, FIELD_SIZE - 1)
            ry = random.randint(0, FIELD_SIZE - groesse)
            if sum(secret_field[ry + i][rx] for i in range(groesse)) == 0:
                for i in range(groesse): secret_field[ry + i][rx] = 1
                platziert = True

# Schiffe generieren
for g in [4, 3, 3, 2, 2, 2]: platziere_schiff(g)

# ----------------------------
# HILFSFUNKTION: PRÜFEN OB EIN FELD IN DER VORSCHAU IST
# ----------------------------
def is_in_preview(x, y, cx, cy, mode):
    if mode == "AIRSTRIKE_PREVIEW":
        return y == cy  # Ganze Reihe markieren
    elif mode == "COLUMN_PREVIEW":
        return x == cx  # Ganze Spalte markieren
    elif mode == "SCAN_PREVIEW":
        return abs(x - cx) <= 1 and abs(y - cy) <= 1  # 3x3 Block um den Cursor
    return False

# ----------------------------
# ANZEIGE-FUNKTION
# ----------------------------
def update_anzeige(cx, cy):
    global treffer_zaehler
    pixels.fill((0, 0, 0))
    pixels[cy] = (255, 255, 0) 
    pixels.show()

    print("\033[2J\033[H", end="")
    print("=== PICO SCHIFFEVERSEKEN (8x8) ===")
    print(f"Cursor: Spalte {chr(65 + cx)} / Zeile {cy + 1} | Modus: {current_mode}")
    print(f"Treffer: {treffer_zaehler} von {TOTAL_SHIP_PARTS}")
    if current_mode != "NORMAL":
        print("⚠️ [Spezialtaste erneut drücken = FEUERN] | [Taste B = Abbrechen] ⚠️\n")
    else:
        print("GP3: Airstrike | GP4: Scan | GP5: Spaltenschlag | B: Schießen\n")
    
    print("    " + "  ".join([chr(65 + i) for i in range(FIELD_SIZE)]))
    print("  +-------------------------")
    
    for y in range(FIELD_SIZE):
        line_chars = []
        for x in range(FIELD_SIZE):
            # Prüfen, was auf dem aktuellen Feld angezeigt werden muss
            char_to_show = player_field[y][x]
            
            # Wenn wir im Vorschau-Modus sind und das Feld betroffen ist
            if current_mode != "NORMAL" and is_in_preview(x, y, cx, cy, current_mode):
                if char_to_show == "O":  # Nur unberührtes Wasser zeigt Vorschau an
                    char_to_show = "?"

            if x == cx and y == cy:
                line_chars.append(f"[{char_to_show}]")
            else:
                line_chars.append(f" {char_to_show} ")
        
        print(f"{y + 1} | {''.join(line_chars)}")

    if treffer_zaehler == TOTAL_SHIP_PARTS:
        print("\n🎉 GEWONNEN! Du hast alle Schiffe versenkt! 🎉")

# Start-Anzeige
update_anzeige(cursor_x, cursor_y)

def warte_auf_loslassen():
    while any(btn.value for btn in alle_taster): time.sleep(0.01)
    time.sleep(0.05)

# ----------------------------
# HAUPTSCHLEIFE
# ----------------------------
while True:
    vibriere_zeit = 0
    aktion_erfolgt = False

    # RICHTUNGSTASTEN
    if btn_down.value:
        aktion_erfolgt = True
        if cursor_y < FIELD_SIZE - 1: cursor_y += 1
        else: vibriere_zeit = 0.15
    elif btn_right.value:
        aktion_erfolgt = True
        if cursor_x < FIELD_SIZE - 1: cursor_x += 1
        else: vibriere_zeit = 0.15
    elif btn_up.value:
        aktion_erfolgt = True
        if cursor_y > 0: cursor_y -= 1
        else: vibriere_zeit = 0.15
    elif btn_left.value:
        aktion_erfolgt = True
        if cursor_x > 0: cursor_x -= 1
        else: vibriere_zeit = 0.15

    # NORMALE SCHIESSTASTE "B" (GP2)
    elif btn_fire.value:
        aktion_erfolgt = True
        if current_mode != "NORMAL":
            # Wenn wir im Vorschau-Modus waren, bricht "B" den Modus ab
            current_mode = "NORMAL"
        else:
            # Normaler Einzelschuss
            if player_field[cursor_y][cursor_x] == "O":
                if secret_field[cursor_y][cursor_x] == 1:
                    player_field[cursor_y][cursor_x] = "X"
                    treffer_zaehler += 1
                    vibriere_zeit = 0.6
                else:
                    player_field[cursor_y][cursor_x] = "~"
                    vibriere_zeit = 0.08

    # GP3: AIRSTRIKE (REIHE)
    elif btn_airstrike.value:
        aktion_erfolgt = True
        if current_mode == "AIRSTRIKE_PREVIEW":
            # 2. Drücken -> AKTION AUSFÜHREN!
            for x in range(FIELD_SIZE):
                if player_field[cursor_y][x] == "O":
                    if secret_field[cursor_y][x] == 1:
                        player_field[cursor_y][x] = "X"
                        treffer_zaehler += 1
                    else:
                        player_field[cursor_y][x] = "~"
            vibriere_zeit = 0.8  # Fette Explosion für die ganze Reihe
            current_mode = "NORMAL"
        else:
            # 1. Drücken -> Vorschau anschalten
            current_mode = "AIRSTRIKE_PREVIEW"

    # GP4: SCANNER (3x3 RADAR)
    elif btn_scan.value:
        aktion_erfolgt = True
        if current_mode == "SCAN_PREVIEW":
            # 2. Drücken -> AKTION AUSFÜHREN!
            schiff_gefunden = False
            for y in range(max(0, cursor_y - 1), min(FIELD_SIZE, cursor_y + 2)):
                for x in range(max(0, cursor_x - 1), min(FIELD_SIZE, cursor_x + 2)):
                    if secret_field[y][x] == 1 and player_field[y][x] == "O":
                        schiff_gefunden = True
            
            if schiff_gefunden:
                vibriere_zeit = 0.5  # Langes Vibrieren = Radar schlägt an! (Schiff in der Nähe!)
            else:
                vibriere_zeit = 0.05 # Ganz kurzes Klicken = Nichts gefunden.
            
            current_mode = "NORMAL"
        else:
            current_mode = "SCAN_PREVIEW"

    # GP5: SPALTENSCHLAG (SPALTE)
    elif btn_column.value:
        aktion_erfolgt = True
        if current_mode == "COLUMN_PREVIEW":
            # 2. Drücken -> AKTION AUSFÜHREN!
            for y in range(FIELD_SIZE):
                if player_field[y][cursor_x] == "O":
                    if secret_field[y][cursor_x] == 1:
                        player_field[y][cursor_x] = "X"
                        treffer_zaehler += 1
                    else:
                        player_field[y][cursor_x] = "~"
            vibriere_zeit = 0.8
            current_mode = "NORMAL"
        else:
            current_mode = "COLUMN_PREVIEW"

    # Logik- und Hardwareupdates ausführen
    if aktion_erfolgt:
        update_anzeige(cursor_x, cursor_y)
        if vibriere_zeit > 0:
            motor.value = True
            time.sleep(vibriere_zeit)
            motor.value = False
        warte_auf_loslassen()

    time.sleep(0.01)
