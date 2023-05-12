from src.Logic.DataStore import DataStore
from .SimulationExtension import SimulationMortalityExtension
from ..DataStore import DataStore
from ..Entities.entity import Entity
from ..Entities.organism import Organism


class ForagingExtension(SimulationMortalityExtension):
    def __init__(self, extension_name: str='foraging') -> None:
        super().__init__(extension_name)

    def next_day(self, datastore: DataStore) -> None:
        pass

    def should_die(self, organism: Entity, datastore: DataStore) -> bool:
        if not isinstance(organism, Organism):
            return False

        # Temp implementation: die if organism old and no corn in vegetation
        try:
            return next((True for vegetation in datastore.vegetation if organism.age >= 4 and vegetation.name == 'Corn'))
        except StopIteration:
            return False
