import dearpygui.dearpygui as dpg

from src.UI.UI import UI
from src import FullExtensions


def main():
    """The main entrypoint of the simulation application.
    """
    sim = UI(dpg, extensions=[
        FullExtensions.ForagingExtension.ForagingExtensionFull()
    ])
    sim.setup_main_window()
    sim.run()


if __name__ == '__main__':
    main()
