import dearpygui.dearpygui as dpg
import dearpygui_ext.logger as logger
import time

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

    def runSimulation(self, sender, callback):
        if self._dpg.get_value("file_selected") == "":
            print("No file selected")
            return
        b_fires = self._dpg.get_value("b_fires")
        b_virus = self._dpg.get_value("b_virus")
        self.sec_tick = self._dpg.get_value("i_tick")

        self.simulation = Simulation(self._dpg.get_value("file_selected"))
        self.simulation._load()
        self.data_y[0] = self.simulation.organism_alive_count()

        print(f"Number of rats: {self.simulation.organism_alive_count()}")
        print(f"Random Fires: {b_fires}")
        print(f"Random Viruses: {b_virus}")
        print(f"Ticks per second: {self.sec_tick}")
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
            self._dpg.add_line_series(x=list(self.data_x), y=list(self.data_y),
                                      label="Label", parent="y_axis",
                                      tag="series_tag")
        self._dpg.set_item_pos(plot_window, [0, 0])
        with self._dpg.window(label="Data box", width=350, height=350) as data_window:
            self._dpg.add_text(
                f"Ticks: {self.simulation.day()}", tag="updatectr")
            self._dpg.add_text("Number of rats in existence: ", tag="r_alive")
            self._dpg.add_text("Number of rats died: ", tag = "r_dead")
            self._dpg.add_text("Number of random occurences happened: ")
        self._dpg.set_item_pos(data_window, [350, 0])
        # Logging example
        # self.logger.log("Rat 1 starved to death")

    def fileCallback(self, app_data, sender):
        self._dpg.set_value(
            "file_selected", f"{sender['selections'][sender['file_name']]}")

    def setUpSimulation(self):
        self._dpg.create_context()
        self._dpg.create_viewport(
            title='Simulation Configuration', width=700, height=700)
        with self._dpg.window(label="Window", tag="primary"):
            self._dpg.add_text("Random occurences")
            self._dpg.add_text("=================")
            self._dpg.add_checkbox(label="Wildfires", tag="b_fires")
            self._dpg.add_checkbox(label="Viruses", tag="b_virus")
            self._dpg.add_text("=================")
            self._dpg.add_text(
                "One tick is equal to one day in the simulation")
            self._dpg.add_input_int(
                label="Ticks per second", min_value=1, min_clamped=True, default_value=1, tag="i_tick")
            self._dpg.add_text("=================")
            self._dpg.add_text("Add a session file (.json)")
            self._dpg.add_text("-----------------")
            with self._dpg.file_dialog(directory_selector=False, show=False, id="file_dialog_id", width=700, height=400,
                                       callback=self.fileCallback):
                self._dpg.add_file_extension(".json")
            self._dpg.add_button(
                label="File Selector", callback=lambda: dpg.show_item("file_dialog_id"))
            self._dpg.add_text("", tag="file_selected")
            self._dpg.add_text("=================")
            self._dpg.add_button(label="Start Simulation",
                                 callback=self.runSimulation)
        self._dpg.setup_dearpygui()
        self._dpg.show_viewport()
        self._dpg.set_primary_window("primary", True)

    def pause(self):
        self.paused = not self.paused

    def start(self):
        self.paused = False

    def run(self):
        while self._dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            if not self.paused:
                cur_time = time.time()
                elapsed = cur_time - self.prev_update
                # print(elapsed)
                if elapsed >= 1/self.sec_tick:
                    self.update_data()
                    self.prev_update = cur_time
        self._dpg.destroy_context()

    def update_data(self):
        if self.simulation is None:
            return
        self._dpg.set_value(
            "updatectr", f"Time steps processed: {self.simulation.day()}")
        # Advance the time in the simulation
        logs, alive, dead = self.simulation.simulate()
        # Get new data from the simulation. Note we need both x and y values
        # if we want a meaningful axis unit.
        self.data_x.append(self.simulation.day())
        self.data_y.append(self.simulation.organism_alive_count())
        self._dpg.set_value("r_alive", f"Number of rats alive: {alive}")
        self._dpg.set_value("r_dead", f"Number of rats died: {dead}")

        for log in logs:
            self.logger.log(log)

        # set the series x and y to the last nsamples
        self._dpg.set_value(
            'series_tag', [list(self.data_x), list(self.data_y)])
        dpg.fit_axis_data('x_axis')
        dpg.fit_axis_data('y_axis')
