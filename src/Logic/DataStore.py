from typing import List, Dict, Tuple

from .Entities.organism import Organism, OrganismSexesEnum
from .Entities.vegetation import MonoVegetationCluster


class DataStore(object):
    """This class contains the data logic of a simulation.
    organisms: A list of all organisms in the ecosystem; Rats, Birds, Snakes, ...
    """

    def __init__(self, s_path: str):
        self.session_path: str = s_path
        self.organisms: List[Organism] = []
        self.dead_organisms: List[Organism] = []
        self.vegetation: List[MonoVegetationCluster] = []
        self.foodChain: dict = {}

        self.male_organisms: List[Organism] = []
        self.female_organisms: List[Organism] = []
        # Map organisms to indexes in organism and sex specific lists
        # Map is (organism index, organism sex index)
        self.org_map: Dict[Organism, Tuple[int, int]] = dict()

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

    def add_organism(self, org: Organism):
        org_index = len(self.organisms)
        self.organisms.append(org)
        sex_index = -1
        # Retrieve correct index based on sex
        if org.sex == OrganismSexesEnum.female:
            sex_index = len(self.female_organisms)
            self.female_organisms.append(org)
        elif org.sex == OrganismSexesEnum.male:
            sex_index = len(self.male_organisms)
            self.male_organisms.append(org)
        # Map the organism to its indexes
        self.org_map[org] = (org_index, sex_index)

    def kill_organism(self, organism: Organism):
        """ Kill the given organism in the datastore

        This function should be used whenever you want to kill an organism.
        It makes sure that all steps are taken to properly 'kill' the organism.
        """
        if not self.organisms:
            # Catch on no organisms
            return
        # Add organism to dead organism list
        self.dead_organisms.append(organism)
        # Remove the organism from the organisms list.
        # Removes happen by switching the organism with the last organism of
        # the list. This greatly speeds up the removal to O(1) instead of O(n).
        # The last element of a list can be removed in O(1) while for a random
        # element all following elements need to be shifted one place to the left.
        to_kill_i, to_kill_s_i = self.org_map[organism]

        last_org = self.organisms.pop()
        if organism != last_org:
            self.organisms[to_kill_i] = last_org
            # Update indexes of moved organism
            self.org_map[last_org] = (to_kill_i, self.org_map[last_org][1])

        # Delete organism from correct sex list
        if organism.sex == OrganismSexesEnum.female:
            last_f_org = self.female_organisms.pop()
            if organism != last_f_org:
                self.female_organisms[to_kill_s_i] = last_f_org
                self.org_map[last_f_org] = (
                    self.org_map[last_f_org][0], to_kill_s_i)
        elif organism.sex == OrganismSexesEnum.male:
            last_m_org = self.male_organisms.pop()
            if organism != last_m_org:
                self.male_organisms[to_kill_s_i] = last_m_org
                self.org_map[last_m_org] = (
                    self.org_map[last_m_org][0], to_kill_s_i)

        self.org_map.pop(organism)

    def printOrganisms(self):
        for org in self.organisms:
            print(str(org.id) + "; age: " + str(org.age) +
                  "; gender: " + str(org.sex.name))
