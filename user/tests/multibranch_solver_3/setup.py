class Setup(simulation.infrastructure):
    """
    Setup class for Test_Solver_MultiBranch_3.
    Responsible for initializing, configuring monitors, and plotting the simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor for the Setup class.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration (default is None).
            fSimTime: Simulation time in seconds (default is 5 hours).
        """
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        super().__init__('Test_Solver_MultiBranch_3', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Initialize Example system
        tests.multibranch_solver_3.systems.Example_3(self.oSimulationContainer, 'Example')

        # Simulation length
        if fSimTime is None:
            fSimTime = 3600 * 5  # Default: 5 hours

        if fSimTime < 0:
            self.fSimTime = 3600
            self.iSimTicks = abs(fSimTime)
            self.bUseTime = False
        else:
            self.fSimTime = fSimTime  # Simulation duration in seconds
            self.iSimTicks = 1950
            self.bUseTime = True

    def configureMonitors(self):
        """
        Configures monitors for logging and other simulation observers.
        """
        oConsOut = self.toMonitors.oConsoleOutput

        # Console output monitor settings (commented out in original code)
        # oConsOut.setLogOn().setVerbosity(3)
        # oConsOut.addMethodFilter('updatePressure')
        # oConsOut.addMethodFilter('massupdate')
        # oConsOut.addIdentFilter('changing-boundary-conditions')

        # Minimum simulation step size
        self.oSimulationContainer.oTimer.setMinStep(1e-16)

        # Logging
        oLog = self.toMonitors.oLogger

        # Log store data
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        for csStore in csStores:
            oLog.addValue(f'Example.toStores.{csStore}.aoPhases(1)', 'this.fMass * this.fMassToPressure', 'Pa', f'{csStore} Pressure')
            oLog.addValue(f'Example.toStores.{csStore}.aoPhases(1)', 'fTemperature', 'K', f'{csStore} Temperature')

        # Log branch data
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        for csBranch in csBranches:
            oLog.addValue(f'Example.toBranches.{csBranch}', 'fFlowRate', 'kg/s', f'{csBranch} Flowrate')

    def plot(self):
        """
        Defines and plots simulation results.
        """
        # Close existing plots
        plt.close('all')

        # Initialize plotter
        oPlotter = super().plot()

        # Define data for plots
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{csStore} Pressure"' for csStore in csStores]
        csTemperatures = [f'"{csStore} Temperature"' for csStore in csStores]

        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{csBranch} Flowrate"' for csBranch in csBranches]

        # Plot options
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Define plots
        coPlots = {}
        coPlots[(1, 1)] = oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)
        coPlots[(2, 1)] = oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)
        coPlots[(1, 2)] = oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)

        # Create figure with defined plots
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)

        # Generate plots
        oPlotter.plot()
