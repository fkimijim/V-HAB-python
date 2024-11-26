class Setup(simulation.infrastructure):
    """
    Setup class for the Introduction_System simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams):
        # Initialize the parent simulation infrastructure
        ttMonitorConfig = {}
        super().__init__('Introduction_System', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Add the Example system to the simulation container
        yaka.introduction.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation length in seconds
        self.fSimTime = 3600  # 1 hour
        self.bUseTime = True

    def configureMonitors(self):
        """
        Configure monitors for logging values.
        """
        oLogger = self.toMonitors.oLogger

        # Add the total cabin pressure to the logger
        oLogger.addValue('Example.toStores.Cabin.toPhases.CabinAir', 'fPressure', 'Pa', 'Total Cabin Pressure')

    def plot(self):
        """
        Plot the simulation results.
        """
        # Close all currently open plots
        import matplotlib.pyplot as plt
        plt.close('all')

        # Attempt to load stored data
        try:
            self.toMonitors.oLogger.readDataFromMat()
        except Exception as e:
            print('No data outputted yet:', e)

        # Define plots
        oPlotter = super().plot()

        # Define a single plot for Total Cabin Pressure
        oPlot = [oPlotter.definePlot(['"Total Cabin Pressure"'], 'Total Cabin Pressure')]

        # Define a figure for the plot
        oPlotter.defineFigure(oPlot, 'Total Cabin Pressure')

        # Generate the plot
        oPlotter.plot()
