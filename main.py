from sim import Simulation

if __name__ == '__main__':
    new_sim: Simulation = Simulation("Input/session_files/session1.json")
    print("Starting simulation...")
    new_sim.setUp()