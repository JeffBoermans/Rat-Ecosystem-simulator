import random

from statistics import NormalDist
from enum import Enum
from typing import List

from .entity import Entity
from .organism_info import OrganismInfo
from ...utils import centered_normal_dist


class OrganismSexesEnum(Enum):
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
        return [e.value for e in OrganismSexesEnum]


class Organism(Entity):
    """A living creature"""
    def __init__(self, e_name: str, e_age: int, e_id: int, e_sex: OrganismSexesEnum, e_info: OrganismInfo):
        """
        :param e_name: The name of the organism's species
        :param e_age: The age of the organism, in Simulation timesteps
        :param e_id: The unique identifier of the organism
        :param e_sex: The sex of the organism
        :param e_info: Species specific organism information
        """
        super().__init__(e_name, e_age*365, e_id)
        # Organism specific properties
        self.sex: OrganismSexesEnum = e_sex
        # Species specific properties
        self.organismInfo: OrganismInfo = e_info
        self.breedingTerm = -1
        self.fertile = True

        self.natural_mortality_dist: NormalDist = centered_normal_dist(self.organismInfo.lifespan, 4.0)
        self.menopause_dist: NormalDist = centered_normal_dist(self.organismInfo.menopause, 4.0)

    def should_die_naturally(self) -> bool:
        # The probability of the organism having died before its current age
        prob_of_death_before_age = self.natural_mortality_dist.cdf(self.age)
        # The random.random function draws form a normally distributed range [0, 1]
        return random.random() < prob_of_death_before_age

    def should_enter_menopause(self) -> bool:
        # The probability of the organism having reached menopause at its current age
        prob_of_having_reached_menopause = self.menopause_dist.cdf(self.age)
        # The random.random function draws form a normally distributed range [0, 1]
        return random.random() < prob_of_having_reached_menopause
