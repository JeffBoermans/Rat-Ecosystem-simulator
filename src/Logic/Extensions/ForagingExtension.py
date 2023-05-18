import random

from typing import Dict, List, Tuple

from .SimulationExtension import SimulationMortalityExtension
from ..DataStore import DataStore
from ..Entities.entity import Entity
from ..Entities.organism import Organism
from ..Entities.vegetation import MonoVegetationCluster


class ForagingExtension(SimulationMortalityExtension):
    def __init__(self, extension_name: str='foraging') -> None:
        super().__init__(extension_name)
        self.organism_foraging_info: Dict[Organism, Tuple[MonoVegetationCluster, int]] = dict()
        self.cluster_organism_populations: Dict[MonoVegetationCluster, int] = dict()

    def get_cluster_organism_population(self, cluster: MonoVegetationCluster) -> int:
        """Get the organism population for the cluster."""
        return self.cluster_organism_populations.get(cluster, 0)

    def next_day(self, datastore: DataStore) -> None:
        # No food clusters, no foraging possible
        if len(datastore.vegetation) == 0:
            return

        daily_energy_upkeep: int = 1
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
            # TODO REMOVE HARDCODED LIMIT
            # TODO REMOVE HARDCODED LIMIT
            # TODO REMOVE HARDCODED LIMIT
            surplus_energy_hardcap: int = 365
            to_forage_energy: int = 1 + (energy <= surplus_energy_hardcap)
            to_forage_energy = cluster.forage_energy(to_forage_energy)
            new_info = (cluster, max(0, energy + to_forage_energy - daily_energy_upkeep))
            self.organism_foraging_info[organism] = new_info

    def notify_organism_death(self, organism: Organism) -> None:
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
