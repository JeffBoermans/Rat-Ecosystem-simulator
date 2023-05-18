import dearpygui.dearpygui as dpg
from src.UI.UI import UI


def main():
    """The main entrypoint of the simulation application.
    """
    sim = UI(dpg)
    sim.setUpSimulation()
    sim.run()


if __name__ == '__main__':
    main()
