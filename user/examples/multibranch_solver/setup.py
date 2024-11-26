class Setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams):
        # Initialize the parent class with configuration
        ttMonitorConfig = {}
        super().__init__('Example_Fan_Loop_Flow', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Create the Example system under the simulation container
        examples.multibranch_solver.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation time and ticks
        self.fSimTime = 1800 * 1  # Simulation time in seconds
        self.iSimTicks = 600      # Number of simulation ticks
        self.bUseTime = True      # Use time-based stopping condition

    def configure_monitors(self):
        """
        Configure the logging for the simulation.
        """
        oLog = self.toMonitors.oLogger
        oLog.add('Example', 'flowProperties')  # Log flow properties for the 'Example' system

    def plot(self, *args, **kwargs):
        """
        Generate plots for the simulation.
        """
        oPlotter = super().plot(*args, **kwargs)
        oPlotter.plot()
