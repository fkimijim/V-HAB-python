class Setup:
    """
    Setup class for the Equalizer Example simulation.
    """
    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig, fSimTime=None):
        """
        Initializes the Setup instance.
        """
        self.simulation_name = 'Equalizer_Example'
        self.ptConfigParams = ptConfigParams
        self.tSolverParams = tSolverParams
        self.ttMonitorConfig = ttMonitorConfig
        self.oSimulationContainer = SimulationContainer()
        self.toMonitors = Monitors()

        # Initialize the Example system
        Example(self.oSimulationContainer, 'Example')

        # Set simulation time
        if fSimTime is None or fSimTime == '':
            fSimTime = 3600
        self.fSimTime = fSimTime

    def configureMonitors(self):
        """
        Configures monitors for logging.
        """
        oLogger = self.toMonitors.oLogger

        # Adding the tank temperatures to the log
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'fTemperature', 'K', 'Temperature Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'fTemperature', 'K', 'Temperature Phase 2')

        # Adding the tank pressures to the log
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2')

        # Adding the branch flow rate to the log
        oLogger.addValue('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate')

    def plot(self):
        """
        Plots the logged data.
        """
        oPlotter = Plotter(self)
        coPlots = [[
            oPlotter.definePlot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures'),
            oPlotter.definePlot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure')
        ], [
            oPlotter.definePlot(['"Branch Flow Rate"'], 'Flowrate')
        ]]

        oPlotter.defineFigure(coPlots, 'Tank Temperatures', {'bTimePlot': True})
        oPlotter.plot()


# Supporting Classes
class SimulationContainer:
    """
    Represents the simulation container.
    """
    pass


class Monitors:
    """
    Represents monitors for logging.
    """
    def __init__(self):
        self.oLogger = Logger()


class Logger:
    """
    Represents the logger for recording simulation data.
    """
    def addValue(self, target, attribute, unit, description):
        print(f"Logging {description}: {target}.{attribute} [{unit}]")


class Plotter:
    """
    Represents the plotting utility.
    """
    def __init__(self, setup):
        self.setup = setup

    def definePlot(self, data_labels, title):
        """
        Defines a plot.
        """
        print(f"Defining plot '{title}' with data: {data_labels}")
        return {'data_labels': data_labels, 'title': title}

    def defineFigure(self, plots, title, options=None):
        """
        Defines a figure with multiple plots.
        """
        print(f"Defining figure '{title}' with options: {options}")

    def plot(self):
        """
        Executes plotting of all defined figures and plots.
        """
        print("Executing plotting...")
