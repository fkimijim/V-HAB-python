import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    """
    Plotter class for simulations
    This class handles the definition and creation of plots and figures using logged simulation data.
    """

    def __init__(self, simulation_infrastructure, logger_name="oLogger"):
        """
        Constructor for the Plotter class.
        Args:
            simulation_infrastructure: Reference to the simulation infrastructure object.
            logger_name (str): Name of the logger object from which data is fetched.
        """
        self.simulation_infrastructure = simulation_infrastructure
        self.logger_name = logger_name
        self.figures = []  # List of figure objects

    def define_plot(self, plot_values, title, plot_options=None):
        """
        Defines a single plot.
        Args:
            plot_values (list): List of data items to plot (e.g., log indices or names).
            title (str): Title of the plot.
            plot_options (dict, optional): Additional options for the plot.
        Returns:
            dict: A dictionary containing plot configuration.
        """
        if isinstance(plot_values, str):
            raise ValueError(f"Plot values for '{title}' should be a list. Enclose string in square brackets.")

        if plot_options is None:
            plot_options = {}

        logger = getattr(self.simulation_infrastructure, self.logger_name)
        indices = logger.find(plot_values, plot_options.get("filter"))

        num_units, unique_units = self.get_number_of_units(logger, indices)

        if num_units > 2 and "unit_override" not in plot_options:
            plot_options["unit_override"] = ["all left"]
            plot_options["y_label"] = "[-]"
            plot_options["num_units"] = 1
        else:
            plot_options["num_units"] = num_units
            plot_options["unique_units"] = unique_units

        if "alt_x_axis" in plot_options:
            plot_options["alt_x_index"] = logger.find([plot_options["alt_x_axis"]])

        return {"title": title, "indices": indices, "options": plot_options}

    def define_figure(self, plots, name, figure_options=None):
        """
        Defines a figure containing multiple plots.
        Args:
            plots (list): List of plot configurations.
            name (str): Name of the figure.
            figure_options (dict, optional): Options for the figure layout.
        """
        if any(fig["name"] == name for fig in self.figures):
            raise ValueError(f"Figure with name '{name}' already exists.")

        if figure_options is None:
            figure_options = {}

        if figure_options.get("arrange_square"):
            grid_size = int(np.ceil(np.sqrt(len(plots))))
            arranged_plots = [None] * (grid_size ** 2)
            arranged_plots[:len(plots)] = plots
            plots = arranged_plots

        self.figures.append({"name": name, "plots": plots, "options": figure_options})

    def plot(self):
        """
        Generates all defined plots and figures.
        """
        logger = getattr(self.simulation_infrastructure, self.logger_name)

        for figure in self.figures:
            fig, axes = plt.subplots(
                nrows=int(np.sqrt(len(figure["plots"]))),
                ncols=int(np.sqrt(len(figure["plots"])))
            )
            for ax, plot_config in zip(axes.flatten(), figure["plots"]):
                if plot_config is None:
                    ax.axis("off")
                    continue

                indices = plot_config["indices"]
                options = plot_config["options"]
                title = plot_config["title"]

                data, time, log_props = logger.get(indices)
                ax.plot(time, data)
                ax.set_title(title)
                ax.set_xlabel(options.get("x_label", "Time"))
                ax.set_ylabel(options.get("y_label", "Values"))
                ax.grid(True)

            plt.tight_layout()
            plt.show()

    @staticmethod
    def get_number_of_units(logger, indices):
        """
        Returns the number of unique units in the plot data.
        Args:
            logger: Logger object.
            indices (list): List of indices to check.
        Returns:
            tuple: Number of units and list of unique units.
        """
        units = [logger.get_unit(index) for index in indices]
        unique_units = list(set(units))
        return len(unique_units), unique_units
