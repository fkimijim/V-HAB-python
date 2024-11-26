class setup(simulation.infrastructure):
    """
    Setup class for Test_Solver_MultiBranch_5.
    Defines the simulation configuration, logging, and plotting.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor for the setup class.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration (optional).
            fSimTime: Simulation time in seconds (optional).
        """
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        super().__init__('Test_Solver_MultiBranch_5', ptConfigParams, tSolverParams, ttMonitorConfig)

        tests.multibranch_solver_5.systems.Example_5(self.oSimulationContainer, 'Example')

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
        Configure the monitors for logging and console output.
        """
        oConsOut = self.toMonitors.oConsoleOutput

        # Uncomment the following block to enable console output filters:
        # oConsOut.setLogOn().setVerbosity(3)
        # oConsOut.addMethodFilter('updatePressure')
        # oConsOut.addMethodFilter('massupdate')
        # oConsOut.addIdentFilter('changing-boundary-conditions')
        # oConsOut.addIdentFilter('solve-flow-rates')
        # oConsOut.addIdentFilter('calc-fr')
        # oConsOut.addIdentFilter('set-fr')
        # oConsOut.addIdentFilter('total-fr')
        # oConsOut.addIdentFilter('negative-mass')
        # oConsOut.addTypeToFilter('matter.phases.gas_flow_node')

        # Set the minimum time step for the simulation timer
        self.oSimulationContainer.oTimer.setMinStep(1e-16)

        # Configure logging
        oLog = self.toMonitors.oLogger

        # Add logging for store pressures and temperatures
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for iStore in range(len(csStores)):
            storePath = f"Example.toStores.{csStores[iStore]}.aoPhases(1)"
            oLog.addValue(f"{storePath}", "this.fMass * this.fMassToPressure", "Pa", f"{csStores[iStore]} Pressure")
            oLog.addValue(f"{storePath}", "fTemperature", "K", f"{csStores[iStore]} Temperature")

        # Add logging for branch flow rates
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for iBranch in range(len(csBranches)):
            branchPath = f"Example.toBranches.{csBranches[iBranch]}"
            oLog.addValue(f"{branchPath}", "fFlowRate", "kg/s", f"{csBranches[iBranch]} Flowrate")

    def plot(self):
        """
        Plot the simulation results.
        """
        # Close all existing plots
        import matplotlib.pyplot as plt
        plt.close('all')

        # Create a plotter object
        oPlotter = super().plot()

        # Prepare plot data for pressures, temperatures, and flow rates
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{csStores[iStore]} Pressure"' for iStore in range(len(csStores))]
        csTemperatures = [f'"{csStores[iStore]} Temperature"' for iStore in range(len(csStores))]

        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{csBranches[iBranch]} Flowrate"' for iBranch in range(len(csBranches))]

        # Define plot options
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Create subplots
        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)
        coPlots[2, 1] = oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)
        coPlots[1, 2] = oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)

        # Define a figure with the subplots
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)

        # Plot the data
        oPlotter.plot()
