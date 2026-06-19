class Cursor:  
    def __init__(self, feldgroesse=9):
        self.x = 0
        self.y = 0
        self.feldgroesse = feldgroesse

    def move(self,richtung):
        if richtung == "Rechts":
            self.x+=1
            if self.x>=9:
                self.x=9
        if richtung == "Links":
            self.x-=1
            if self.x<0:
                self.x=0
        if richtung == "Oben":
            self.y+=1
            if self.y>=9:
                self.y=9
        if richtung == "Unten":
            self.y-=1
            if self.y<0:
                self.y=0

    def get_position(self):
        return (self.x, self.y)
    
if __name__ == "__main__":
    cursor = Cursor()
    
    # Test Rechts
    for i in range(12):
        cursor.move("Rechts")
        print("Rechts:", cursor.get_position())
    
    # Test Links
    for i in range(12):
        cursor.move("Links")
        print("Links:", cursor.get_position())
    
    # Test Oben
    for i in range(12):
        cursor.move("Oben")
        print("Oben:", cursor.get_position())
    
    # Test Unten
    for i in range(12):
        cursor.move("Unten")
        print("Unten:", cursor.get_position())