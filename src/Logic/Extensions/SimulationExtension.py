
from typing import List
from ..DataStore import DataStore
from ..Entities.entity import Entity
from ...Logic.Entities.organism import Organism


class SimulationExtension(object):
    """An extension of the simulation.

    This base class defines the functionality shared amongst
    all extensions. 
    """
    def __init__(self, extension_name: str) -> None:
        self.name = extension_name
    
    def next_day(self, datastore: DataStore) -> None:
        raise NotImplementedError(f"Missing required (pure virtual) method of the extension interface: {self.next_day.__name__}")

    def notify_organism_death(self, organism: Organism) -> None:
        """Notfiy the extension of the death of an organism.
        
        Used for bookkeeping within the extension.
        """
        raise NotImplementedError(f"Missing required (pure virtual) method of the extension interface: {self.next_day.__name__}")



class SimulationMortalityExtension(SimulationExtension):
    """The base class of all extensions add new ways for entities to die.

    Each mortality extension implements a common interface defined by this
    base class, which allows the simulation to call the list of all extensions
    to cull the entity populations accordingly.
    """
    def should_die(self, organism: Entity, datastore: DataStore, log: List[str]) -> bool:
        """Decide whether the organism should die, based on the state
        of the simulation and the additional statistics kept by the
        extension.

        :param organism: The organism to decide death for
        :param datastore: The simulation datastore to aid in the decision
        :param log: A log to optionally add a message to
        :return: True if organism should die, else False
        """
        raise NotImplementedError(f"Missing required (pure virtual) method of the mortality extension interface: {self.should_die.__name__}")
