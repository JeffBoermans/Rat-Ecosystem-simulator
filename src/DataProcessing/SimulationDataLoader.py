import json
from typing import Dict

from ..Logic.DataStore import DataStore
from ..Logic.Entities.organism import Organism, OrganismInfo, OrganismSexesEnum
from ..Logic.Entities.vegetation import AnnualVegetationCluster, Vegetation
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
            raise WrongInputFile(
                f"The provided input file '{input_path}' is not a .json file.")

        # Setup
        with open(input_path, "r") as f:
            data = json.load(f)

            # Input Validation; check if the input file is valid
            required_keys = ['organisms', 'vegetation', 'food-chain-preys',
                             'organism-characteristics', 'vegetation-characteristics']
            missing_key: str | None = next(
                (req_key for req_key in required_keys if req_key not in data), None)
            if missing_key is not None:
                raise MissingInputKey(
                    f"{input_path}: A required top-level key is missing from the session file: {missing_key}")

            food_chain_preys = data.get("food-chain-preys", None)
            organism_characteristics: dict = data.get(
                "organism-characteristics", None)
            vegetation_characteristics: dict = data.get(
                "vegetation-characteristics", None)

            required_organism_char_keys = {
                "sexual-maturity-weeks", "breeding-age-weeks", "life-span-months", "menopause-age-months"}
            required_vegetation_char_keys = {
                "energy-yield", "maturity-age-days"}

            assert isinstance(
                food_chain_preys, dict), "The food chain preys key must have a dictionary value"
            assert isinstance(organism_characteristics,
                              dict), "The organism characteristics key must have a dictionary value"
            assert isinstance(vegetation_characteristics,
                              dict), "The vegetation characteristics key must have a dictionary value"

            organism_info_mapping: Dict[str, OrganismInfo] = dict()
            try:
                organism_info_mapping = dict()
                # Map each organism species to an object instance that keeps
                # track of the species-specific data
                for organism_name in organism_characteristics.keys():
                    species_characteristics: dict = organism_characteristics[organism_name]
                    non_required_characteristics = {
                        key: species_characteristics[key]
                        for key in species_characteristics.keys()
                        if key not in required_organism_char_keys
                    }

                    non_required_characteristics = self.get_trimmed_dict(
                        species_characteristics, required_organism_char_keys)
                    organism_info_mapping[organism_name] = OrganismInfo(
                        o_m=7 *
                        int(species_characteristics["sexual-maturity-weeks"]),
                        o_b=7 *
                        int(species_characteristics["breeding-age-weeks"]),
                        o_ls=species_characteristics["life-span-months"],
                        o_mpa=species_characteristics["menopause-age-months"],
                        **non_required_characteristics
                    )

            except KeyError as e:
                raise MissingInputKey(f"Malformed organism info entry: {e}")

            # All keys are organisms, All non-keys are vegetation
            organisms = [entity_name for entity_name in food_chain_preys]
            vegetations = []

            # Populate Data Store
            allowed_sexes_values = OrganismSexesEnum.values()
            for organism in data['organisms']:

                name = organism["name"]
                data_organism_info = organism_info_mapping[name]
                if name in organisms:
                    organisms.remove(name)
                try:
                    for item in food_chain_preys[name]:
                        if item not in vegetations:
                            vegetations.append(item)
                    assert isinstance(name, str)
                    assert isinstance(organism["age"], int)
                    assert len(organism["sex"]) == 1  # Check if char
                    assert organism[
                        "sex"] in allowed_sexes_values, f"Unknown sex value: {organism['sex']}"

                except KeyError:
                    raise InputException(
                        f"{input_path}: Wrong typing used when specifying an organism!")
                except AssertionError as e:
                    raise InputException(
                        f"{input_path}: A '{organism['name']}' was not configured correctly: {e}")

                e_id = datastore.reserve_organism_id()
                datastore.add_organism(Organism(organism["name"], organism["age"], e_id, OrganismSexesEnum(organism["sex"]),
                                                data_organism_info))

            for vegetation in data['vegetation']:
                vegetation_name = vegetation["name"]
                try:
                    assert "name" in vegetation, "name"
                    assert "age" in vegetation, "age"
                    assert "amount" in vegetation, "amount"
                except AssertionError as e:
                    raise MissingInputKey(
                        f"Missing required vegetation key: {e}")

                if vegetation_name in organisms:
                    raise InputException(
                        f"{input_path}: Vegetation detected as prey in the food-chain!")
                if vegetation_name in vegetations:
                    vegetations.remove(vegetation["name"])

                vegetation_info = vegetation_characteristics[vegetation_name]
                non_required_characteristics = self.get_trimmed_dict(
                    vegetation_info, required_vegetation_char_keys)

                vegetation_cluster = AnnualVegetationCluster(
                    species=vegetation_name,
                    age=vegetation["age"],
                    amount=vegetation["amount"],
                    energy_yield=vegetation_info["energy-yield"],
                    maturity_age_range=vegetation_info["maturity-age-days"],
                    id=datastore.reserve_vegetation_id(),
                    **non_required_characteristics
                )
                datastore.vegetation.append(vegetation_cluster)

            if len(organisms) != 0:
                raise InputException(
                    f"{input_path}: Uninitialized organism detected in the food-chain: {organisms}")
            if len(vegetations) != 0:
                raise InputException(
                    f"{input_path}: Uninitialized vegetation detected in food-chain: {vegetations}")

            datastore.foodChain = food_chain_preys

    def get_trimmed_dict(self, original: dict, to_trim_keys: list) -> dict:
        """Return a shallow copy of the original dict with all to trim keys removed.

        :param original: The dict to get a trimmed version of
        :param to_trim_keys: The keys to not include in the copy; the keys to trim
        :return: A trimmed shallow copy of the original dict
        """
        return {
            key: original[key]
            for key in original.keys()
            if key not in to_trim_keys
        }
