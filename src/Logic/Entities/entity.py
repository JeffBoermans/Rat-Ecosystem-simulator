class Entity:
    def __init__(self, e_name: str, e_age: int, e_id: int):
        """
        age: age in days
        """
        self.name: str = e_name
        self.age: int = e_age  # TODO: Don't work with age?
        self.id: int = e_id
        self.alive = True

