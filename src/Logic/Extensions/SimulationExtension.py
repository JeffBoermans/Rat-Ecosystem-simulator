
from ..DataStore import DataStore
from ..Entities.entity import Entity


class SimulationExtension(object):
    """An extension of the simulation.

    This base class defines the functionality shared amongst
    all extensions. 
    """
    def __init__(self, extension_name: str) -> None:
        self.name = extension_name
    
    def next_day(self, datastore: DataStore) -> None:
        raise NotImplementedError(f"Missing required (pure virtual) method of the extension interface: {self.next_day.__name__}")


class SimulationMortalityExtension(SimulationExtension):
    """The base class of all extensions add new ways for entities to die.

    Each mortality extension implements a common interface defined by this
    base class, which allows the simulation to call the list of all extensions
    to cull the entity populations accordingly.
    """
    def should_die(self, organism: Entity, datastore: DataStore) -> bool:
        """Decide whether the organism should die, based on the state
        of the simulation and the additional statistics kept by the
        extension.
        """
        raise NotImplementedError(f"Missing required (pure virtual) method of the mortality extension interface: {self.should_die.__name__}")