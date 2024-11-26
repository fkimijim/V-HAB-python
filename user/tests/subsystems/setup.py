class Setup(simulation.infrastructure):
    """
    Setup class for the Test_Subsystems simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor for the Setup class.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration (optional).
            fSimTime: Simulation time in seconds (optional).
        """
        if "rHighestMaxChangeDecrease" not in tSolverParams:
            tSolverParams["rHighestMaxChangeDecrease"] = 500

        # Initialize the parent class
        super().__init__('Test_Subsystems', ptConfigParams, tSolverParams, ttMonitorConfig or {})

        # Creating the root object
        oExample = tutorials.subsystems.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation duration (default: 3600 seconds)
        self.fSimTime = fSimTime if fSimTime is not None else 3600

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        oLog = self.toMonitors.oLogger

        # Log values for the main Example system
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        for iStore in csStores:
            oLog.addValue(f"Example.toStores.{iStore}.aoPhases(1)", "this.fMass * this.fMassToPressure", "Pa", f"{iStore} Pressure")
            oLog.addValue(f"Example.toStores.{iStore}.aoPhases(1)", "fTemperature", "K", f"{iStore} Temperature")

        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        for iBranch in csBranches:
            oLog.addValue(f"Example.toBranches.{iBranch}", "fFlowRate", "kg/s", f"{iBranch} Flowrate")

        # Log values for the SubSystem
        csStoresSubSystem = self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toStores.keys()
        for iStore in csStoresSubSystem:
            oLog.addValue(f"Example:c:SubSystem.toStores.{iStore}.aoPhases(1)", "this.fMass * this.fMassToPressure", "Pa", f"{iStore} Pressure")
            oLog.addValue(f"Example:c:SubSystem.toStores.{iStore}.aoPhases(1)", "fTemperature", "K", f"{iStore} Temperature")

        csBranchesSubSystem = self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toBranches.keys()
        for iBranch in csBranchesSubSystem:
            oLog.addValue(f"Example:c:SubSystem.toBranches.{iBranch}", "fFlowRate", "kg/s", f"{iBranch} Flowrate")

    def plot(self, *args):
        """
        Define and generate plots for the simulation results.
        """
        from matplotlib import pyplot as plt
        plt.close('all')  # Close all existing plots

        oPlotter = super().plot()

        # Define plots for the main Example system
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        # Define plots for the SubSystem
        csStoresSubSystem = self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toStores.keys()
        csPressuresSubSystem = [f'"{store} Pressure"' for store in csStoresSubSystem]
        csTemperaturesSubSystem = [f'"{store} Temperature"' for store in csStoresSubSystem]

        csBranchesSubSystem = self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toBranches.keys()
        csFlowRatesSubSystem = [f'"{branch} Flowrate"' for branch in csBranchesSubSystem]

        tPlotOptions = {"sTimeUnit": "seconds"}
        tFigureOptions = {"bTimePlot": False, "bPlotTools": False}

        coPlots = {}
        coPlots[(1, 1)] = oPlotter.definePlot(csPressures + csPressuresSubSystem, "Pressures", tPlotOptions)
        coPlots[(2, 1)] = oPlotter.definePlot(csFlowRates + csFlowRatesSubSystem, "Flow Rates", tPlotOptions)
        coPlots[(1, 2)] = oPlotter.definePlot(csTemperatures + csTemperaturesSubSystem, "Temperatures", tPlotOptions)

        oPlotter.defineFigure(coPlots, "Plots", tFigureOptions)
        oPlotter.plot()
