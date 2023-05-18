import random
import time

import dearpygui.dearpygui as dpg
import dearpygui_ext.logger as logger

from ..Logic.Simulation import Simulation


class UI():
    def __init__(self, _dpg) -> None:
        self.data_x = [0.0]
        self.data_y = [0.0]
        self.x_axis = None
        self.y_axis = None
        self._dpg = _dpg
        self.sec_tick = 0

        self.paused = True
        self.prev_update = time.time()

        self.logger = None
        self.simulation = None

    def _setup_simulation(self, sender, callback):
        if self._dpg.get_value("file_selected") == "":
            # Check that a file has been selected, else abort setup
            dpg.show_item("warn_select_file")
            print("No file selected")
            return

        b_fires = self._dpg.get_value("b_fires")
        b_virus = self._dpg.get_value("b_virus")
        self.sec_tick = self._dpg.get_value("i_tick")

        self.simulation = Simulation(self._dpg.get_value("file_selected"))
        self.data_y[0] = self.simulation.organism_alive_count()

        self.simulation._externalLog(
            f"Number of rats: {self.simulation.organism_alive_count()}\n")
        self.simulation._externalLog(f"Random Fires: {b_fires}\n")
        self.simulation._externalLog(f"Random Viruses: {b_virus}\n")
        self.simulation._externalLog(f"Ticks per second: {self.sec_tick}\n")
        self.logger = logger.mvLogger(self._dpg.add_window(
            label="mvLogger", pos=(0, 350), width=350, height=350))
        with self._dpg.window(label="Simulation Window", width=350, height=350) as plot_window:
            with dpg.group(horizontal=True):
                self._dpg.add_button(label="Start", callback=self.start)
                self._dpg.add_button(
                    label="Pause", callback=self.pause, tag="pause")
                self._dpg.add_button(label="Stop")
            with dpg.plot(label='Current Organism Population', height=-1, width=-1):
                self.x_axis = self._dpg.add_plot_axis(
                    self._dpg.mvXAxis, label='x', tag='x_axis')
                self.y_axis = self._dpg.add_plot_axis(
                    self._dpg.mvYAxis, label='y', tag='y_axis')
            self._dpg.add_line_series(x=self.data_x, y=self.data_y,
                                      label="Label", parent="y_axis",
                                      tag="series_tag")
        self._dpg.set_item_pos(plot_window, [0, 0])
        with self._dpg.window(label="Data box", width=350, height=350) as data_window:
            self._dpg.add_text(
                f"Ticks: {self.simulation.day()}", tag="updatectr")
            self._dpg.add_text("Number of rats in existence: ", tag="r_alive")
            self._dpg.add_text("Number of rats died: ", tag="r_dead")
            self._dpg.add_text("Number of random occurences happened: ")
        self._dpg.set_item_pos(data_window, [350, 0])
        with self._dpg.window(label="Control box", width=350, height=350) as control_box:
            self._dpg.add_text("Control the simulation while running")
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
        self._dpg.set_item_pos(control_box, [350, 350])

    def _file_selected(self, app_data, sender):
        dpg.hide_item("warn_select_file")
        self._dpg.set_value(
            "file_selected", f"{sender['selections'][sender['file_name']]}")

    def setup_main_window(self):
        self._dpg.create_context()
        self._dpg.create_viewport(
            title='Simulation', width=700, height=700)

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

    def run(self):
        while self._dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            if not self.paused:
                cur_time = time.time()
                elapsed = cur_time - self.prev_update
                if elapsed >= 1/self.sec_tick:
                    self.advance_simulation()
                    self.prev_update = cur_time
            self.update_data()
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
        self.data_x.append(cur_sim_day)
        self.data_y.append(alive)
        self._dpg.set_value("r_alive", f"Number of rats alive: {alive}")
        self._dpg.set_value("r_dead", f"Number of rats died: {dead}")

        # set the series x and y to the last nsamples
        self._dpg.set_value(
            'series_tag', [self.data_x, self.data_y])
        dpg.fit_axis_data('x_axis')
        dpg.fit_axis_data('y_axis')

    def advance_simulation(self):
        if self.simulation is None:
            return
        logs, _, _ = self.simulation.simulate()

        for log in logs:
            self.logger.log(log)
