import dearpygui.dearpygui as dpg


class dpg_plot():
    def __init__(self, _dpg) -> None:
        self.time_step = 1
        self.data_x = [0.0]
        self.data_y = [2.0]
        self.x_axis = None
        self.y_axis = None
        self._dpg = _dpg

    def setUpPlot(self):
        self._dpg.create_context()
        self._dpg.create_viewport(title='Population Simulation', width=600, height=600)
        with self._dpg.window(label="Window", tag="primary"):
            self._dpg.add_button(label="Button", callback=self.update_data)
            with dpg.plot(label='Line Series', height=-1, width=-1):
                self.x_axis = self._dpg.add_plot_axis(self._dpg.mvXAxis, label='x', tag='x_axis')
                self.y_axis = self._dpg.add_plot_axis(self._dpg.mvYAxis, label='y', tag='y_axis')
            self._dpg.add_line_series(x=list(self.data_x), y=list(self.data_y),
                                label="Label", parent="y_axis",
                                tag="series_tag")
        self._dpg.setup_dearpygui()
        self._dpg.show_viewport()
        self._dpg.set_primary_window("primary", True)
        

    def run(self):
        self._dpg.start_dearpygui()
        self._dpg.destroy_context()

    def update_data(self):

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
    plot.setUpPlot()
    plot.run()




