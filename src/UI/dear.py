import dearpygui.dearpygui as dpg
import dearpygui_ext.logger as logger

class dpg_plot():
    def __init__(self, _dpg) -> None:
        self.time_step = 1
        self.data_x = [0.0]
        self.data_y = [2.0]
        self.x_axis = None
        self.y_axis = None
        self._dpg = _dpg
        self.updatectr = 0
    
    def runSimulation(self, sender, callback):
        sim_name = self._dpg.get_value("sim_name")
        nr_rats = self._dpg.get_value("nr_rats")
        r_occ = self._dpg.get_value("r_occ")
        print(f"Name of simulation: {sim_name}")
        print(f"Number of rats: {nr_rats}")
        print(f"Random occurences: {r_occ}")
    
        with self._dpg.window(label="Simulation Window", width=350, height=350) as plot_window:
            self._dpg.add_button(label="Button", callback=self.update_data)
            with dpg.plot(label='Line Series', height=-1, width=-1):
                self.x_axis = self._dpg.add_plot_axis(self._dpg.mvXAxis, label='x', tag='x_axis')
                self.y_axis = self._dpg.add_plot_axis(self._dpg.mvYAxis, label='y', tag='y_axis')
            self._dpg.add_line_series(x=list(self.data_x), y=list(self.data_y),
                                label="Label", parent="y_axis",
                                tag="series_tag")
        self._dpg.set_item_pos(plot_window, [0,0])
        with self._dpg.window(label="Data box", width = 350, height = 350) as data_window:
            self._dpg.add_text(f"Time steps processed: {self.updatectr}", tag="updatectr")
            self._dpg.add_text("Number of rats in existence: ")
            self._dpg.add_text("Number of rats died: ")
            self._dpg.add_text("Number of random occurences happened: ")
        self._dpg.set_item_pos(data_window, [350,0])
        a = logger.mvLogger(self._dpg.add_window(label="mvLogger", pos=(0, 350), width=350, height=350))
        a.log("Rat Sander has died")



    def setUpSimulation(self):
        self._dpg.create_context()
        self._dpg.create_viewport(title='Simulation Configuration', width=700, height = 700)
        with self._dpg.window(label="Window", tag="primary"):
            with self._dpg.menu_bar():
                with self._dpg.menu(label="Settings"):
                    self._dpg.add_input_text(label="Name of simulation", tag="sim_name")
                    self._dpg.add_input_int(label="Number of rats", tag="nr_rats")
                    self._dpg.add_text("Random occurences")
                    self._dpg.add_text("=================")
                    self._dpg.add_checkbox(label="Wildfires", tag="r_occ")
                    self._dpg.add_checkbox(label="Viruses")
                    self._dpg.add_button(label="Start Simulation", callback=self.runSimulation)
        self._dpg.setup_dearpygui()
        self._dpg.show_viewport()
        self._dpg.set_primary_window("primary", True)
        

    def run(self):
        # Replaces the start_dearpygui()
        while self._dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        self._dpg.destroy_context()

    def update_data(self):
        self.updatectr += 1
        self._dpg.set_value("updatectr", f"Time steps processed: {self.updatectr}")
        nsamples = 10
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




