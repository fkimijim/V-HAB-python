class Setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams):
        super().__init__('Tutorial_ReconnectingExMe', ptConfigParams, tSolverParams)

        # Instantiate the Example system
        tutorials.reconnectingExMe.systems.Example(self.oSimulationContainer, 'Example')

        self.iSimTicks = 2000
        self.bUseTime = False

    def configureMonitors(self):
        oLog = self.toMonitors.oLogger

        # Log data for each store
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for iStore in csStores:
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "this.fMass * this.fMassToPressure",
                "Pa",
                f"{iStore} Pressure"
            )
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "this.afPP(this.oMT.tiN2I.O2)",
                "Pa",
                f"{iStore} O2 Pressure"
            )
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "this.afPP(this.oMT.tiN2I.CO2)",
                "Pa",
                f"{iStore} CO2 Pressure"
            )
            oLog.addValue(
                f"Example.toStores.{iStore}.aoPhases(1)",
                "fTemperature",
                "K",
                f"{iStore} Temperature"
            )

        # Log data for each branch
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for iBranch in csBranches:
            oLog.addValue(
                f"Example.toBranches.{iBranch}",
                "fFlowRate",
                "kg/s",
                f"{iBranch} Flowrate"
            )

    def plot(self, *args):
        import matplotlib.pyplot as plt

        plt.close("all")
        oPlotter = super().plot()

        # Prepare data for plots
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csO2 = [f'"{store} O2 Pressure"' for store in csStores]
        csCO2 = [f'"{store} CO2 Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        # Plot configuration
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        coPlots = {
            (1, 1): oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions),
            (1, 2): oPlotter.definePlot(csO2, 'O2 Pressures', tPlotOptions),
            (1, 3): oPlotter.definePlot(csCO2, 'CO2 Pressures', tPlotOptions),
            (2, 1): oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions),
            (2, 2): oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions),
        }

        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)
        oPlotter.plot()
