from .DataStore import DataStore
from ..DataProcessing.SimulationDataPersistor import SimulationDataPersistor
from ..DataProcessing.SimulationDataLoader import SimulationDataLoader


class Simulation(object):
    def __init__(self, s_path: str) -> None:
        self.dataStore: DataStore = DataStore(s_path)

    def run(self):
        """Run the simulation.
        This is the entry point of the simulation.
        """
        self._load()

    def persist(self, output_path: str) -> None:
        """Persist the contents and results of the simulation to an output file.

        :param output_path: The path to write the output to
        """
        aggregator: SimulationDataPersistor = SimulationDataPersistor()
        aggregator.persist(self.dataStore, output_path)

    def _load(self):
        """Populate the simulation from an input file.
        """
        loader: SimulationDataLoader = SimulationDataLoader()
        loader.load(self.dataStore, self.dataStore.session_path)
