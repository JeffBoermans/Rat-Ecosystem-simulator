from src.Logic.Entities.entity import Entity

class Organism(Entity):
    def __init__(self, e_name: str, e_age: int, e_id: int):
        super().__init__(e_name, e_age, e_id)

