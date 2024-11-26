class Setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams, fSimTime=None):
        ttMonitorCfg = {}
        super().__init__('Tutorial_p2p', ptConfigParams, tSolverParams, ttMonitorCfg)

        # Add the Example system
        tutorials.p2p.stationary.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation length
        self.fSimTime = 5000
        if fSimTime is not None:
            self.fSimTime = fSimTime

        self.bUseTime = True

    def configureMonitors(self):
        oLog = self.toMonitors.oLogger

        csStores = list(self.oSimulationContainer.toChildren['Example'].toStores.keys())
        for iStore in range(len(csStores)):
            store_name = csStores[iStore]
            iPhase = 2 if store_name == 'Filter' else 1

            oLog.addValue(
                f"Example.toStores.{store_name}.aoPhases({iPhase})",
                "this.fMass * this.fMassToPressure",
                "Pa",
                f"{store_name} Pressure",
            )
            oLog.addValue(
                f"Example.toStores.{store_name}.aoPhases({iPhase})",
                "this.afPP(this.oMT.tiN2I.CO2)",
                "Pa",
                f"{store_name} CO2 Pressure",
            )
            oLog.addValue(
                f"Example.toStores.{store_name}.aoPhases({iPhase})",
                "this.afPP(this.oMT.tiN2I.H2O)",
                "Pa",
                f"{store_name} H2O Pressure",
            )
            oLog.addValue(
                f"Example.toStores.{store_name}.aoPhases({iPhase})",
                "fTemperature",
                "K",
                f"{store_name} Temperature",
            )

        oLog.addValue(
            "Example.toStores.Filter.toPhases.FilteredPhase",
            "this.afMass(this.oMT.tiN2I.CO2)",
            "kg",
            "Adsorbed CO2",
        )
        oLog.addValue(
            "Example.toStores.Filter.toPhases.FilteredPhase",
            "this.afMass(this.oMT.tiN2I.H2O)",
            "kg",
            "Adsorbed H2O",
        )

        csBranches = list(self.oSimulationContainer.toChildren['Example'].toBranches.keys())
        for iBranch in range(len(csBranches)):
            branch_name = csBranches[iBranch]
            oLog.addValue(
                f"Example.toBranches.{branch_name}",
                "fFlowRate",
                "kg/s",
                f"{branch_name} Flowrate",
            )

    def plot(self):
        import matplotlib.pyplot as plt

        plt.close('all')
        oPlotter = super().plot()

        csStores = list(self.oSimulationContainer.toChildren['Example'].toStores.keys())
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]
        csCO2 = [f'"{store} CO2 Pressure"' for store in csStores]
        csH2O = [f'"{store} H2O Pressure"' for store in csStores]

        csBranches = list(self.oSimulationContainer.toChildren['Example'].toBranches.keys())
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        tPlotOptions = {"sTimeUnit": "seconds"}
        tFigureOptions = {"bTimePlot": False, "bPlotTools": False}

        coPlots = [
            [oPlotter.definePlot(csPressures, "Pressures", tPlotOptions)],
            [oPlotter.definePlot(csFlowRates, "Flow Rates", tPlotOptions)],
            [oPlotter.definePlot(['"Adsorbed CO2"', '"Adsorbed H2O"'], "Adsorbed Masses", tPlotOptions)],
            [oPlotter.definePlot(csCO2, "CO2", tPlotOptions)],
            [oPlotter.definePlot(csH2O, "H2O", tPlotOptions)],
            [oPlotter.definePlot(csTemperatures, "Temperatures", tPlotOptions)],
        ]

        oPlotter.defineFigure(coPlots, "Plots", tFigureOptions)
        oPlotter.plot()
