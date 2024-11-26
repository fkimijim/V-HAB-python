class Setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams):
        """
        Constructor for the Setup class.
        
        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
        """
        ttMonitorConfig = {}
        super().__init__('Tutorial_Manipulator', ptConfigParams, tSolverParams, ttMonitorConfig)
        tutorials.manipulator.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation length
        self.fSimTime = 2000  # In seconds
        self.iSimTicks = 600
        self.bUseTime = True

    def configureMonitors(self):
        """
        Configure logging monitors for the simulation.
        """
        oLog = self.toMonitors.oLogger

        # Log pressures and temperatures for all stores
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        for iStore in csStores:
            oLog.addValue(f"Example.toStores.{iStore}.aoPhases(1)", "this.fMass * this.fMassToPressure", "Pa", f"{iStore} Pressure")
            oLog.addValue(f"Example.toStores.{iStore}.aoPhases(1)", "fTemperature", "K", f"{iStore} Temperature")

        # Log flow rates for all branches
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        for iBranch in csBranches:
            oLog.addValue(f"Example.toBranches.{iBranch}", "fFlowRate", "kg/s", f"{iBranch} Flowrate")

        # Log specific values related to the Bosch Reactor
        oLog.addValue("Example:s:Reactor.toProcsP2P.FilterProc", "fFlowRate", "kg/s", "P2P Flow Rate")
        oLog.addValue("Example:s:Reactor.toPhases.FlowPhase.toManips.substance", "afPartialFlows(this.oMT.tiN2I.O2)", "kg/s", "Bosch O2 Flow Rate")
        oLog.addValue("Example:s:Reactor.toPhases.FlowPhase.toManips.substance", "afPartialFlows(this.oMT.tiN2I.CO2)", "kg/s", "Bosch CO2 Flow Rate")
        oLog.addValue("Example:s:Reactor.toPhases.FlowPhase.toManips.substance", "afPartialFlows(this.oMT.tiN2I.C)", "kg/s", "Bosch C Flow Rate")

    def plot(self):
        """
        Define and plot results of the simulation.
        """
        import matplotlib.pyplot as plt

        # Close all existing plots
        plt.close('all')

        oPlotter = super().plot()

        # Define plots
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        csBoschReactorFlows = ['"P2P Flow Rate"', '"Bosch O2 Flow Rate"', '"Bosch CO2 Flow Rate"', '"Bosch C Flow Rate"']

        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        coPlots = {}
        coPlots[(1, 1)] = oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)
        coPlots[(2, 1)] = oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)
        coPlots[(1, 2)] = oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)
        coPlots[(2, 2)] = oPlotter.definePlot(csBoschReactorFlows, 'Bosch Reactor Flowrates', tPlotOptions)

        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)

        # Generate plots
        oPlotter.plot()
