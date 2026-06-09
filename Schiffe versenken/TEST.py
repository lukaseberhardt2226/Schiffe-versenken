
import time
import random

from controller import Controller
from cursor import Cursor
from fähigkeiten import Skill_Show, Skills

controller = Controller()
cursor = Cursor()
skill_show = Skill_Show(controller)
skills = Skills(controller, cursor, skill_show, None)  # None weil Spielfeld noch fehlt

# Test
skill_show.punkte_hinzufuegen(3)
print(cursor.get_position())