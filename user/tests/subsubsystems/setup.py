class Setup(simulation.infrastructure):
    """
    Setup class for the Test_SubSubSystems simulation.
    - Instantiates the root object and subsystems.
    - Configures logging for relevant values.
    - Defines simulation duration.
    - Provides methods for plotting results.
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
        # Set default solver parameter if not provided
        if "rHighestMaxChangeDecrease" not in tSolverParams:
            tSolverParams["rHighestMaxChangeDecrease"] = 500

        # Initialize the parent class
        super().__init__('Test_SubSubSystems', ptConfigParams, tSolverParams, ttMonitorConfig or {})

        # Create the root object
        tutorials.subsubsystems.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation duration (default: 900 seconds)
        self.fSimTime = fSimTime if fSimTime is not None else 900

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

        # Log values for the MiddleSystem
        csStoresMiddleSystem = self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toStores.keys()
        for iStore in csStoresMiddleSystem:
            oLog.addValue(f"Example:c:MiddleSystem.toStores.{iStore}.aoPhases(1)", "this.fMass * this.fMassToPressure", "Pa", f"{iStore} Pressure")
            oLog.addValue(f"Example:c:MiddleSystem.toStores.{iStore}.aoPhases(1)", "fTemperature", "K", f"{iStore} Temperature")

        csBranchesMiddleSystem = self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toBranches.keys()
        for iBranch in csBranchesMiddleSystem:
            oLog.addValue(f"Example:c:MiddleSystem.toBranches.{iBranch}", "fFlowRate", "kg/s", f"{iBranch} Flowrate")

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

        # Define plots for the MiddleSystem
        csStoresMiddleSystem = self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toStores.keys()
        csPressuresMiddleSystem = [f'"{store} Pressure"' for store in csStoresMiddleSystem]
        csTemperaturesMiddleSystem = [f'"{store} Temperature"' for store in csStoresMiddleSystem]

        csBranchesMiddleSystem = self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toBranches.keys()
        csFlowRatesMiddleSystem = [f'"{branch} Flowrate"' for branch in csBranchesMiddleSystem]

        tPlotOptions = {"sTimeUnit": "seconds"}
        tFigureOptions = {"bTimePlot": False, "bPlotTools": False}

        coPlots = {}
        coPlots[(1, 1)] = oPlotter.definePlot(csPressures + csPressuresMiddleSystem, "Pressures", tPlotOptions)
        coPlots[(2, 1)] = oPlotter.definePlot(csFlowRates + csFlowRatesMiddleSystem, "Flow Rates", tPlotOptions)
        coPlots[(1, 2)] = oPlotter.definePlot(csTemperatures + csTemperaturesMiddleSystem, "Temperatures", tPlotOptions)

        oPlotter.defineFigure(coPlots, "Plots", tFigureOptions)
        oPlotter.plot()
