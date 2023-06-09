import random

from typing import List

from .DataStore import DataStore
from ..DataProcessing.SimulationDataPersistor import SimulationDataPersistor
from ..DataProcessing.SimulationDataLoader import SimulationDataLoader
from ..DataProcessing.exceptions import *
from .exceptions import DuplicateExtension
from ..Logic.Entities.organism import Organism, OrganismSexesEnum
from .Extensions.SimulationExtension import SimulationMortalityExtension
from ..utils import Logger


class Simulation(object):
    def __init__(self, s_path: str) -> None:
        self.dataStore: DataStore = DataStore(s_path)

        self._sim_day = 0
        self._logger: Logger = Logger("Output/log.txt")

        self._load()
        # The active list of mortality extensions, which are consulted
        # periodically to cull the entity populations
        self.mortality_extensions: List[SimulationMortalityExtension] = []

    def _load(self):
        """Populate the simulation from an input file.
        """
        loader: SimulationDataLoader = SimulationDataLoader()
        loader.load(self.dataStore, self.dataStore.session_path)
        self._logger.setup(self.dataStore.session_path)

    def run(self, days: int = 0):
        """Run the simulation.
        This is the entry point of the simulation.
        """
        for _ in range(days):
            self.simulate()
        self.dataStore.printOrganisms()

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
            raise DuplicateExtension(
                f"The mortality extension '{extension.name}' is already registerd")
        self.mortality_extensions.append(extension)

    def organism_alive_count(self):
        """ Get amount of organisms currently alive in simulation
        """
        return len(self.dataStore.organisms)

    def male_female_ratio(self):
        """ Get the amount of males/females currently alive in the simulation
        """
        return len(self.dataStore.male_organisms), len(self.dataStore.female_organisms)

    def organism_dead_count(self):
        """ Get amount of organisms that have passed away in the simulation
        """
        return len(self.dataStore.dead_organisms)

    def day(self):
        return self._sim_day

    def kill_amount(self, amount: int):
        """ Kill given amount of randomly chosen organisms
        """
        if amount < 0:
            # Protect against negative amounts
            return
        still_alive = self.organism_alive_count()
        if still_alive == 0:
            # All organisms are already dead
            return
        if still_alive < amount:
            # Avoid getting stuck in an endless loop of trying to kill
            # more organisms then there are actually alive
            amount = still_alive

        self._logger.log(f"Manually killed {amount} organisms")
        killed = 0
        while killed != amount:
            # A random organism is chosen every time
            # This is done in a while loop with an increment at the end
            # to make sure the right amount of organisms are killed
            index = random.randrange(self.organism_alive_count())
            to_kill = self.dataStore.organisms[index]
            self.kill(to_kill)
            # Increment amount killed
            killed += 1

    def kill(self, organism: Organism):
        """ Kill the organism at the given index """
        # Actually kill the organism
        self.dataStore.kill_organism(organism)
        # Make sure extensions know the organism is dead
        self._notify_extensions_of_death(organism)

    def simulate(self):
        """ Simulate a day in the current ecosystem.
        """

        self._nextday()
        death_log = self._mortality()
        self._reproduction()
        birth_log = self._nativity()
        return death_log + birth_log, self.organism_alive_count(), self.organism_dead_count()

    def _reproduction(self):
        # Repopulate the cluster once a year
        current_day: int = self.day()
        for cluster in self.dataStore.vegetation:
            cluster.repopulate(current_day)

        # First: Put Females into Menopause
        for org in self.dataStore.female_organisms:
            if org.fertile and org.should_enter_menopause():
                org.fertile = False

        if not self.dataStore.female_organisms:
            # Don't bother when there are no females alive
            return
        for male in self.dataStore.male_organisms:
            if male.age < male.organismInfo.maturity:
                continue
            missed = 0
            mated = 0
            mate_count = random.randrange(7)
            while mated < mate_count and missed < 7:
                mate_index = random.randrange(
                    len(self.dataStore.female_organisms))
                mate = self.dataStore.female_organisms[mate_index]
                if mate.breedingTerm == -1 and mate.organismInfo.maturity <= mate.age \
                        and mate.fertile:
                    mate.breedingTerm = mate.age
                    self._logger.log("Female impregnated")
                    mated += 1
                else:
                    missed += 1
        #
        # # Second: Check for 1 sexually mature Male
        # smm_flag: bool = False
        # for org in self.dataStore.organisms:
        #     if org.sex.name == "male" and org.age >= org.organismInfo.maturity:
        #         smm_flag = True
        # if not smm_flag:
        #     return
        #
        # # Third: Impregnate all sexually mature Females
        # for org in self.dataStore.organisms:
        #     if org.sex.name == "female" and org.breedingTerm == -1 and \
        #             org.organismInfo.maturity <= org.age and org.fertile:
        #         # Female gets impregnated
        #         org.breedingTerm = org.age
        #         self._logger.log("Female impregnated")

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
        if len(self.dataStore.organisms) == 0:
            # Catch for when all rats have died
            return []
        last_id: int = self.dataStore.organisms[-1].id
        for org in self.dataStore.organisms:
            if org is None:
                continue
            if org.sex.name == "female" and org.breedingTerm != -1:
                days_pregnant: int = org.age - org.breedingTerm
                breeding_time: int = org.organismInfo.breeding
                if days_pregnant > breeding_time:
                    raise Exception("Pregnant female exceeded breeding time.")
                elif days_pregnant == breeding_time:
                    # Birth occurs
                    self._logger.log("A rat was born")
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
            self.dataStore.add_organism(baby)
        return log

    def _notify_extensions_of_death(self, organism: Organism):
        for extension in self.mortality_extensions:
            extension.notify_organism_death(organism)

    def _mortality(self):
        log = []
        to_kill = []
        for org in self.dataStore.organisms:
            if org.should_die_naturally():
                log.append(f"{org.name} {org.id} died at age {org.age}.")
                self._logger.log(str(org.id) + " Rats died.")
                to_kill.append(org)
                continue
            else:
                # Let extensions also decide death per organism
                if next((extension.should_die(org, self.dataStore, log)
                         for extension in self.mortality_extensions), False):
                    to_kill.append(org)
                    continue

        for org in to_kill:
            self.kill(org)
        return log

    def _nextday(self):
        self._sim_day += 1
        for org in self.dataStore.organisms:
            org.age += 1

        for cluster in self.dataStore.vegetation:
            cluster.next_day()

        for extension in self.mortality_extensions:
            extension.next_day(self.dataStore)

    def _externalLog(self, msg: str):
        """ External access to logger (Just for UI purposes)
        """
        self._logger.logNoTimestamp(msg)
