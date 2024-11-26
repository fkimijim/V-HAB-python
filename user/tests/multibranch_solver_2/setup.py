class Setup(simulation.infrastructure):
    """
    Setup class for Test_Solver_MultiBranch_2 simulation.
    """

    def __init__(self, ptConfigParams=None, tSolverParams=None, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor function for the Setup class.
        """
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        super().__init__('Test_Solver_MultiBranch_2', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Creating the 'Example' system as a child of the root system
        tests.multibranch_solver_2.systems.Example_2(self.oSimulationContainer, 'Example')

        # Simulation length
        if fSimTime is None or fSimTime == []:
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
        Configures the monitors for the simulation.
        """
        oConsOut = self.toMonitors.oConsoleOutput

        # Uncomment and customize the following lines for detailed console output debugging:
        # oConsOut.setLogOn().setVerbosity(3)
        # oConsOut.addMethodFilter('updatePressure')
        # oConsOut.addMethodFilter('massupdate')

        # Set minimum simulation step size
        self.oSimulationContainer.oTimer.setMinStep(1e-16)

        # Logging configuration
        oLog = self.toMonitors.oLogger

        # Log values for stores
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        for iStore in csStores:
            oLog.addValue(
                f'Example.toStores.{iStore}.aoPhases(1)',
                'this.fMass * this.fMassToPressure',
                'Pa',
                f'{iStore} Pressure'
            )
            oLog.addValue(
                f'Example.toStores.{iStore}.aoPhases(1)',
                'fTemperature',
                'K',
                f'{iStore} Temperature'
            )

        # Log values for branches
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        for iBranch in csBranches:
            oLog.addValue(
                f'Example.toBranches.{iBranch}',
                'fFlowRate',
                'kg/s',
                f'{iBranch} Flowrate'
            )

    def plot(self):
        """
        Plots the simulation results.
        """
        # Define Plots
        oPlotter = plot.simulation.infrastructure(self)

        # Configure store logs for plotting
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{iStore} Pressure"' for iStore in csStores]
        csTemperatures = [f'"{iStore} Temperature"' for iStore in csStores]

        # Configure branch logs for plotting
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{iBranch} Flowrate"' for iBranch in csBranches]

        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)
        coPlots[2, 1] = oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)
        coPlots[1, 2] = oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)

        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)
        oPlotter.plot()
