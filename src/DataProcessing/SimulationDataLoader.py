import json

from ..Logic.DataStore import DataStore
from ..Logic.Entities.organism import Organism
from ..Logic.Entities.vegetation import Vegetation


class SimulationDataLoader(object):
    """This class loads input information into a simulation's datastore.
    """
    def load(self, datastore: DataStore, input_path: str) -> None:
        """Populate the datastore with the contents of the designated session file.

        :param datastore: The data store to populate
        :param input_path: The path to the input file
        """
        f = open(input_path, "r")
        data = json.load(f)
        e_id = 0
        for organism in data['organisms']:
            datastore.organisms.append(Organism(organism["name"], organism["age"], e_id))
            e_id += 1
        v_id = 0
        for vegetation in data['vegetation']:
            datastore.vegetation.append(Vegetation(vegetation["name"], vegetation["age"], v_id))
            v_id += 1
