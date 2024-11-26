class Setup(simulation.infrastructure):
    """
    Setup class for the Test_Simple_Flow simulation.
    - Instantiates the simulation.
    - Configures logging for relevant values.
    - Defines simulation duration.
    - Provides methods for plotting results.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor for the Setup class.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration (optional).
            fSimTime: Simulation time in seconds (optional).
        """
        super().__init__('Test_Simple_Flow', ptConfigParams, tSolverParams, ttMonitorConfig or {})

        # Instantiate the Example system
        tutorials.simple_flow.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation duration (default: 3600 seconds)
        self.fSimTime = fSimTime if fSimTime is not None else 3600

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        oLogger = self.toMonitors.oLogger

        # Adding temperatures to the log
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'fTemperature', 'K', 'Temperature Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'fTemperature', 'K', 'Temperature Phase 2')

        # Adding pressures to the log
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2')

        # Adding branch flow rate to the log
        oLogger.addValue('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate')

    def plot(self):
        """
        Define and generate plots for the simulation results.
        """
        # Get the plotter object
        oPlotter = super().plot()

        # Define plots
        coPlots = {
            (1, 1): oPlotter.definePlot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures'),
            (1, 2): oPlotter.definePlot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure'),
            (2, 1): oPlotter.definePlot(['"Branch Flow Rate"'], 'Flowrate'),
        }

        # Define figure with time plot enabled
        oPlotter.defineFigure(coPlots, 'Tank Temperatures', {'bTimePlot': True})

        # Generate plots
        oPlotter.plot()
