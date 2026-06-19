import serial
import time

#
# SERIELLE BRÜCKE (PC <-> PICO)
#

class SerialController:
    # initialisierung der usb-verbindung
    def __init__(self, port="COM3", baudrate=115200):
        # achtung: port muss an den eigenen pc angepasst werden (z.b. COM3 bei windows)
        try:
            # timeout=0.1 verhindert, dass das programm einfriert, wenn nichts gesendet wird
            self.pico = serial.Serial(port, baudrate, timeout=0.1)
            print(f"Verbindung zu {port} erfolgreich hergestellt")
            time.sleep(2) # warte kurz, bis die usb-verbindung stabil ist
        except Exception as e:
            print(f"fehler bei der verbindung zum controller: {e}")
            self.pico = None

    #
    # DATEN EMPFANGEN (PICO -> PC)
    #

    def read_input(self):
        # liest daten vom pico (z.b. tastendrücke wie "UP" oder "A")
        if self.pico and self.pico.in_waiting > 0:
            try:
                # zeile auslesen, umwandeln (decode) und zeilenumbrüche entfernen (strip)
                daten = self.pico.readline().decode("utf-8").strip()
                return daten
            except:
                return None
        return None

    #
    # BEFEHLE SENDEN (PC -> PICO)
    #

    def vibrate(self):
        # schickt den vibrations-befehl an den pico
        if self.pico:
            self.pico.write(b"vibrate\n")

    def set_led_single(self, index, farbe):
        # einzelne led steuern (farbe ist ein tuple, z.b. (255, 0, 0) für rot)
        r, g, b = farbe
        befehl = f"led_single {index} {r} {g} {b}\n"
        if self.pico:
            # befehl in bytes umwandeln und senden
            self.pico.write(befehl.encode("utf-8"))

    def set_led_all(self, farbe):
        # alle leds steuern
        r, g, b = farbe
        befehl = f"led_all {r} {g} {b}\n"
        if self.pico:
            self.pico.write(befehl.encode("utf-8"))