import dearpygui.dearpygui as dpg
from src.UI.UI import dpg_plot


def main():
    plot = dpg_plot(dpg)
    plot.setUpSimulation()
    plot.run()


if __name__ == '__main__':
    main()
