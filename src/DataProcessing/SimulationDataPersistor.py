import json
import os

from ..Logic.DataStore import DataStore
from .SimulationDataAggregator import SimulationDataAggregator


class SimulationDataPersistor(object):
    """This class extracts useful information from a simulation's
    datastore and then persists it into an output file.
    """
    def persist(self, datastore: DataStore, output_path: str) -> None:
        """Aggregate the simulation data and persist it to an output file.

        :param datastore: The data store to persist
        :param output_path: The file to persist aggregated results to
        """
        output_dir: str = os.path.dirname(output_path)
        assert os.path.isdir(output_dir), "The output directory does not exist"

        # Setup
        aggregator: SimulationDataAggregator = SimulationDataAggregator()
        output: dict = dict()

        # Generate output
        output["organisms"] = aggregator.aggregateOrganisms(datastore)
        output["vegetation"] = aggregator.aggregateVegetation(datastore)

        # Persist results
        with open(output_path, "w") as of:
            json.dump(output, of, indent=2, separators=(',', ': '))
