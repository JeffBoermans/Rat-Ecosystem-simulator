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

        # cluster: MonoVegetationCluster, energy_level: int , time_at_cluster: int
        self.organism_foraging_info: Dict[Organism, Tuple[MonoVegetationCluster, int, int]] = dict()
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
                energy = organism.organismInfo.get_extension_property(self.PROP_ORG_DAILY_ENERGY_CONSUMPTION)
                time_at_cluster = 0
                self.organism_foraging_info[organism] = (cluster, energy, 0)
                self._incr_cluster_organism_count(cluster)
            # Organism is on cluster, get its foraging info
            else:
                cluster, energy, time_at_cluster = self.organism_foraging_info[organism]

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
            # Energy logic
            satiation_hardcap: int = energy_stockpile_days * daily_consumption
            room_in_stomach: int = satiation_hardcap - energy # The amount of energy the organism can still stockpile
            to_forage_energy: int = daily_consumption + min(forage_amount, room_in_stomach)
            foraged_energy: int = cluster.forage_energy(to_forage_energy)
            new_energy: int = max(0, energy + foraged_energy - daily_consumption)

            # Cluster logic
            new_cluster = cluster
            new_cluster_suggestion = self._try_changing_cluster(organism, datastore)
            if new_cluster_suggestion != None and new_cluster_suggestion != cluster:
                new_cluster = new_cluster_suggestion
                self._incr_cluster_organism_count(new_cluster)
                self._decr_cluster_organism_count(cluster)
                time_at_cluster = -1

            # Store results
            new_info = (new_cluster, new_energy, time_at_cluster + 1)
            self.organism_foraging_info[organism] = new_info

    def notify_organism_death(self, organism: Organism) -> None:
        if organism in self.organism_foraging_info:
            foraging_info = self.organism_foraging_info.pop(organism)
            cluster = foraging_info[0]
            self._decr_cluster_organism_count(cluster)

    def should_die(self, organism: Entity, datastore: DataStore, log: List[str]) -> bool:
        if not isinstance(organism, Organism):
            return False

        foraging_info = self.organism_foraging_info.get(organism, None)
        if foraging_info is None:
            return False

        should_die: bool = foraging_info[1] <= 0

        if should_die:
            log.append(f"{organism.name} {organism.id} starved to death (Age: {organism.age})")

        return should_die

    def _try_changing_cluster(self, organism: Organism, datastore: DataStore) -> Union[MonoVegetationCluster, None]:
        """Suggest a new cluster to change to based on current foraging information.
        
        :param organism: The organism to consider a cluster change for
        :param datastore: The simulation data store to base the decision off of
        :return: The new cluster if change suggested. None if no change suggested
        """

        if len(datastore.vegetation) == 0:
            return None

        # Do MVT: Should organism change cluster?
        should_change_cluster: bool = self._MVT(organism, datastore)

        if not should_change_cluster:
            return None

        # Do IFD specific logic
        new_cluster: MonoVegetationCluster = self._IFD(organism, datastore)

        return new_cluster


    def _IFD(self, organism: Organism, datastore: DataStore) -> MonoVegetationCluster:
        """Choose a new cluster for the organism based on the Ideal Free Distribution model.
        
        The term cluster is analogous to the term food patch. The quality of a food patch
        is measured in the amount of energy the cluster contains.

        reference: [IFD wikipedia](https://en.wikipedia.org/wiki/Ideal_free_distribution)

        The IFD assumptions map to implementation details as follows:
            1) Each available patch has an individual quality that is determined by the amount of resources available in each patch. Given that there is not yet any competition in each patch, individuals can assess the quality of each patch based merely on the resources available.
                &rarr; patch qualty = cluster energy amount, the energy amount is always accessible even if competition 

            2) Individuals are free to move to the highest quality patch. However, this can be violated by dominant individuals within a species who may keep a weaker individual from reaching the ideal patch.
                &rarr; movement is free, no distinction is made between organism capabilities

            3) Individuals are aware of the value of each patch so that they can choose the ideal patch.
                &rarr; cluster energy amount is freely available
            
            4) Increasing the number of individuals in a given patch reduces the quality of that patch, through either increased scramble competition or increased interference competition.
                &rarr; this will be taken into account in this method

            5) All individuals are competitively equal, so they are all equally able to forage and choose the ideal patch.
                &rarr; no distinction is made between organism capabilities
            
        :param organism: The organism to consider a cluster change for
        :param datastore: The simulation data store to base the decision off of
        :return: The new (possibly the same as currently) clust for the organism
        to move to
        """
        organism_daily_consumption: int = organism.organismInfo.get_extension_property(self.PROP_ORG_DAILY_ENERGY_CONSUMPTION)
        clusters_by_quality = [
            (cluster, cluster.energy_amount - organism_daily_consumption * cluster.population()[1])
            for cluster in datastore.vegetation
        ]

        best_cluster_by_quality = max(clusters_by_quality, key=lambda x: x[1])

        return best_cluster_by_quality[0]

    def _MVT(self, organism: Organism, datastore: DataStore) -> bool:
        return self.organism_foraging_info[organism][2] >=  5

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
