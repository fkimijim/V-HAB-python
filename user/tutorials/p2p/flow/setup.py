class Setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams):
        """
        Initialize the simulation setup.
        """
        ttMonitorConfig = {}
        super().__init__('Tutorial_p2p', ptConfigParams, tSolverParams, ttMonitorConfig)

        tutorials.p2p.flow.systems.Example(self.oSimulationContainer, 'Example')

        self.fSimTime = 2000
        self.bUseTime = True

    def configureMonitors(self):
        """
        Configure the simulation monitors and loggers.
        """
        oLog = self.toMonitors.oLogger

        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for iStore in range(len(csStores)):
            oLog.addValue(
                f"Example.toStores.{csStores[iStore]}.aoPhases[0]",
                "self.fMass * self.fMassToPressure",
                "Pa",
                f"{csStores[iStore]} Pressure",
            )
            oLog.addValue(
                f"Example.toStores.{csStores[iStore]}.aoPhases[0]",
                "self.afPP(self.oMT.tiN2I.CO2)",
                "Pa",
                f"{csStores[iStore]} CO2 Pressure",
            )
            oLog.addValue(
                f"Example.toStores.{csStores[iStore]}.aoPhases[0]",
                "self.afPP(self.oMT.tiN2I.H2O)",
                "Pa",
                f"{csStores[iStore]} H2O Pressure",
            )
            oLog.addValue(
                f"Example.toStores.{csStores[iStore]}.aoPhases[0]",
                "fTemperature",
                "K",
                f"{csStores[iStore]} Temperature",
            )

        oLog.addValue(
            "Example.toStores.Filter.toPhases.FilteredPhase",
            "self.afMass(self.oMT.tiN2I.CO2)",
            "kg",
            "Adsorbed CO2",
        )
        oLog.addValue(
            "Example.toStores.Filter.toPhases.FilteredPhase",
            "self.afMass(self.oMT.tiN2I.H2O)",
            "kg",
            "Adsorbed H2O",
        )

        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for iBranch in range(len(csBranches)):
            oLog.addValue(
                f"Example.toBranches.{csBranches[iBranch]}",
                "fFlowRate",
                "kg/s",
                f"{csBranches[iBranch]} Flowrate",
            )

    def plot(self):
        """
        Define and generate simulation plots.
        """
        import matplotlib.pyplot as plt

        plt.close('all')
        oPlotter = super().plot()

        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]
        csCO2 = [f'"{store} CO2 Pressure"' for store in csStores]
        csH2O = [f'"{store} H2O Pressure"' for store in csStores]

        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)
        coPlots[2, 2] = oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)
        coPlots[1, 2] = oPlotter.definePlot(
            ['"Adsorbed CO2"', '"Adsorbed H2O"'], 'Adsorbed Masses', tPlotOptions
        )
        coPlots[2, 1] = oPlotter.definePlot(csCO2, 'CO2', tPlotOptions)
        coPlots[3, 1] = oPlotter.definePlot(csH2O, 'H2O', tPlotOptions)
        coPlots[3, 2] = oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)

        oPlotter.plot()
