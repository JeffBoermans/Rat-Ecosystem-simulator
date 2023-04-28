import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title='Population Simulation', width=600, height=600)


time_step = 1
data_x = [0.0]
data_y = [2.0]


def update_data():
    global time_step
    global data_x
    global data_y

    nsamples = 10
    # Get new data sample. Note we need both x and y values
    # if we want a meaningful axis unit.
    data_x.append(time_step)
    data_y.append(data_y[time_step-1]*2)

    # set the series x and y to the last nsamples
    dpg.set_value(
        'series_tag', [list(data_x), list(data_y)])
    dpg.fit_axis_data('x_axis')
    dpg.fit_axis_data('y_axis')

    time_step = time_step+1


with dpg.window(label="Window", tag="primary"):
    dpg.add_button(label="Button", callback=update_data)

    with dpg.plot(label='Line Series', height=-1, width=-1):
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis')
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis')

        dpg.add_line_series(x=list(data_x), y=list(data_y),
                            label="Label", parent="y_axis",
                            tag="series_tag")


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("primary", True)
dpg.start_dearpygui()
dpg.destroy_context()
