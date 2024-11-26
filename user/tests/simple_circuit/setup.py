class Setup(simulation.infrastructure):
    """
    Setup class for the Test_Simple_Circuit simulation.
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
        super().__init__('Test_Simple_Circuit', ptConfigParams, tSolverParams, ttMonitorConfig or {})

        # Instantiate the Example system
        tutorials.simple_circuit.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation length
        self.fSimTime = fSimTime if fSimTime is not None else 100

        # Log value storage
        self.ciLogValues = []

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        oLog = self.toMonitors.oLogger

        # Adding electrical properties of the Example system to the log
        self.ciLogValues = oLog.add('Example', 'electricalProperties')

    def plot(self):
        """
        Define and generate plots for the simulation results.
        """
        # Get the plotter object
        oPlotter = super().plot()

        # Voltage plot
        tPlotOptions = {}
        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(self.ciLogValues, 'Voltages', tPlotOptions)

        # Current plot
        coPlots[2, 1] = oPlotter.definePlot(self.ciLogValues, 'Currents', tPlotOptions)

        # Define figure
        oPlotter.defineFigure(coPlots, 'Results')

        # Generate plots
        oPlotter.plot()
