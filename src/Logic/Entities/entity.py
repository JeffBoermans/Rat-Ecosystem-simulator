class Entity:
    def __init__(self, e_name: str, e_age: int, e_id: int):
        """
        age: age in days
        """
        self.name: str = e_name
        self.age: int = e_age  # TODO: Don't work with age?
        self.id: int = e_id

    def should_die_naturally(self) -> bool:
        """Whether the entity should die of natural causes.

        This method may be implemented either deterministically or
        stochastically.

        This method is a generalization of death by natural causes.
        Natural causes include age, ... but should manually exclude
        causes that are part of the simulation itself. For example,
        if the simulation implements wildfire events, then death by
        wildfire should not be considered by this method to determine
        whether the organism should die.
        """
        raise NotImplementedError("A derived entity should specify natural mortality dynamics")
