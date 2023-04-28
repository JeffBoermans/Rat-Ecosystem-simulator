from src import Simulation

def main():
    inputfile: str = "Input/SessionFiles/session1.json"
    new_sim: Simulation = Simulation(inputfile)

    print("Starting simulation ...")
    new_sim.run()

    print("Persisting results ...")
    new_sim.persist("Output/results.json")

    print("Simulation stopped")

if __name__ == '__main__':
    main()