class Setup(simulation.infrastructure):
    """
    Setup class for the Test_Simple_Thermal simulation.
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
        super().__init__('Test_Simple_Thermal', ptConfigParams, tSolverParams, ttMonitorConfig or {})

        # Instantiate the Example system
        tutorials.simple_thermal.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation duration (default: 3600 seconds)
        self.fSimTime = fSimTime if fSimTime is not None else 3600

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        oLogger = self.toMonitors.oLogger

        # Adding thermal properties to the log
        oLogger.add('Example', 'thermalProperties')

    def plot(self):
        """
        Define and generate plots for the simulation results.
        """
        # Get the plotter object
        oPlotter = super().plot()

        # If no plots are explicitly defined, produce a default plot with all values sorted by unit
        oPlotter.plot()
