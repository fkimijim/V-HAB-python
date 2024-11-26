class Setup:
    """
    SETUP class for initializing and configuring a simulation.

    This class is used to:
    - Instantiate the root object.
    - Register branches to their appropriate solvers.
    - Determine which items are logged.
    - Set the simulation duration.
    - Provide methods for plotting the results.
    """

    def __init__(self, config_params, solver_params, monitor_config, sim_time=10):
        """
        Constructor for the Setup class.

        Args:
            config_params (dict): Configuration parameters.
            solver_params (dict): Solver parameters.
            monitor_config (dict): Monitor configuration.
            sim_time (float): Simulation time in seconds (default is 10).
        """
        self.simulation_name = "Test_CCAA"
        self.config_params = config_params
        self.solver_params = solver_params
        self.monitor_config = monitor_config
        self.sim_time = sim_time

        # Create the root simulation container
        self.simulation_container = SimulationContainer(self.simulation_name)
        self.example_system = Example(self.simulation_container, "Example")

    def configure_monitors(self):
        """
        Configures the logger for the simulation.
        """
        logger = Logger()

        for i in range(1, 7):
            cabin_prefix = f"Example:s:Cabin_{i}"
            ccaa_prefix = f"Example:c:CCAA_{i}"

            logger.add_value(f"{cabin_prefix}.toPhases.Air", "rRelHumidity", "-", f"Relative Humidity Cabin_{i}")
            logger.add_value(f"{cabin_prefix}.toPhases.Air", "fTemperature", "K", f"Temperature Cabin_{i}")

            logger.add_value(f"{ccaa_prefix}:c:CCAA_CHX", "fTotalCondensateHeatFlow", "W", f"CCAA_{i} Condensate Heat Flow")
            logger.add_value(f"{ccaa_prefix}:c:CCAA_CHX", "fTotalHeatFlow", "W", f"CCAA_{i} Total Heat Flow")
            logger.add_value(f"{ccaa_prefix}:c:CCAA_CHX", "fTempOut_Fluid1", "K", f"CCAA_{i} Air Outlet Temperature")
            logger.add_value(f"{ccaa_prefix}:c:CCAA_CHX", "fTempOut_Fluid2", "K", f"CCAA_{i} Coolant Outlet Temperature")
            logger.add_value(f"{ccaa_prefix}:s:CHX.toProcsP2P.CondensingHX", "fFlowRate", "kg/s", f"CCAA_{i} Condensate Flow Rate")
            logger.add_value(f"{ccaa_prefix}:s:Mixing.toPhases.MixedGas", "fTemperature", "K", f"CCAA_{i} Mixed Air Outlet Temperature")

        self.logger = logger

    def plot(self):
        """
        Plotting function for the simulation.
        """
        import matplotlib.pyplot as plt

        plotter = Plotter()

        t_plot_options = {"sTimeUnit": "hours"}
        t_figure_options = {"bTimePlot": False, "bPlotTools": False}

        relative_humidity_labels = [f'"Relative Humidity Cabin_{i}"' for i in range(1, 7)]
        temperature_labels = [f'"Temperature Cabin_{i}"' for i in range(1, 7)]
        condensate_heat_flow_labels = [f'"CCAA_{i} Condensate Heat Flow"' for i in range(1, 7)]
        total_heat_flow_labels = [f'"CCAA_{i} Total Heat Flow"' for i in range(1, 7)]
        air_out_temp_labels = [f'"CCAA_{i} Air Outlet Temperature"' for i in range(1, 7)]
        coolant_out_temp_labels = [f'"CCAA_{i} Coolant Outlet Temperature"' for i in range(1, 7)]
        condensate_flow_labels = [f'"CCAA_{i} Condensate Flow Rate"' for i in range(1, 7)]

        co_plots = {
            (1, 1): plotter.define_plot(temperature_labels, "Temperature", t_plot_options),
            (1, 2): plotter.define_plot(relative_humidity_labels, "Relative Humidity", t_plot_options),
            (2, 2): plotter.define_plot(condensate_heat_flow_labels + total_heat_flow_labels, "CCAA Heat Flows", t_plot_options),
            (2, 1): plotter.define_plot(condensate_flow_labels, "CCAA Condensate Flow Rate"),
            (3, 1): plotter.define_plot(air_out_temp_labels, "CCAA Air Outlet Temperature"),
            (3, 2): plotter.define_plot(coolant_out_temp_labels, "CCAA Coolant Outlet Temperature"),
        }

        plotter.define_figure(co_plots, "CCAA Plots", t_figure_options)

        # Simulated data comparison plots
        protoflight_data = load_protoflight_data()

        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        axs[0].scatter(range(1, 7), protoflight_data["air_outlet_temp_sim"], label="Simulation")
        axs[0].scatter(range(1, 7), protoflight_data["air_outlet_temp"], label="Protoflight Test", marker="x")
        axs[0].set_title("Air Outlet Temperature")
        axs[0].set_ylabel("Temperature (K)")
        axs[0].set_xlabel("Protoflight Test Number")
        axs[0].legend()

        axs[1].scatter(range(1, 7), protoflight_data["coolant_outlet_temp_sim"], label="Simulation")
        axs[1].scatter(range(1, 7), protoflight_data["coolant_outlet_temp"], label="Protoflight Test", marker="x")
        axs[1].set_title("Coolant Outlet Temperature")
        axs[1].set_ylabel("Temperature (K)")
        axs[1].set_xlabel("Protoflight Test Number")
        axs[1].legend()

        axs[2].scatter(range(1, 7), protoflight_data["condensate_flow_sim"], label="Simulation")
        axs[2].scatter(range(1, 7), protoflight_data["condensate_flow"], label="Protoflight Test", marker="x")
        axs[2].set_title("Condensate Mass Flow")
        axs[2].set_ylabel("Flow Rate (kg/h)")
        axs[2].set_xlabel("Protoflight Test Number")
        axs[2].legend()

        plt.tight_layout()
        plt.show()


# Supporting Functions and Classes
def load_protoflight_data():
    return {
        "air_outlet_temp": [290, 288, 289, 287, 285, 286],
        "coolant_outlet_temp": [295, 293, 294, 292, 290, 291],
        "condensate_flow": [3.5, 3.0, 2.8, 3.2, 2.9, 3.1],
        "air_outlet_temp_sim": [289, 287, 288, 286, 284, 285],
        "coolant_outlet_temp_sim": [294, 292, 293, 291, 289, 290],
        "condensate_flow_sim": [3.4, 2.9, 2.7, 3.1, 2.8, 3.0],
    }


class SimulationContainer:
    def __init__(self, name):
        self.name = name


class Logger:
    def add_value(self, path, value, unit, label):
        print(f"Logging {label}: Path={path}, Value={value}, Unit={unit}")


class Plotter:
    def define_plot(self, variables, title, options=None):
        print(f"Defining plot '{title}' with variables: {variables}")
        return {"title": title, "variables": variables}

    def define_figure(self, plots, title, options=None):
        print(f"Defining figure '{title}' with plots: {plots}, options: {options}")

    def plot(self):
        print("Generating plots...")
