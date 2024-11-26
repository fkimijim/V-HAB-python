class Setup(simulation.infrastructure):
    """
    Setup class for the Test_Solver_MultiBranch_4 simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor function.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration.
            fSimTime: Simulation time in seconds.
        """
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        super().__init__('Test_Solver_MultiBranch_4', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Initialize the Example_4 system
        tests.multibranch_solver_4.systems.Example_4(self.oSimulationContainer, 'Example')

        # Set simulation length
        if fSimTime is None or fSimTime == 0:
            fSimTime = 3600 * 5

        if fSimTime < 0:
            self.fSimTime = 3600
            self.iSimTicks = abs(fSimTime)
            self.bUseTime = False
        else:
            self.fSimTime = fSimTime  # In seconds
            self.iSimTicks = 1950
            self.bUseTime = True

    def configureMonitors(self):
        """
        Configure monitors for the simulation.
        """
        oConsOut = self.toMonitors.oConsoleOutput

        # Example of adding debug filters (commented out in original)
        # oConsOut.setLogOn().setVerbosity(3)
        # oConsOut.addMethodFilter('updatePressure')
        # oConsOut.addMethodFilter('massupdate')

        # Set the minimum step for the simulation timer
        self.oSimulationContainer.oTimer.setMinStep(1e-16)

        # Configure logging
        oLog = self.toMonitors.oLogger

        # Log store-related data
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for iStore in csStores:
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "this.fMass * this.fMassToPressure",
                "Pa",
                f"{iStore} Pressure",
            )
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "fTemperature",
                "K",
                f"{iStore} Temperature",
            )

        # Log branch-related data
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for iBranch in csBranches:
            oLog.addValue(
                f"Example.toBranches.{iBranch}",
                "fFlowRate",
                "kg/s",
                f"{iBranch} Flowrate",
            )

    def plot(self):
        """
        Plot the simulation results.
        """
        # Initialize the plotter
        oPlotter = super().plot()

        # Prepare plots
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{iStore} Pressure"' for iStore in csStores]
        csTemperatures = [f'"{iStore} Temperature"' for iStore in csStores]

        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{iBranch} Flowrate"' for iBranch in csBranches]

        tPlotOptions = {"sTimeUnit": "seconds"}
        tFigureOptions = {"bTimePlot": False, "bPlotTools": False}

        # Define plots
        coPlots = {
            (1, 1): oPlotter.definePlot(csPressures, "Pressures", tPlotOptions),
            (2, 1): oPlotter.definePlot(csFlowRates, "Flow Rates", tPlotOptions),
            (1, 2): oPlotter.definePlot(csTemperatures, "Temperatures", tPlotOptions),
        }

        # Define figure and plot
        oPlotter.defineFigure(coPlots, "Plots", tFigureOptions)
        oPlotter.plot()
