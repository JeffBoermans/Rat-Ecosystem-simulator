from .entity import Entity
from .organism_info import OrganismInfo

class Organism(Entity):
    def __init__(self, e_name: str, e_age: int, e_id: int, e_sex, e_info: OrganismInfo):
        super().__init__(e_name, e_age, e_id)
        self.sex = e_sex
        self.organismInfo = e_info
