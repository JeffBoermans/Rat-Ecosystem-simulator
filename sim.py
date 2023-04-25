from Entities.organism import Organism
from Entities.vegetation import Vegetation
import json

class Simulation:
    def __init__(self, s_path: str):
        self.session_path: str = s_path
        self.organisms = []
        self.vegetation = []
    def setUp(self):
        print("Reading session file")
        self.processInput()

    def processInput(self):
        f = open(self.session_path)
        data = json.load(f)
        e_id = 0
        for organism in data['organisms']:
            self.organisms.append(Organism(organism["name"], organism["age"], e_id))
            e_id += 1
        v_id = 0
        for vegetation in data['vegetation']:
            self.vegetation.append(Vegetation(vegetation["name"], vegetation["age"], v_id))
            v_id += 1
