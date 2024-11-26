class Setup(simulation.infrastructure):
    """
    Setup class for the subsystem simulation in V-HAB 2.0.
    This class handles the simulation setup, logging, and plotting for a system
    with subsystems.
    """

    def __init__(self, ptConfigParams, tSolverParams):
        """
        Constructor for the Setup class.

        Args:
            ptConfigParams: Configuration parameters for the simulation.
            tSolverParams: Solver parameters for the simulation.
        """
        super().__init__('Tutorial_Subsystems', ptConfigParams, tSolverParams)

        # Adding the main Example system to the simulation container
        tutorials.subsystems.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation parameters
        self.fSimTime = 3600 * 2  # Two hours in seconds
        self.bUseTime = True

    def configure_monitors(self):
        """
        Configures logging for the simulation.
        """
        oLog = self.toMonitors.oLogger

        # Logging for the main system's stores
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for iStore in csStores:
            oLog.add_value(
                f'Example.toStores.{iStore}.aoPhases(1)',
                'this.fMass * this.fMassToPressure',
                'Pa',
                f'{iStore} Pressure'
            )
            oLog.add_value(
                f'Example.toStores.{iStore}.aoPhases(1)',
                'fTemperature',
                'K',
                f'{iStore} Temperature'
            )

        # Logging for the main system's branches
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for iBranch in csBranches:
            oLog.add_value(
                f'Example.toBranches.{iBranch}',
                'fFlowRate',
                'kg/s',
                f'{iBranch} Flowrate'
            )

        # Logging for the subsystem's stores
        csStoresSubSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toStores.keys())
        for iStore in csStoresSubSystem:
            oLog.add_value(
                f'Example:c:SubSystem.toStores.{iStore}.aoPhases(1)',
                'this.fMass * this.fMassToPressure',
                'Pa',
                f'{iStore} Pressure'
            )
            oLog.add_value(
                f'Example:c:SubSystem.toStores.{iStore}.aoPhases(1)',
                'fTemperature',
                'K',
                f'{iStore} Temperature'
            )

        # Logging for the subsystem's branches
        csBranchesSubSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toBranches.keys())
        for iBranch in csBranchesSubSystem:
            oLog.add_value(
                f'Example:c:SubSystem.toBranches.{iBranch}',
                'fFlowRate',
                'kg/s',
                f'{iBranch} Flowrate'
            )

    def plot(self, *args):
        """
        Creates and displays plots for the simulation results.
        """
        # Closing all previous plots
        plt.close('all')

        # Getting a handle to the plotter object
        oPlotter = super().plot()

        # Main system stores
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        # Main system branches
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        # Subsystem stores
        csStoresSubSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toStores.keys())
        csPressuresSubSystem = [f'"{store} Pressure"' for store in csStoresSubSystem]
        csTemperaturesSubSystem = [f'"{store} Temperature"' for store in csStoresSubSystem]

        # Subsystem branches
        csBranchesSubSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.SubSystem.toBranches.keys())
        csFlowRatesSubSystem = [f'"{branch} Flowrate"' for branch in csBranchesSubSystem]

        # Plot options
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Define plots
        coPlots = {}
        coPlots[(1, 1)] = oPlotter.define_plot(csPressures + csPressuresSubSystem, 'Pressures', tPlotOptions)
        coPlots[(2, 1)] = oPlotter.define_plot(csFlowRates + csFlowRatesSubSystem, 'Flow Rates', tPlotOptions)
        coPlots[(1, 2)] = oPlotter.define_plot(csTemperatures + csTemperaturesSubSystem, 'Temperatures', tPlotOptions)

        # Define the figure
        oPlotter.define_figure(coPlots, 'Plots', tFigureOptions)

        # Plot all defined figures
        oPlotter.plot()
