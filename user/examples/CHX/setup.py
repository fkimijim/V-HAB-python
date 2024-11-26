class Setup:
    """
    SETUP class used to set up a simulation.
    It performs the following tasks:
    - Instantiates the root object.
    - Registers branches to their appropriate solvers.
    - Determines which items are logged.
    - Sets the simulation duration.
    - Provides methods for plotting the results.
    """

    def __init__(self, ptConfigParams, tSolverParams):
        """
        Constructor function to initialize the setup.
        """
        # Possible to change the constructor paths and params for the monitors
        ttMonitorConfig = {
            "oTimeStepObserver": {
                "sClass": "simulation.monitors.timestepObserver",
                "cParams": [0],
            }
        }

        self.simulation_name = "Example_Condensing_Heat_Exchanger"
        self.ptConfigParams = ptConfigParams
        self.tSolverParams = tSolverParams
        self.ttMonitorConfig = ttMonitorConfig

        # Creating the root object
        self.oSimulationContainer = SimulationContainer(
            self.simulation_name, ptConfigParams, tSolverParams, ttMonitorConfig
        )
        self.example = Example(self.oSimulationContainer, "Example")

        # Simulation length
        self.fSimTime = 3600 * 1  # In seconds
        self.bUseTime = True

    def configure_monitors(self):
        """
        Configures the logging for the simulation.
        """
        oLog = self.oSimulationContainer.toMonitors.oLogger
        sLogValueHumidity = (
            "self.oMT.convertHumidityToDewpoint(self.rRelHumidity, self.fTemperature)"
        )

        # Add values to log
        oLog.add_value(
            "Example", "toProcsF2F.CondensingHeatExchanger_1.fHeatFlow", "W", "Heat Flow Air"
        )
        oLog.add_value(
            "Example", "toProcsF2F.CondensingHeatExchanger_2.fHeatFlow", "W", "Heat Flow Coolant"
        )
        oLog.add_value(
            "Example:s:CHX.toProcsP2P.CondensingHX", "fFlowRate", "kg/s", "Condensate Flow Rate"
        )
        oLog.add_value(
            "Example:s:Cabin.toPhases.Air", "rRelHumidity", "-", "Relative Humidity Cabin"
        )
        oLog.add_value(
            "Example:s:Cabin.toPhases.Air", "fTemperature", "K", "Temperature Cabin"
        )
        oLog.add_value(
            "Example:s:Cabin.toPhases.Air", sLogValueHumidity, "K", "Dew Point Cabin"
        )
        oLog.add_value(
            "Example:s:Coolant.toPhases.Water", "fTemperature", "K", "Temperature Coolant"
        )

    def plot(self):
        """
        Plots the results of the simulation.
        """
        import matplotlib.pyplot as plt

        # Close any existing plots
        plt.close("all")

        oPlotter = Plotter(self.oSimulationContainer)

        # Define individual plots
        coPlot = [[None for _ in range(2)] for _ in range(2)]
        coPlot[0][0] = oPlotter.define_plot(
            ["Heat Flow Air", "Heat Flow Coolant"], "Heat Flows"
        )
        coPlot[0][1] = oPlotter.define_plot(
            ["Temperature Cabin", "Temperature Coolant", "Dew Point Cabin"], "Temperatures"
        )
        coPlot[1][0] = oPlotter.define_plot(["Relative Humidity Cabin"], "Relative Humidity")
        coPlot[1][1] = oPlotter.define_plot(["Condensate Flow Rate"], "Condensate Flowrate")

        # Define a single figure with multiple plots
        oPlotter.define_figure(coPlot, "Condensing Heat Exchanger")

        # Generate plots
        oPlotter.plot()


class SimulationContainer:
    """
    A simplified simulation container for managing simulation infrastructure.
    """
    def __init__(self, name, ptConfigParams, tSolverParams, ttMonitorConfig):
        self.name = name
        self.ptConfigParams = ptConfigParams
        self.tSolverParams = tSolverParams
        self.ttMonitorConfig = ttMonitorConfig
        self.toMonitors = MonitorContainer()


class MonitorContainer:
    """
    A simplified monitor container for logging and observing simulation data.
    """
    def __init__(self):
        self.oLogger = Logger()


class Logger:
    """
    A simplified logger class for simulation logging.
    """
    def __init__(self):
        self.logs = []

    def add_value(self, location, variable, unit, description):
        self.logs.append({
            "location": location,
            "variable": variable,
            "unit": unit,
            "description": description,
        })


class Plotter:
    """
    A simplified plotter for simulation results.
    """
    def __init__(self, simulation_container):
        self.simulation_container = simulation_container

    def define_plot(self, variables, title):
        return {"variables": variables, "title": title}

    def define_figure(self, plots, title):
        self.figure_title = title
        self.plots = plots

    def plot(self):
        for row in self.plots:
            for plot in row:
                if plot:
                    print(f"Plotting: {plot['title']} with variables {plot['variables']}")
