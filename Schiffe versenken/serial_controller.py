class SerialController:
    """Brücke: tut so als wäre es der Controller,
    schickt aber alles über Serial an den Pico."""

    def __init__(self, pico):
        self.pico = pico

    def vibrate(self, duration):
        self.pico.write(b"vibrate\n") #b--> Byte Objekt erstellen 

    def set_led_single(self, index, farbe):
        r, g, b = farbe
        befehl = f"led {index} {r} {g} {b}\n"
        self.pico.write(befehl.encode())

    def set_led_all(self, farbe):
        r, g, b = farbe
        for i in range(8):
            befehl = f"led {i} {r} {g} {b}\n"
            self.pico.write(befehl.encode()) #--> Bytes an Pico