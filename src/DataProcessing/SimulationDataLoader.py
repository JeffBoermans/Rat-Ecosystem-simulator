import json

from ..Logic.DataStore import DataStore
from ..Logic.Entities.organism import Organism, OrganismInfo, OrganismSexesEnum
from ..Logic.Entities.vegetation import Vegetation
from .exceptions import InputException, MissingInputKey, WrongInputFile


class SimulationDataLoader(object):
    """This class loads input information into a simulation's datastore.
    """

    def load(self, datastore: DataStore, input_path: str) -> None:
        """Populate the datastore with the contents of the designated session file.

        :param datastore: The data store to populate
        :param input_path: The path to the input file
        """

        # Input Validation; check if the input file is a .json file
        if not input_path.lower().endswith(".json"):
            raise WrongInputFile(f"The provided input file '{input_path}' is not a .json file.")


        # Setup
        f = open(input_path, "r")
        data = json.load(f)

        # Input Validation; check if the input file is valid
        required_keys = ['organisms', 'vegetation', 'food-chain-preys']
        missing_key: str | None = next((req_key for req_key in required_keys if req_key not in data), None)
        if missing_key is not None:
            raise MissingInputKey(f"{input_path}: A required top-level key is missing from the session file: {missing_key}")

        try:
            food_chain_preys = data["food-chain-preys"]
        except KeyError:
            raise InputException("No food-chain  was specified!")
        try:
            organism_info = data["organism-characteristics"]
        except KeyError:
            raise InputException("No organism characteristics were specified!")
        data_organism_info = None

        # All keys are organisms, All non-keys are vegetation
        organisms = [entity_name for entity_name in food_chain_preys]
        vegetations = []

        # Populate Data Store
        allowed_sexes_values = OrganismSexesEnum.values()
        for e_id, organism in enumerate(data['organisms']):
            name = organism["name"]
            if name in organisms:
                organisms.remove(name)
            try:
                if data_organism_info is None:
                    data_organism_info = OrganismInfo(
                        o_m = 8 * int(organism_info[0][name]["sexual-maturity-weeks"]),
                        o_b = 8 * int(organism_info[0][name]["breeding-age-weeks"]),
                        o_ls = organism_info[0][name]["life-span-months"],
                        o_mpa = organism_info[0][name]["menopause-age-months"]
                    )
                for item in food_chain_preys[name]:
                    if item not in vegetations:
                        vegetations.append(item)
                assert isinstance(name, str)
                assert isinstance(organism["age"], int)
                assert len(organism["sex"]) == 1 #Check if char
                assert organism["sex"] in allowed_sexes_values, f"Unknown sex value: {organism['sex']}"
            except KeyError:
                raise InputException(f"{input_path}: Wrong typing used when specifying an organism!")
            except AssertionError as e:
                raise InputException(f"{input_path}: A '{organism['name']}' was not configured correctly: {e}")
            datastore.organisms.append(Organism(organism["name"], organism["age"], e_id, OrganismSexesEnum(organism["sex"]),
                                                data_organism_info))
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
        a = 3