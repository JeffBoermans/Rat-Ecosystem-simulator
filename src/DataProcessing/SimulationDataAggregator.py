from typing import Dict

from ..Logic.DataStore import DataStore


class SimulationDataAggregator(object):
    """This class provides functions to extract useful information from
    a simulation's datastore. Its primary purpose is to format the
    generated results in such a way that they can immediately be persisted
    into output files.
    """
    def aggregateOrganisms(self, datastore: DataStore) -> dict:
        """Aggregate the data on organisms part of the simulation.

        :param datastore: The datastore to extract the to aggregate data from
        :return: The aggregated data
        """
        # Setup
        output_json: dict = dict()
        populations: Dict[str: int] = dict()

        # Aggregate output
        for organism in datastore.organisms:
            populations[organism.name] = populations.get(organism.name, 0) + 1

        # Prepare output
        output_json["populations"] = populations

        return output_json

    def aggregateVegetation(self, datastore: DataStore) -> dict:
        """Aggregate the data on vegetation part of the simulation.

        :param datastore: The datastore to extract the to aggregate data from
        :return: The aggregated data
        """
        # Setup
        output_json: dict = dict()
        populations: Dict[str: int] = dict()

        # Aggregate output
        for vegetaion in datastore.vegetation:
            populations[vegetaion.name] = populations.get(vegetaion.name, 0) + 1

        # Prepare output
        output_json["populations"] = populations

        return output_json
