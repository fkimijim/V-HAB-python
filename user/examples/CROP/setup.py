class Setup(simulation.infrastructure):
    """
    Setup class for the CROP model simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams):
        """
        Constructor for the Setup class.
        """
        ttMonitorCfg = {}
        super().__init__('CROP_Example', ptConfigParams, tSolverParams, ttMonitorCfg)

        # Define compound mass for urine
        trBaseCompositionUrine = {'H2O': 0.9644, 'CH4N2O': 0.0356}
        self.oSimulationContainer.oMT.defineCompoundMass(self, 'Urine', trBaseCompositionUrine)

        # Create the CROP system
        examples.CROP.system.Example(self.oSimulationContainer, 'Example')

        # Simulation length
        self.fSimTime = 100 * 24 * 3600  # 100 days in seconds
        self.iSimTicks = 200
        self.bUseTime = True

        # Logging indexes
        self.tiLogIndexes = {}

    def configureMonitors(self):
        """
        Configure the monitors and loggers.
        """
        oLogger = self.toMonitors.oLogger

        # Add simulation timestep
        oLogger.addValue('Example.oTimer', 'fTimeStepFinal', 's', 'Timestep')

        for iCROP in range(1, self.oSimulationContainer.toChildren.Example.iChildren + 1):
            sCROP = f"CROP_{iCROP}"

            # Add values for logging
            oLogger.addValue(f"Example:c:{sCROP}:s:CROP_Tank.toPhases.TankSolution", 'fMass', 'kg', f"{sCROP} CROP Tank Mass")
            oLogger.addValue(f"Example:c:{sCROP}.toBranches.CROP_Calcite_Inlet", 'fFlowRate', 'kg/s', f"{sCROP} CROP Calcite Inlet")

            self.tiLogIndexes[f"mfPH_{iCROP}"] = oLogger.addValue(
                f"Example:c:{sCROP}:s:CROP_BioFilter.toPhases.BioPhase.toManips.substance", 'fpH', '-', f"{sCROP} BioFilter pH"
            )

            substances = ['CH4N2O', 'NH3', 'NH4', 'NO3', 'NO2', 'CO2', 'Ca2plus', 'CO3']
            for substance in substances:
                self.tiLogIndexes[f"mf{substance}_{iCROP}"] = oLogger.addValue(
                    f"Example:c:{sCROP}:s:CROP_Tank.toPhases.TankSolution", f"afMass(this.oMT.tiN2I.{substance})", 'kg', f"{sCROP} Tank {substance} Mass"
                )

            self.tiLogIndexes[f"mfCaCO3_{iCROP}"] = oLogger.addValue(
                f"Example:c:{sCROP}:s:CROP_Tank.toPhases.Calcite", f"afMass(this.oMT.tiN2I.CaCO3)", 'kg', f"{sCROP} Tank CaCO3 Mass"
            )

            # Add enzyme reaction flow rates
            reactions = ['CH4N2O', 'NH3', 'NH4', 'NO3', 'NO2', 'O2', 'H2O', 'CO2']
            for reaction in reactions:
                self.tiLogIndexes[f"mf{reaction}flow_{iCROP}"] = oLogger.addValue(
                    f"Example:c:{sCROP}:s:CROP_BioFilter.toPhases.BioPhase.toManips.substance", f"afPartialFlows(this.oMT.tiN2I.{reaction})", 'kg/s', f"{sCROP} Enzyme Reaction {reaction}"
                )

            # Gas exchange and dissolution logging
            exchanges = ['NH3', 'CO2', 'O2']
            for exchange in exchanges:
                self.tiLogIndexes[f"mf{exchange}gasex_{iCROP}"] = oLogger.addValue(
                    f"Example:c:{sCROP}:s:CROP_Tank.toProcsP2P.{exchange}_Outgassing_Tank", 'fFlowRate', 'kg/s', f"{sCROP} {exchange} gas exchange"
                )

            self.tiLogIndexes[f"mfCalcitecum_{iCROP}"] = oLogger.addValue(
                f"Example:s:CalciteSupply.toPhases.CalciteSupply", 'this.afMassChange(this.oMT.tiN2I.CaCO3)', 'kg', f"Total consumed Calcite Mass"
            )

    def plot(self):
        """
        Define and display plots for the simulation results.
        """
        try:
            self.toMonitors.oLogger.readFromMat()
        except Exception:
            print('No data outputted yet.')

        oPlotter = super().plot()
        tPlotOptions = {'sTimeUnit': 'hours'}

        # Define plots for pH and various masses
        coPlots = {
            (1, 1): oPlotter.definePlot([self.tiLogIndexes[f"mfPH_{i}"] for i in range(1, 8)], 'pH Value', tPlotOptions),
            (1, 2): oPlotter.definePlot([self.tiLogIndexes[f"mfCH4N2O_{i}"] for i in range(1, 8)], 'Urea', tPlotOptions),
            (1, 3): oPlotter.definePlot([self.tiLogIndexes[f"mfNH3_{i}"] for i in range(1, 8)], 'NH3', tPlotOptions),
        }

        oPlotter.defineFigure(coPlots, 'CROP Masses and pH')
        oPlotter.plot()

        # Load and plot test data comparison
        test_data = loadmat('+examples/+CROP/+TestData/Data_Experiment.mat')['Data_Modified']
        csSeries = ['C', 'A', 'B', 'D', 'E', 'F', 'G']

        fig, axs = plt.subplots(3, 7, figsize=(20, 10))

        for i, series in enumerate(csSeries):
            for j, metric in enumerate(['b', 'c', 'd']):
                axs[j, i].set_title(f"{test_data[series]['UreaPercent']}% Urea {metric}")
                axs[j, i].scatter(test_data[series][metric][:, 0], test_data[series][metric][:, 1:])
                axs[j, i].set_xlabel('Time (d)')
                axs[j, i].set_ylabel(f"{metric} Concentration (mmol/l)")
                axs[j, i].grid(True)

        plt.tight_layout()
        plt.show()
