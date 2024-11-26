class Setup(simulation.infrastructure):
    """
    Setup class used to initialize and configure the simulation.
    - Instantiate the root object.
    - Register branches to their appropriate solvers.
    - Determine which items are logged.
    - Set the simulation duration.
    - Provide methods for plotting the results.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor function.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration (optional).
            fSimTime: Simulation time (optional).
        """
        super().__init__('Test_Performance', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Initialize the example system
        tests.performance_test.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation length
        if fSimTime is None:
            self.iSimTicks = 5000
            self.bUseTime = False
        else:
            self.fSimTime = fSimTime

    def configureMonitors(self):
        """
        Configure monitors for logging.
        """
        oLog = self.toMonitors.oLogger

        # Log pressures and temperatures of all stores
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        for iStore in csStores:
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "this.fMass * this.fMassToPressure",
                "Pa",
                f"{iStore} Pressure"
            )
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "fTemperature",
                "K",
                f"{iStore} Temperature"
            )

        # Log flow rates of all branches
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        for iBranch in csBranches:
            oLog.addValue(
                f"Example.toBranches.{iBranch}",
                "fFlowRate",
                "kg/s",
                f"{iBranch} Flowrate"
            )

    def plot(self):
        """
        Plot the results of the simulation.
        """
        # Close any open figures
        plt.close('all')

        # Create plotter object
        oPlotter = super().plot()

        # Define plots for pressures and temperatures
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        # Define plots for flow rates
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        # Plot options
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Define plots
        coPlots = {
            (1, 1): oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions),
            (2, 1): oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions),
            (1, 2): oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions),
        }

        # Define and plot figures
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)
        oPlotter.plot()
