import random
import time

from typing import List

import dearpygui.dearpygui as dpg
import dearpygui_ext.logger as logger

from ..Logic.Simulation import Simulation
from ..Logic.Extensions.SimulationExtension import SimulationExtension, SimulationMortalityExtension
from .Extensions.SimulationExtensionUI import SimulationExtensionUI


class UI():
    def __init__(self, _dpg: dpg, extensions: List[SimulationExtensionUI] = None) -> None:
        if extensions is None:
            extensions = []
        for extension in extensions:
            if not (isinstance(extension, SimulationExtension) and isinstance(extension, SimulationExtensionUI)):
                raise RuntimeError(
                    f"All extensions must be instances of both the {SimulationExtension.__name__} class and the {SimulationExtensionUI.__name__} class")

        self.data_x = [0.0]
        self.data_y = [0.0]
        self._dpg = _dpg
        self.sec_tick = 0

        self.paused = True
        self.prev_update = time.time()

        self.logger = None
        self.simulation = None

        self.extensions: List[SimulationExtensionUI] = extensions

    def _setup_population_graph(self):
        window_id = "sim_population_graph"
        with self._dpg.window(label="Population Graph", id=window_id, width=350, height=350, no_close=True):
            with dpg.group(horizontal=True):
                self._dpg.add_button(label="Start", callback=self.start)
                self._dpg.add_button(
                    label="Pause", callback=self.pause, tag="pause")
                self._dpg.add_button(label="Stop")
            with dpg.plot(label='Current Organism Population', height=-1, width=-1):
                self._dpg.add_plot_axis(
                    self._dpg.mvXAxis, label='x', tag='x_axis')
                self._dpg.add_plot_axis(
                    self._dpg.mvYAxis, label='y', tag='y_axis')
            self._dpg.add_line_series(x=self.data_x, y=self.data_y,
                                      label="Label", parent="y_axis",
                                      tag="series_tag")
        return window_id

    def _setup_data_window(self):
        window_id = "sim_data_window"
        with self._dpg.window(label="Data box", id=window_id, width=350, height=350, no_close=True):
            self._dpg.add_text(
                f"Day: {self.simulation.day()}", tag="updatectr")
            self._dpg.add_text("Number of rats in existence: ", tag="r_alive")
            self._dpg.add_text("Number of rats died: ", tag="r_dead")
            self._dpg.add_text("Number of random occurences happened: ")
        return window_id

    def _setup_control_window(self):
        window_id = "sim_control_window"
        with self._dpg.window(label="Control box", id=window_id, width=350, height=350, no_close=True):
            self._dpg.add_text("Control the simulation while running")

            self._dpg.add_text("====================================")
            self._dpg.add_text("Change simulation speed")
            with self._dpg.group(horizontal=True):
                self._dpg.add_input_int(label="Ticks per second", min_value=1,
                                        min_clamped=True, default_value=self.sec_tick,
                                        tag="sim_i_tick", width=100)
                self._dpg.add_button(
                    label="Update", callback=self.update_sim_speed)

            self._dpg.add_text("====================================")
            self._dpg.add_text("Random Purge")
            self._dpg.add_text("Select a min and max value")
            with self._dpg.group(horizontal=True):
                self._dpg.add_input_int(
                    label="", min_value=1, min_clamped=True, default_value=1, tag="min_val", width=100)
                self._dpg.add_input_int(
                    label="", min_value=2, min_clamped=True, default_value=2, tag="max_val", width=100
                )
                self._dpg.add_button(label="KILL", callback=self.purge)
            self._dpg.add_text("=============================")
            with self._dpg.group(horizontal=True):
                self._dpg.add_button(label="Start Fire")
                self._dpg.add_button(label="End Fire")
            self._dpg.add_text("=============================")
            with self._dpg.group(horizontal=True):
                self._dpg.add_button(label="Insert Virus")
                self._dpg.add_button(label="Kill virus")
        return window_id

    def _setup_simulation(self, sender, callback):
        if self._dpg.get_value("file_selected") == "":
            # Check that a file has been selected, else abort setup
            dpg.show_item("warn_select_file")
            return
        self._dpg.hide_item("primary")

        b_fires = self._dpg.get_value("b_fires")
        b_virus = self._dpg.get_value("b_virus")
        self.sec_tick = self._dpg.get_value("i_tick")

        self.simulation = Simulation(self._dpg.get_value("file_selected"))
        for extension in self.extensions:
            if isinstance(extension, SimulationMortalityExtension):
                self.simulation.register_mortality_extension(extension)

        self.data_y[0] = self.simulation.organism_alive_count()

        # Initial log to file
        self.simulation._externalLog(
            f"Number of rats: {self.simulation.organism_alive_count()}\n")
        self.simulation._externalLog(f"Random Fires: {b_fires}\n")
        self.simulation._externalLog(f"Random Viruses: {b_virus}\n")
        self.simulation._externalLog(f"Ticks per second: {self.sec_tick}\n")

        self.logger = logger.mvLogger(self._dpg.add_window(
            label="mvLogger", pos=(0, 350), width=350, height=350, no_close=True))

        population_graph_id = self._setup_population_graph()
        self._dpg.set_item_pos(population_graph_id, [0, 0])

        data_window_id = self._setup_data_window()
        self._dpg.set_item_pos(data_window_id, [350, 0])

        control_window_id = self._setup_control_window()
        self._dpg.set_item_pos(control_window_id, [350, 350])

        for extension in self.extensions:
            extension.add_ui_elements(self)

    def _file_selected(self, app_data, sender):
        dpg.hide_item("warn_select_file")
        self._dpg.set_value(
            "file_selected", f"{sender['selections'][sender['file_name']]}")

    def setup_main_window(self):
        self._dpg.create_context()
        self._dpg.create_viewport(
            title='Simulation', width=1065, height=738)

        with self._dpg.window(label="Window", tag="primary"):
            # Enable random occurrences in the simulation
            self._dpg.add_text("Random occurrences")
            self._dpg.add_text("=================")
            self._dpg.add_checkbox(label="Wildfires", tag="b_fires")
            self._dpg.add_checkbox(label="Viruses", tag="b_virus")
            # Set simulation time steps
            self._dpg.add_text("=================")
            self._dpg.add_text(
                "One tick is equal to one day in the simulation")
            self._dpg.add_input_int(
                label="Ticks per second", min_value=1, min_clamped=True, default_value=30, tag="i_tick", width=100)
            # Select session file
            self._dpg.add_text("=================")
            self._dpg.add_text("Add a session file (.json)")
            self._dpg.add_text("-----------------")
            with self._dpg.file_dialog(directory_selector=False, show=False, id="file_dialog_id", width=700, height=400,
                                       callback=self._file_selected):
                self._dpg.add_file_extension(".json")
            with dpg.group(horizontal=True):
                self._dpg.add_button(
                    label="File Selector", callback=lambda: dpg.show_item("file_dialog_id"))
                # Warning when no file is selected
                self._dpg.add_text("Please select a session file.", show=False,
                                   id="warn_select_file", color=(230, 50, 40))
            self._dpg.add_text("", tag="file_selected")
            self._dpg.add_text("=================")
            # Start
            self._dpg.add_button(label="Load Simulation",
                                 callback=self._setup_simulation)

        self._dpg.setup_dearpygui()
        self._dpg.show_viewport()
        self._dpg.set_primary_window("primary", True)

    def pause(self):
        self.paused = not self.paused

    def start(self):
        self.paused = False

    def purge(self):
        min_val: int = self._dpg.get_value("min_val")
        max_val: int = self._dpg.get_value("max_val")
        rand_val = random.randint(min_val, max_val)
        if min_val >= max_val:
            # TODO: Maybe error message display?
            pass
        elif self.simulation is not None:
            self.simulation.kill(rand_val)

    def update_sim_speed(self):
        self.sec_tick = self._dpg.get_value("sim_i_tick")

    def run(self):
        while self._dpg.is_dearpygui_running():
            self.update_data()
            if not self.paused:
                cur_time = time.time()
                elapsed = cur_time - self.prev_update
                if elapsed >= 1/self.sec_tick:
                    self.advance_simulation()
                    self.prev_update = cur_time
            dpg.render_dearpygui_frame()
        self._dpg.destroy_context()

    def update_data(self):
        if self.simulation is None:
            return
        cur_sim_day = self.simulation.day()
        alive = self.simulation.organism_alive_count()
        dead = self.simulation.organism_dead_count()
        self._dpg.set_value(
            "updatectr", f"Time steps processed: {cur_sim_day}")
        # Get new data from the simulation. Note we need both x and y values
        # if we want a meaningful axis unit.
        if cur_sim_day == len(self.data_x):
            self.data_x.append(cur_sim_day)
            self.data_y.append(alive)
        else:
            self.data_y[cur_sim_day] = alive
        self._dpg.set_value("r_alive", f"Number of rats alive: {alive}")
        self._dpg.set_value("r_dead", f"Number of rats died: {dead}")

        # set the series x and y to the last nsamples
        self._dpg.set_value(
            'series_tag', [self.data_x, self.data_y])
        if not self.paused:
            dpg.fit_axis_data('x_axis')
            dpg.fit_axis_data('y_axis')

        for extension in self.extensions:
            extension.update_ui_elements(self)

    def advance_simulation(self):
        if self.simulation is None:
            return
        logs, _, _ = self.simulation.simulate()

        for log in logs:
            self.logger.log(log)
