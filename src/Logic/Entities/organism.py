import random

from statistics import NormalDist
from enum import Enum
from typing import List

from .entity import Entity
from .organism_info import OrganismInfo


class OrgamnismSexesEnum(Enum):
    """An enumerator for the possible sex of an organism.
    """
    male = "m"
    female = "f"
    other = "o"

    @staticmethod
    def values() -> List[str]:
        """The list of possible sex values.

        This is the list of enum values that the constructor
        of the enum allows.
        """
        return [e.value for e in OrgamnismSexesEnum]


class Organism(Entity):
    """A living creature"""
    def __init__(self, e_name: str, e_age: int, e_id: int, e_sex: OrgamnismSexesEnum, e_info: OrganismInfo):
        """
        :param e_name: The name of the organism's species
        :param e_age: The age of the organism, in Simulation timesteps
        :param e_id: The unique identifier of the organism
        :param e_sex: The sex of the organism
        :param e_info: Species specific organism information
        """
        super().__init__(e_name, e_age, e_id)
        # Organism specific properties
        self.sex: OrgamnismSexesEnum = e_sex
        # Species specific properties
        self.organismInfo: OrganismInfo = e_info

        life_span_range: int = self.organismInfo.lifespan[1] - self.organismInfo.lifespan[0]
        life_span_range_half: int = life_span_range / 2
        life_span_mean: int = self.organismInfo.lifespan[0] + life_span_range_half
        self.natural_mortality_dist: NormalDist = NormalDist(mu=life_span_mean, sigma=life_span_range_half)

    def should_die_naturally(self) -> bool:
        # The probability of the organism reaching reaching its current age
        prob_of_reaching_age = self.natural_mortality_dist.cdf(self.age)
        # The random.random function draws form a normally distributed range [0, 1]
        return random.random() < prob_of_reaching_age
