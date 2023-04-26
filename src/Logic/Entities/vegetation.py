from src.Logic.Entities.entity import Entity
class Vegetation(Entity):
    def __init__(self, v_name: str, v_age: int, v_id: int):
        super().__init__(v_name, v_age, v_id)
