from src import Simulation

from src.Logic.Entities.organism import Organism, OrganismInfo, OrganismSexesEnum


def main():
    inputfile: str = "Input/SessionFiles/session1.json"
    new_sim: Simulation = Simulation(inputfile)
    days:int = 39 * 30


    print("Starting simulation ...")
    new_sim.run(days)

    print("Persisting results ...")
    new_sim.persist("Output/results.json")

    print("Simulation stopped")

if __name__ == '__main__':
    main()