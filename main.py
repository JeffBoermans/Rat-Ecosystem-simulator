from src.Logic.Simulation import Simulation


if __name__ == '__main__':
    new_sim: Simulation = Simulation("Input/SessionFiles/session1.json")
    print("Starting simulation ...")
    new_sim.run()
    print("Persisting results ...")
    new_sim.persist("Output/results.json")
    print("Simulation stopped")