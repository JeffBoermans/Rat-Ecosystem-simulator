from .DataStore import DataStore
from ..DataProcessing.SimulationDataPersistor import SimulationDataPersistor
from ..DataProcessing.SimulationDataLoader import SimulationDataLoader
from ..DataProcessing.exceptions import *
import random
from ..Logic.Entities.organism import Organism, OrganismSexesEnum


class Simulation(object):
    def __init__(self, s_path: str) -> None:
        self.dataStore: DataStore = DataStore(s_path)

    def run(self, days: int = 0):
        """Run the simulation.
        This is the entry point of the simulation.
        """
        self._load()
        for i in range(days):
            self._simulate()
        self.dataStore.printOrganisms()
        #print(self.dataStore.organisms[0].organismInfo.lifespan)

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

    def _simulate(self):
        """ Simulate a day in the current ecosystem.
        """

        self._nextday()
        self._mortality()
        self._reproduction()
        self._nativity()

    def _reproduction(self):
        # First: Put Females into Menopause
        for org in self.dataStore.organisms:
            if org.sex.name == "female" and org.fertile:
                if org.age > org.organismInfo.menopause[1]:
                    org.fertile = False
                elif org.age >= org.organismInfo.menopause[0]:
                    if random.randint(0, 21) == 1:  # TODO Normale Verdeling
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


    def _int_to_sex(self, sex_int:int) -> str:
        if sex_int == 0:
            return 'm'
        elif sex_int == 1:
            return 'f'
        else:
            raise Exception("Gender Error.")

    def _nativity(self):
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
                    sex_int: int = random.randint(0,1) # 0:male, 1:female
                    sex: str = self._int_to_sex(sex_int)
                    sex_enum: OrganismSexesEnum = OrganismSexesEnum(sex)

                    new_baby = Organism(org.name, 0, last_id, sex_enum, org.organismInfo)
                    babies.append(new_baby)

        for baby in babies:
            self.dataStore.organisms.append(baby)


    def _mortality(self):
        for org in self.dataStore.organisms:
            if org.alive:
                if org.organismInfo.lifespan[1] < org.age:

                    raise InvalidAge(f"Invalid Age of {org.age} days, exceeding lifespan of {org.organismInfo.lifespan[1]} days.")
                elif org.organismInfo.lifespan[1] == org.age:
                    # Organism dies
                    print(str(org.id) + " died.")
                    org.alive = False
                elif org.organismInfo.lifespan[0] <= org.age:
                    if random.randint(0, 42) == 1: # TODO Normale Verdeling
                        print(str(org.id) + " died.")
                        org.alive = False


    def _nextday(self):
        for org in self.dataStore.organisms:
            if org.alive:
                org.age += 1
