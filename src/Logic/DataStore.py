import json

from typing import List

from .Entities.organism import Organism
from .Entities.vegetation import MonoVegetationCluster


class DataStore(object):
    """This class contains the data logic of a simulation.
    organisms: A list of all organisms in the ecosystem; Rats, Birds, Snakes, ...
    """

    def __init__(self, s_path: str):
        self.session_path: str = s_path
        self.organisms: List[Organism] = []
        self.death_organisms: List[Organism] = []
        self.vegetation: List[MonoVegetationCluster] = []
        self.foodChain: dict = {}

        self.__organism_id_counter: int = 1
        self.__vegetation_id_counter: int = 1

    def reserve_organism_id(self) -> int:
        """Reserve a unique organism id.

        An output id will never appear twice.
        """
        reserved_id = self.__organism_id_counter
        self.__organism_id_counter += 1
        return reserved_id

    def reserve_vegetation_id(self) -> int:
        """Reserve a unique vegetation id.

        An output id will never appear twice.
        """
        reserved_id = self.__vegetation_id_counter
        self.__vegetation_id_counter += 1
        return reserved_id

    def printOrganisms(self):
        for org in self.organisms:
            print(str(org.id) + "; age: " + str(org.age) +
                  "; gender: " + str(org.sex.name))
