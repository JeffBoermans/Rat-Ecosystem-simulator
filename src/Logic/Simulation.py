import random

from typing import List

from .DataStore import DataStore
from ..DataProcessing.SimulationDataPersistor import SimulationDataPersistor
from ..DataProcessing.SimulationDataLoader import SimulationDataLoader
from ..DataProcessing.exceptions import *
from .exceptions import DuplicateExtension
from ..Logic.Entities.organism import Organism, OrganismSexesEnum
from .Extensions.SimulationExtension import SimulationMortalityExtension


class Simulation(object):
    def __init__(self, s_path: str) -> None:
        self.dataStore: DataStore = DataStore(s_path)

        self._sim_day = 0

        # The active list of mortality extensions, which are consulted
        # periodically to cull the entity populations
        self.mortality_extensions: List[SimulationMortalityExtension] = []

    def run(self, days: int = 0):
        """Run the simulation.
        This is the entry point of the simulation.
        """
        self._load()
        for _ in range(days):
            self.simulate()
        self.dataStore.printOrganisms()
        # print(self.dataStore.organisms[0].organismInfo.lifespan)

    def persist(self, output_path: str) -> None:
        """Persist the contents and results of the simulation to an output file.

        :param output_path: The path to write the output to
        """
        aggregator: SimulationDataPersistor = SimulationDataPersistor()
        aggregator.persist(self.dataStore, output_path)

    def register_mortality_extension(self, extension: SimulationMortalityExtension):
        """Register the mortality extension instance with the simulation.

        Duplicate extensions raise an exception, only one extension with the same name may
        exist in the simulation at a time.

        :param extension: The extension to register
        """
        if extension.name in (ext.name for ext in self.mortality_extensions):
            raise DuplicateExtension(f"The mortality extension '{extension.name}' is already registerd")
        self.mortality_extensions.append(extension)

    def organism_count(self):
        """ Get amount of organisms currently alive in simulation
        """
        return len(self.dataStore.organisms)

    def day(self):
        return self._sim_day

    def _load(self):
        """Populate the simulation from an input file.
        """
        loader: SimulationDataLoader = SimulationDataLoader()
        loader.load(self.dataStore, self.dataStore.session_path)

    def simulate(self):
        """ Simulate a day in the current ecosystem.
        """

        self._nextday()
        death_log = self._mortality()
        self._reproduction()
        birth_log = self._nativity()
        logs = death_log + birth_log
        random.shuffle(logs)
        return logs

    def _reproduction(self):
        # First: Put Females into Menopause
        for org in self.dataStore.organisms:
            if org.sex.name == "female" and org.fertile:
                if org.should_enter_menopause():
                    org.fertile = False

        # Second: Check for 1 sexually mature Male
        smm_flag: bool = False
        for org in self.dataStore.organisms:
            if org.sex.name == "male" and org.age >= org.organismInfo.maturity:
                smm_flag = True
        if not smm_flag:
            return

        # Third: Impregnate all sexually mature Females
        for org in self.dataStore.organisms:
            if org.sex.name == "female" and org.breedingTerm == -1 and \
                    org.organismInfo.maturity <= org.age and org.fertile:
                # Female gets impregnated
                org.breedingTerm = org.age
                print("Female impregnated.")

    def _int_to_sex(self, sex_int: int) -> str:
        if sex_int == 0:
            return 'm'
        elif sex_int == 1:
            return 'f'
        else:
            raise Exception("Gender Error.")

    def _nativity(self):
        log = []
        babies: list[Organism] = []
        last_id: int = self.dataStore.organisms[-1].id
        for org in self.dataStore.organisms:
            if org.sex.name == "female" and org.breedingTerm != -1:
                days_pregnant: int = org.age - org.breedingTerm
                breeding_time: int = org.organismInfo.breeding
                if days_pregnant > breeding_time:
                    raise Exception("Pregnant female exceeded breeding time.")
                elif days_pregnant == breeding_time:
                    # Birth occurs
                    print("Birth")
                    org.breedingTerm = -1
                    last_id += 1
                    sex_int: int = random.randint(0, 1)  # 0:male, 1:female
                    sex: str = self._int_to_sex(sex_int)
                    sex_enum: OrganismSexesEnum = OrganismSexesEnum(sex)

                    new_baby = Organism(
                        org.name, 0, last_id, sex_enum, org.organismInfo)
                    log.append(f"{new_baby.name} {new_baby.id} is born.")
                    babies.append(new_baby)

        for baby in babies:
            self.dataStore.organisms.append(baby)
        return log

    def _mortality(self):
        log = []
        updated_organisms = []
        for org in self.dataStore.organisms:
            if org.should_die_naturally():
                log.append(f"{org.name} {org.id} died at age {org.age}.")
                print(str(org.id) + " died.")
                org.alive = False
                self.dataStore.death_organisms.append(org)
            else:
                updated_organisms.append(org)
        self.dataStore.organisms = updated_organisms
        return log

    def _nextday(self):
        self._sim_day += 1
        for org in self.dataStore.organisms:
            if org.alive:
                org.age += 1
