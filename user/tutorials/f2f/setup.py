class Setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams):
        super().__init__('Tutorial_f2f', ptConfigParams, tSolverParams)

        # Create the Example system as a child of the simulation container
        tutorials.f2f.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation length settings
        self.fSimTime = 3600 * 3  # Simulation time in seconds
        self.iSimTicks = 1500  # Number of simulation ticks
        self.bUseTime = True  # Use simulation time instead of ticks

    def configureMonitors(self):
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

    def plot(self, *args):
        import matplotlib.pyplot as plt
        plt.close('all')  # Close all existing figures
        oPlotter = super().plot()

        # Prepare data for plots
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{iStore} Pressure"' for iStore in csStores]
        csTemperatures = [f'"{iStore} Temperature"' for iStore in csStores]

        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{iBranch} Flowrate"' for iBranch in csBranches]

        # Plot options
        tPlotOptions = {"sTimeUnit": "seconds"}
        tFigureOptions = {"bTimePlot": False, "bPlotTools": False}

        # Define plots
        coPlots = {}
        coPlots[(1, 1)] = oPlotter.definePlot(csPressures, "Pressures", tPlotOptions)
        coPlots[(2, 1)] = oPlotter.definePlot(csFlowRates, "Flow Rates", tPlotOptions)
        coPlots[(1, 2)] = oPlotter.definePlot(csTemperatures, "Temperatures", tPlotOptions)

        # Define figure
        oPlotter.defineFigure(coPlots, "Plots", tFigureOptions)

        # Generate plots
        oPlotter.plot()
