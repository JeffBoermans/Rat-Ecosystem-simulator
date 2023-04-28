import json

from ..Logic.DataStore import DataStore
from ..Logic.Entities.organism import Organism
from ..Logic.Entities.vegetation import Vegetation
from .exceptions import InputException, MissingInputKey


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
        required_keys = ['organisms', 'vegetation', 'food-chain-preys']
        missing_key: str | None = next((req_key for req_key in required_keys if req_key not in data), None)
        if missing_key is not None:
            raise MissingInputKey(f"{input_path}: A required top-level key is missing from the session file: {missing_key}")

        food_chain_preys = data["food-chain-preys"]

        # All keys are organisms, All non-keys are vegetation
        organisms = [entity_name for entity_name in food_chain_preys]
        vegetations = []

        # Populate Data Store
        e_id = 0
        for organism in data['organisms']:
            name = organism["name"]
            if name in organisms:
                organisms.remove(name)
            try:
                for item in food_chain_preys[name]:
                    if item not in vegetations:
                        vegetations.append(item)
                assert isinstance(name, str)
                assert isinstance(organism["age"], int)
            except KeyError:
                raise InputException(f"{input_path}: Wrong typing used when specifying an organism!")
            except AssertionError:
                raise InputException(f"{input_path}: '{organism['name']}' was not found present in the food-chain!")

            datastore.organisms.append(Organism(organism["name"], organism["age"], e_id))
            e_id += 1
        v_id = 0
        for vegetation in data['vegetation']:
            if vegetation["name"] in organisms:
                raise InputException(f"{input_path}: Vegetation detected as prey in the food-chain!")
            if vegetation["name"] in vegetations:
                vegetations.remove(vegetation["name"])
            datastore.vegetation.append(Vegetation(vegetation["name"], vegetation["age"], v_id))
            v_id += 1
        if len(organisms) != 0:
            raise InputException(f"{input_path}: Uninitialized organism detected in the food-chain!")
        if len(vegetations) != 0:
            raise InputException(f"{input_path}: Uninitialized vegetation detected in food-chain!")
        datastore.foodChain = food_chain_preys
