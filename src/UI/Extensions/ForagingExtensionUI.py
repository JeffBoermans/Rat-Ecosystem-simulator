import dearpygui.dearpygui as dpg

from typing import List, Tuple

from .SimulationExtensionUI import SimulationExtensionUI
from ...Logic.Extensions.ForagingExtension import ForagingExtension as ForagingExtensionLogic
from ...UI.UI import UI


class ForagingExtensionUI(SimulationExtensionUI):
    def __init__(self) -> None:
        super().__init__()
        self.x_axis_tag_veg = "x_axis_cluster_veg"
        self.x_axis_veg = None
        self.x_axis_tag_org = "x_axis_cluster_org"
        self.x_axis_org = None
        self.y_axix_tag_veg = "y_axis_cluster_veg"
        self.y_axis_veg = None
        self.y_axix_tag_org = "y_axis_cluster_org"
        self.y_axis_org = None
        self.bar_plot_vegetation_tag = "bar_tag_clusters_vegetation"
        self.bar_plot_vegetation_label = "vegetation population"
        self.bar_plot_organism_tag = "bar_tag_clusters_organism"
        self.bar_plot_organism_label = "organism population"
        self.bar_plot_energy_tag = "bar_tag_clusters_energy"
        self.bar_plot_energy_label = "energy left"

    def add_ui_elements(self, ui: UI) -> None:
        # Add bar plot for cluster information
        with ui._dpg.window(label="Cluster Window", width=350, height=350) as cluster_window:
            with ui._dpg.plot(label='Cluster vegetation stats', height=-1, width=-1):
                ui._dpg.add_plot_legend()

                # Add x-axis
                self.x_axis_veg = ui._dpg.add_plot_axis(ui._dpg.mvXAxis, label='Clusters', tag=self.x_axis_tag_veg, no_gridlines=True)

                # Add y-axis
                self.y_axis_veg = ui._dpg.add_plot_axis(ui._dpg.mvYAxis, label='y', tag=self.y_axix_tag_veg)

            ui._dpg.add_bar_series(x=[], y=[], label=self.bar_plot_vegetation_label, parent=self.y_axix_tag_veg, tag=self.bar_plot_vegetation_tag)
            ui._dpg.add_bar_series(x=[], y=[], label=self.bar_plot_energy_label,     parent=self.y_axix_tag_veg, tag=self.bar_plot_energy_tag)
            ui._dpg.set_item_pos(cluster_window, [700, 0])

        with ui._dpg.window(label="Cluster 2 Window", width=350, height=350) as cluster_window:
            with ui._dpg.plot(label='Cluster organism stats', height=-1, width=-1):
                ui._dpg.add_plot_legend()

                # Add x-axis
                self.x_axis_org = ui._dpg.add_plot_axis(ui._dpg.mvXAxis, label='Clusters', tag=self.x_axis_tag_org, no_gridlines=True)

                # Add y-axis
                self.y_axis_org = ui._dpg.add_plot_axis(ui._dpg.mvYAxis, label='y', tag=self.y_axix_tag_org)

            ui._dpg.add_bar_series(x=[], y=[], label=self.bar_plot_organism_label,   parent=self.y_axix_tag_org, tag=self.bar_plot_organism_tag)
            ui._dpg.set_item_pos(cluster_window, [700, 350])

    def update_ui_elements(self, ui: UI) -> None:
        bar_label_pairs: List[Tuple[str, int]] = []     # The (cluster label, label x-pos) pairs
        bar_org_pop_series: Tuple[List[int], List[int]] = ([], [])  # The (series x-positions, series y-positions, series label)
        bar_veg_pop_series: Tuple[List[int], List[int]] = ([], [])  # The (series x-positions, series y-positions, series label)
        bar_energy_series:  Tuple[List[int], List[int]] = ([], [])  # The (series x-positions, series y-positions, series label)
        bar_cluster_x_offset: int = 4

        for idx, cluster in enumerate(ui.simulation.dataStore.vegetation):
            base_x: int = bar_cluster_x_offset * idx
            species, population = cluster.population()

            # Add x-tick label
            bar_label_pairs.append((f"{species} cl{idx}", base_x+1))

            # Add vegetation population series
            bar_veg_pop_series[0].append(base_x)
            bar_veg_pop_series[1].append(population)

            if isinstance(self, ForagingExtensionLogic):
                # Add cluster organism population
                bar_org_pop_series[0].append(base_x+1)
                bar_org_pop_series[1].append(self.get_cluster_organism_population(cluster))

            # Add cluster vegetation population
            bar_energy_series[0].append(base_x+2)
            bar_energy_series[1].append(cluster.energy_amount)

        ui._dpg.set_axis_ticks(self.x_axis_veg, tuple(bar_label_pairs))
        ui._dpg.set_value(self.bar_plot_vegetation_tag, [bar_veg_pop_series[0], bar_veg_pop_series[1]])
        ui._dpg.set_value(self.bar_plot_energy_tag,     [bar_energy_series[0],  bar_energy_series[1]])

        ui._dpg.fit_axis_data(self.x_axis_tag_veg)
        ui._dpg.fit_axis_data(self.y_axix_tag_veg)

        ui._dpg.set_value(self.bar_plot_organism_tag,   [bar_org_pop_series[0], bar_org_pop_series[1]])
        ui._dpg.set_axis_ticks(self.x_axis_org, tuple(bar_label_pairs))

        ui._dpg.fit_axis_data(self.x_axis_tag_org)
        ui._dpg.fit_axis_data(self.y_axix_tag_org)
