import json

from ..Logic.DataStore import DataStore
from ..Logic.Entities.organism import Organism
from ..Logic.Entities.vegetation import Vegetation

from src.DataProcessing.ExceptionHandler import InputException

class SimulationDataLoader(object):
    """This class loads input information into a simulation's datastore.
    """
    def load(self, datastore: DataStore, input_path: str) -> None:
        """Populate the datastore with the contents of the designated session file.

        :param datastore: The data store to populate
        :param input_path: The path to the input file
        """

        # Setup
        f = open(input_path, "r")
        data = json.load(f)

        # Input Validation
        food_chain_preys = data["food-chain-preys"]

        # All keys are organisms, All non-keys are vegetation
        organisms = [entity_name for entity_name in food_chain_preys]
        vegetation = []

        # Populate Data Store
        e_id = 0
        for organism in data['organisms']:
            if organism["name"] in organisms:
                organisms.remove(organism["name"])
            datastore.organisms.append(Organism(organism["name"], organism["age"], e_id))
            e_id += 1
        v_id = 0
        for vegetation in data['vegetation']:
            if vegetation["name"] in organisms:
                raise InputException(f"{input_path}: Vegetation detected as prey in the food-chain!")
            datastore.vegetation.append(Vegetation(vegetation["name"], vegetation["age"], v_id))
            v_id += 1
        if len(organisms) != 0:
            raise InputException(f"{input_path}: Uninitialized organism detected in the food-chain!")
        datastore.foodChain = food_chain_preys
        #TODO: Can an organism be its own prey?




