class Setup(simulation.infrastructure):
    """
    Setup class for Test Monitors simulation.
    Handles:
    - Instantiating the root object.
    - Configuring monitors and logging.
    - Setting simulation duration.
    - Providing methods for plotting results.
    """

    def __init__(self, ptConfigParams=None, tSolverParams=None, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor for the Setup class.

        Args:
            ptConfigParams: Configuration parameters for the simulation.
            tSolverParams: Solver parameters for the simulation.
            ttMonitorConfig: Monitor configuration for logging.
            fSimTime: Simulation time duration (in seconds).
        """
        # Initialize monitor configurations
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        # Logger monitor configuration for dumping and pre-allocation
        ttMonitorConfig['oLogger'] = {'cParams': [True, 100000]}

        # Time step observer monitor (use for debugging, slows down simulation)
        ttMonitorConfig['oTimeStepObserver'] = {
            'sClass': 'simulation.monitors.timestepObserver',
            'cParams': [0],
        }

        # Mass balance observer monitor configuration
        fAccuracy = 1e-8
        fMaxMassBalanceDifference = float('inf')
        bSetBreakPoints = False
        ttMonitorConfig['oMassBalanceObserver'] = {
            'sClass': 'simulation.monitors.massbalanceObserver',
            'cParams': [fAccuracy, fMaxMassBalanceDifference, bSetBreakPoints],
        }

        # Call the parent constructor with the simulation name
        super().__init__('Test_Monitors', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Create the 'Example' system as a child of the simulation container
        tutorials.simple_flow.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation duration (default: 1 hour in seconds)
        self.fSimTime = 3600 if fSimTime is None or not fSimTime else fSimTime

    def configure_monitors(self):
        """
        Configure the logging monitors for the simulation.
        """
        # Local variable for the logger object
        oLogger = self.toMonitors.oLogger

        # Log tank temperatures
        oLogger.add_value('Example:s:Tank_1:p:Tank_1_Phase_1', 'fTemperature', 'K', 'Temperature Phase 1')
        oLogger.add_value('Example:s:Tank_2:p:Tank_2_Phase_1', 'fTemperature', 'K', 'Temperature Phase 2')

        # Log tank pressures
        oLogger.add_value(
            'Example:s:Tank_1:p:Tank_1_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1'
        )
        oLogger.add_value(
            'Example:s:Tank_2:p:Tank_2_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2'
        )

        # Log branch flow rate
        oLogger.add_value('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate')

    def plot(self):
        """
        Plot the results of the simulation.
        """
        import matplotlib.pyplot as plt

        # Close existing plots
        plt.close('all')

        # Get the plotter object for the simulation
        oPlotter = super().plot()

        # Define plots
        coPlots = {
            (1, 1): oPlotter.define_plot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures'),
            (1, 2): oPlotter.define_plot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure'),
            (2, 1): oPlotter.define_plot(['"Branch Flow Rate"'], 'Flowrate'),
        }

        # Create a figure containing the defined plots
        oPlotter.define_figure(coPlots, 'Tank Temperatures', {'bTimePlot': True})

        # Generate the plots
        oPlotter.plot()
