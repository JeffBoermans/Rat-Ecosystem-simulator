import random

from typing import Any, Dict, List, Tuple, Union

from .SimulationExtension import SimulationMortalityExtension
from ..DataStore import DataStore
from ..Entities.entity import Entity
from ..Entities.organism import Organism
from ..Entities.vegetation import MonoVegetationCluster
from ..exceptions import MissingOrganismProperty, MissingVegetationProperty


class ForagingExtension(SimulationMortalityExtension):
    def __init__(self, extension_name: str='foraging') -> None:
        super().__init__(extension_name)
        self.organism_foraging_info: Dict[Organism, Tuple[MonoVegetationCluster, int]] = dict()
        self.cluster_organism_populations: Dict[MonoVegetationCluster, int] = dict()

        # Extension input properties
        self.PROP_ORG_DAILY_ENERGY_CONSUMPTION   = "daily-energy-consumption"
        self.PROP_ORG_ENERGY_FORAGING_AMOUNT     = "energy-foraging-amount"
        self.PROP_ORG_DAYS_ENERGY_STOCKPILE_MAX  = "days-energy-stockpile-max"
        self.PROP_VEG_FORAGING_DIFFICULTY_FACTOR = "foraging-difficulty-factor"

    def get_cluster_organism_population(self, cluster: MonoVegetationCluster) -> int:
        """Get the organism population for the cluster."""
        return self.cluster_organism_populations.get(cluster, 0)

    def next_day(self, datastore: DataStore) -> None:
        # No food clusters, no foraging possible
        if len(datastore.vegetation) == 0:
            return

        for organism in datastore.organisms:
            # Add organism to cluster
            if organism not in self.organism_foraging_info:
                cluster = random.choice(datastore.vegetation)
                energy = 0
                self.organism_foraging_info[organism] = (cluster, energy)
                self._incr_cluster_organism_count(cluster)
            # Organism is on cluster, get its foraging info
            else:
                cluster, energy = self.organism_foraging_info[organism]

            daily_consumption: int | None = organism.organismInfo.get_extension_property(self.PROP_ORG_DAILY_ENERGY_CONSUMPTION)
            forage_amount: int | None = organism.organismInfo.get_extension_property(self.PROP_ORG_ENERGY_FORAGING_AMOUNT)
            # The amount of days worth of energy upkeep the organism is
            # allowed to stockpile
            energy_stockpile_days: int | None = organism.organismInfo.get_extension_property(self.PROP_ORG_DAYS_ENERGY_STOCKPILE_MAX)
            if daily_consumption is None:
                raise MissingOrganismProperty(f"An organism's organism info is missing a required extension key: {self.PROP_ORG_DAILY_ENERGY_CONSUMPTION}")
            if forage_amount is None:
                raise MissingOrganismProperty(f"An organism's organism info is missing a required extension key: {self.PROP_ORG_ENERGY_FORAGING_AMOUNT}")
            if energy_stockpile_days is None:
                raise MissingOrganismProperty(f"An organism's organism info is missing a required extension key: {self.PROP_ORG_DAYS_ENERGY_STOCKPILE_MAX}")
            satiation_hardcap: int = energy_stockpile_days * daily_consumption
            room_in_stomach: int = satiation_hardcap - energy # The amount of energy the organism can still stockpile
            to_forage_energy: int = daily_consumption + min(forage_amount, room_in_stomach)
            foraged_energy = cluster.forage_energy(to_forage_energy)
            new_info = (cluster, max(0, energy + foraged_energy - daily_consumption))
            self.organism_foraging_info[organism] = new_info

    def notify_organism_death(self, organism: Organism) -> None:
        if organism in self.organism_foraging_info:
            cluster, _ = self.organism_foraging_info.pop(organism)
            self._decr_cluster_organism_count(cluster)

    def should_die(self, organism: Entity, datastore: DataStore, log: List[str]) -> bool:
        if not isinstance(organism, Organism):
            return False

        foraging_info = self.organism_foraging_info.get(organism, None)
        if foraging_info is None:
            return False

        should_die: bool = foraging_info[1] <= 0

        if should_die:
            log.append(f"{organism.name} died at age {organism.age} to starvation with {foraging_info[1]} energy remaining")

        return should_die

    def _incr_cluster_organism_count(self, cluster: MonoVegetationCluster) -> None:
        """Increment the cluster's organism count and set it to 1 if it does not have an organism count associated with it."""
        self.cluster_organism_populations[cluster] = self.cluster_organism_populations.get(cluster, 0) + 1

    def _decr_cluster_organism_count(self, cluster: MonoVegetationCluster) -> None:
        """Decrement the cluster's organism count iff. the cluster has an organism count associated with it."""
        stored_value = self.cluster_organism_populations.get(cluster, None)
        if stored_value is None:
            return
        # Intentionally let value reach invalid range if bug
        self.cluster_organism_populations[cluster] -= 1
