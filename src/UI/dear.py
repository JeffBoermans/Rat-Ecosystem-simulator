import dearpygui.dearpygui as dpg
import dearpygui_ext.logger as logger
import time


class dpg_plot():
    def __init__(self, _dpg) -> None:
        self.time_step = 1
        self.data_x = [0.0]
        self.data_y = [2.0]
        self.x_axis = None
        self.y_axis = None
        self._dpg = _dpg
        self.updatectr = 0
        self.sec_tick = 0

        self.paused = True
        self.prev_update = time.time()

    def runSimulation(self, sender, callback):
        if self._dpg.get_value("file_selected") == "":
            print("No file selected")
            return
        nr_rats = self._dpg.get_value("i_rats")
        b_fires = self._dpg.get_value("b_fires")
        b_virus = self._dpg.get_value("b_virus")
        self.sec_tick = self._dpg.get_value("i_tick")

        print(f"Number of rats: {nr_rats}")
        print(f"Random Fires: {b_fires}")
        print(f"Random Viruses: {b_virus}")
        print(f"Seconds per tick: {self.sec_tick}")
        logger_ = logger.mvLogger(self._dpg.add_window(
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
            self._dpg.add_text(f"Ticks: {self.updatectr}", tag="updatectr")
            self._dpg.add_text("Number of rats in existence: ")
            self._dpg.add_text("Number of rats died: ")
            self._dpg.add_text("Number of random occurences happened: ")
        self._dpg.set_item_pos(data_window, [350, 0])
        logger_.log("Rat 1 starved to death")

    def fileCallback(self, app_data, sender):
        self._dpg.set_value("file_selected", f"Current file selected: {sender['file_name']}")

    def setUpSimulation(self):
        self._dpg.create_context()
        self._dpg.create_viewport(
            title='Simulation Configuration', width=700, height=700)
        with self._dpg.window(label="Window", tag="primary"):
            self._dpg.add_input_int(
                label="Number of rats", tag="i_rats", min_value=1, min_clamped=True, default_value=1)
            self._dpg.add_text("Random occurences")
            self._dpg.add_text("=================")
            self._dpg.add_checkbox(label="Wildfires", tag="b_fires")
            self._dpg.add_checkbox(label="Viruses", tag="b_virus")
            self._dpg.add_text("=================")
            self._dpg.add_text(
                "One tick is equal to one day in the simulation")
            self._dpg.add_input_int(
                label="Seconds per tick", min_value=1, min_clamped=True, default_value=1, tag="i_tick")
            self._dpg.add_text("=================")
            self._dpg.add_text("Add a session file (.json)")
            self._dpg.add_text("-----------------")
            with self._dpg.file_dialog(directory_selector=False, show=False, id="file_dialog_id", width=700 ,height=400, 
                                       callback=self.fileCallback):
                self._dpg.add_file_extension(".json")
            self._dpg.add_button(label="File Selector", callback=lambda: dpg.show_item("file_dialog_id"))
            self._dpg.add_text("", tag="file_selected")
            self._dpg.add_text("=================")
            self._dpg.add_button(label="Start Simulation", callback=self.runSimulation)
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
                print(elapsed)
                if elapsed >= self.sec_tick:
                    self.update_data()
                    self.prev_update = cur_time
        self._dpg.destroy_context()

    def update_data(self):
        self.updatectr += 1
        self._dpg.set_value(
            "updatectr", f"Time steps processed: {self.updatectr}")
        # Get new data sample. Note we need both x and y values
        # if we want a meaningful axis unit.
        self.data_x.append(self.time_step)
        self.data_y.append(self.data_y[self.time_step-1]*2)

        # set the series x and y to the last nsamples
        self._dpg.set_value(
            'series_tag', [list(self.data_x), list(self.data_y)])
        dpg.fit_axis_data('x_axis')
        dpg.fit_axis_data('y_axis')

        self.time_step = self.time_step+1


if __name__ == '__main__':
    plot = dpg_plot(dpg)
    plot.setUpSimulation()
    plot.run()
