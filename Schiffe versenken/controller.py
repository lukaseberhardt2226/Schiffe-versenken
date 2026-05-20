import curses

class Steuerung:
    """Verwaltet die Position des Cursors und die Tastatureingaben."""

    def __init__(self, max_size):
        self.max_size = max_size
        self.cursor_y = max_size // 2
        self.cursor_x = max_size // 2

    def verarbeite_taste(self, taste):
        """Bewegt den Cursor basierend auf der gedrückten Taste."""
        if taste == curses.KEY_UP and self.cursor_y > 0:
            self.cursor_y -= 1
        elif taste == curses.KEY_DOWN and self.cursor_y < self.max_size - 1:
            self.cursor_y += 1
        elif taste == curses.KEY_LEFT and self.cursor_x > 0:
            self.cursor_x -= 1
        elif taste == curses.KEY_RIGHT and self.cursor_x < self.max_size - 1:
            self.cursor_x += 1