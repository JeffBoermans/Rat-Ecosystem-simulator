import dearpygui.dearpygui as dpg
from src.UI.UI import UI


def main():
    plot = UI(dpg)
    plot.setUpSimulation()
    plot.run()


if __name__ == '__main__':
    main()
