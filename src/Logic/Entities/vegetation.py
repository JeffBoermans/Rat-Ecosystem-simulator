from typing import Tuple, Any, Dict, Union
from statistics import NormalDist
from numpy import random as np_random

from src.Logic.Entities.entity import Entity
from ...utils import centered_normal_dist


class Vegetation(Entity):
    """A plant"""
    def __init__(self, species: str, age: int, id: int, **kwargs):
        """
        :param species: The species of the vegetation
        :param age: The age of the vegetation
        :param id: The unique identifier of the vegetation
        """
        super(Vegetation, self).__init__(species, age, id)
        self.extension_properties: Dict[str, Any] = { **kwargs }
        """Any non-required or expected organism info properties get stored for use by extensions."""

    def get_extension_property(self, property_name: str) -> Union[Any, None]:
        """Get the value of an extension property.
        
        :return: The property value, None if the property does not exist
        """
        return self.extension_properties.get(property_name, None)

    def __repr__(self) -> str:
        return f"{self.name} | {self.age} Age | {self.id} ID"


class MonoVegetationCluster(Vegetation):
    """A homogenous cluster of plants that follow an undefined life/growth cycle.
    """
    def __init__(self, species: str, age: int, id: int, energy_yield: int, maturity_age_range: Tuple[int, int], **kwargs) -> None:
        """
        :param energy_yield: The amount of energy that a single plant in the cluster yields
        :param maturity_age_range: The age range in days between which the vegetation normally reaches maturation
        """
        super(MonoVegetationCluster, self).__init__(species, age, id, **kwargs)
        self._crop_energy_yield: int = energy_yield
        """The fixed energy yield for a single crop once it reaches maturity"""
        self._energy_amount: int = 0
        """The amount of energy that is currently available in this cluster to any organisms"""
        self._maturity_dist: NormalDist = centered_normal_dist(maturity_age_range, 4.0)
        """The age range in days when the plant typically reaches maturity"""

    @property
    def energy_amount(self):
        return self._energy_amount
    
    def add_energy(self, amount: int) -> None:
        assert amount >= 0, f"Cannot add negative amount of energy to cluster: {amount}"
        self._energy_amount += amount

    def forage_energy(self, amount) -> int:
        """Forage at most the specified amount of energy from the vegetation cluster.
        
        The foraged energy is subtracted from the cluster's energy amount.

        :param amount: The amount of energy to forage
        :return: The foraged amount of energy
        """
        remaining_energy: int = max(0, self.energy_amount - amount)
        foraged_energy = self.energy_amount - remaining_energy
        self._energy_amount = remaining_energy
        return foraged_energy

    def next_day(self) -> None:
        """Make a single time step pass for the vegetation cluster."""
        raise NotImplementedError("The derived cluster should implement this method")

    def repopulate(self, day: int) -> None:
        """Make the cluster repopulate, expanding the population of plants in the
        cluster based on the current population.

        :param day: The current day in the year in the simulation
        """
        raise NotImplementedError("The derived cluster should implement this method")

    def population(self) -> Tuple[str, int]:
        """Get the (species, population count) tuple for the cluster."""
        raise NotImplementedError("The derived cluster should implement this method")

    def __repr__(self) -> str:
        return f"{self._energy_amount} Energy | {self._crop_energy_yield} Yield | " + super().__repr__()


class AnnualVegetationCluster(MonoVegetationCluster):
    """A homogenous cluster of plants that follow an annual life/growth cycle.
    
    Plants with an annual life cycle do not survive past their first
    growing season.
    """
    def __init__(self, species: str, age: int, id: int, amount: int, energy_yield: int, maturity_age_range: Tuple[int, int], **kwargs) -> None:
        """
        :param species: The species of the vegetation
        :param age: The initial age of the vegetation in days
        :param id: The unique identifier of the vegetation
        :param amount: The initial amount of plants of the specified species part of this cluster
        :param energy_yield: The amount of energy that a single plant in the cluster yields
        :param maturity_age_range: The age range in days between which the vegetation normally reaches maturation
        """
        super(AnnualVegetationCluster, self).__init__(species=species, age=age, id=id,
                                                      energy_yield=energy_yield, maturity_age_range=maturity_age_range,
                                                      **kwargs)
        self.mature_amount: int = 0
        """The amount of mature plants of the specified species in this cluster"""
        self.immature_amount: int = amount
        """The amount of plants that are either seedlings or still before the maturity stage in their growth cycle"""

    def next_day(self) -> None:
        """Make a single time step pass for the vegetation cluster.
        """
        # Handle time logic
        self.age += 1
        # Maturation logic
        matured_count: int = self._should_mature_amount()
        self.mature_amount += matured_count
        self.add_energy(matured_count * self._crop_energy_yield)
        self.immature_amount -= matured_count

    def repopulate(self, day: int) -> None:
        if (day % 365) == 0:
            self.immature_amount = self.mature_amount
            self.mature_amount = 0
            self.age = 0

    def population(self) -> Tuple[str, int]:
        return self.name, self.mature_amount + self.immature_amount

    def _should_mature_amount(self) -> int:
        """Stochastically choose a number x plants in the current cluster that should mature.

        Because a cluster implicitly represents a number of plants, output a number of
        plants that should mature instead of a list of plants that should mature.

        :return: The number of plants that should mature
        """
        # The probability of an individual having reached maturity before its current age
        prob_of_mature_before_age = self._maturity_dist.cdf(self.age)
        
        # A binomial distribution maps the number of successes for n disconnected
        # trials to the probability of those n successes
        # ==> Choose a sample from an inverse binomial distribution based on the
        #   current age of the cluster vegetation and the maturity normal distribution
        return np_random.binomial(n=self.immature_amount, p=prob_of_mature_before_age)

    def __repr__(self) -> str:
        return f"{self.mature_amount} Mature | {self.immature_amount} Immature | " + super().__repr__()
