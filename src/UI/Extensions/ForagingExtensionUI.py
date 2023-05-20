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
        self.energy_maxes = [1000]
        self.population_maxes =[1]

    def add_ui_elements(self, ui: UI) -> int:
        # Add bar plot for cluster information
        nice_height = (ui._dpg.get_viewport_client_height() - ui._dpg.get_item_height("sim_population_graph")) / 2
        nice_width = (ui._dpg.get_viewport_client_width()/100)*45
        with ui._dpg.window(label="Cluster Window", width=nice_width, height=nice_height, no_close=True) as cluster_window:
            with ui._dpg.plot(label='Cluster vegetation stats', height=-1, width=-1):
                ui._dpg.add_plot_legend()

                # Add x-axis
                self.x_axis_veg = ui._dpg.add_plot_axis(ui._dpg.mvXAxis, label='Clusters', tag=self.x_axis_tag_veg, no_gridlines=True)

                # Add y-axis
                self.y_axis_veg = ui._dpg.add_plot_axis(ui._dpg.mvYAxis, label='Energy left', tag=self.y_axix_tag_veg)

            ui._dpg.add_bar_series(x=[], y=[], label=self.bar_plot_vegetation_label, parent=self.y_axix_tag_veg, tag=self.bar_plot_vegetation_tag)
            ui._dpg.add_bar_series(x=[], y=[], label=self.bar_plot_energy_label,     parent=self.y_axix_tag_veg, tag=self.bar_plot_energy_tag)
            ui._dpg.set_item_pos(cluster_window, [0, ui._dpg.get_item_height("sim_population_graph")])

        with ui._dpg.window(label="Cluster 2 Window", width=nice_width, height=nice_height, no_close=True) as cluster_window:
            with ui._dpg.plot(label='Cluster organism stats', height=-1, width=-1):
                ui._dpg.add_plot_legend()

                # Add x-axis
                self.x_axis_org = ui._dpg.add_plot_axis(ui._dpg.mvXAxis, label='Clusters', tag=self.x_axis_tag_org, no_gridlines=True)

                # Add y-axis
                self.y_axis_org = ui._dpg.add_plot_axis(ui._dpg.mvYAxis, label='Number of Organisms', tag=self.y_axix_tag_org)

            ui._dpg.add_bar_series(x=[], y=[], label=self.bar_plot_organism_label,   parent=self.y_axix_tag_org, tag=self.bar_plot_organism_tag)
            ui._dpg.set_item_pos(cluster_window, [0, ui._dpg.get_item_height("sim_population_graph")
                                                  + nice_height])
        return nice_width

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

        #Collect 50 samples
        if len(self.energy_maxes) == 50:
            del self.energy_maxes[0]
        self.energy_maxes.append(max(bar_energy_series[1]))
        max_energy = max(self.energy_maxes)
        # Ik weet niet hoezo (het is ook gwn laat en ik ben moe) maar om de 1 of andere fucking
        # rot reden moet ik dit hardcoden en accepteert die niet hoe ik initializeer?
        # Als ik deze 2 schreeuwlelijke lijnen niet toevoeg loopt de y-waarde van 0 tot 0 op die
        # godvergeten grafiek
        # Jeff is tired
        if max_energy == 0:
            max_energy = 1000

        if len(self.population_maxes) == 50:
            del self.population_maxes[0]
        self.population_maxes.append(max(bar_org_pop_series[1]))
        max_pop = max(self.population_maxes)
        if max_pop == 0:
            max_pop = 1

        ui._dpg.set_axis_ticks(self.x_axis_veg, tuple(bar_label_pairs))
        ui._dpg.set_value(self.bar_plot_vegetation_tag, [bar_veg_pop_series[0], bar_veg_pop_series[1]])
        ui._dpg.set_value(self.bar_plot_energy_tag,     [bar_energy_series[0],  bar_energy_series[1]])

        ui._dpg.fit_axis_data(self.x_axis_tag_veg)
        ui._dpg.set_axis_limits(self.y_axix_tag_veg, 0, max_energy)

        ui._dpg.set_value(self.bar_plot_organism_tag,   [bar_org_pop_series[0], bar_org_pop_series[1]])
        ui._dpg.set_axis_ticks(self.x_axis_org, tuple(bar_label_pairs))

        ui._dpg.fit_axis_data(self.x_axis_tag_org)
        ui._dpg.set_axis_limits(self.y_axix_tag_org, 0 , max_pop)
