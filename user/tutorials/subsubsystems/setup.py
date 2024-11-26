class Setup(simulation.infrastructure):
    """
    Setup class for the MiddleSystems tutorial simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams):
        """
        Initializes the setup for the simulation.
        """
        super().__init__('Tutorial_MiddleSystems', ptConfigParams, tSolverParams)

        # Add the Example system
        tutorials.subsubsystems.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation parameters
        self.fSimTime = 3600 * 2
        self.bUseTime = True

    def configureMonitors(self):
        """
        Configures monitors for logging values.
        """
        oLog = self.toMonitors.oLogger

        # Log values for Example system stores
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for iStore in csStores:
            oLog.addValue(f'Example.toStores.{iStore}.aoPhases(1)', 
                          'this.fMass * this.fMassToPressure', 
                          'Pa', f'{iStore} Pressure')
            oLog.addValue(f'Example.toStores.{iStore}.aoPhases(1)', 
                          'fTemperature', 
                          'K', f'{iStore} Temperature')

        # Log values for Example system branches
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for iBranch in csBranches:
            oLog.addValue(f'Example.toBranches.{iBranch}', 
                          'fFlowRate', 
                          'kg/s', f'{iBranch} Flowrate')

        # Log values for MiddleSystem stores
        csStoresMiddleSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toStores.keys())
        for iStore in csStoresMiddleSystem:
            oLog.addValue(f'Example:c:MiddleSystem.toStores.{iStore}.aoPhases(1)', 
                          'this.fMass * this.fMassToPressure', 
                          'Pa', f'{iStore} Pressure')
            oLog.addValue(f'Example:c:MiddleSystem.toStores.{iStore}.aoPhases(1)', 
                          'fTemperature', 
                          'K', f'{iStore} Temperature')

        # Log values for MiddleSystem branches
        csBranchesMiddleSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toBranches.keys())
        for iBranch in csBranchesMiddleSystem:
            oLog.addValue(f'Example:c:MiddleSystem.toBranches.{iBranch}', 
                          'fFlowRate', 
                          'kg/s', f'{iBranch} Flowrate')

    def plot(self, *args):
        """
        Plots the results of the simulation.
        """
        oPlotter = super().plot()

        # Define plots for stores in Example
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        # Define plots for branches in Example
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        # Define plots for stores in MiddleSystem
        csStoresMiddleSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toStores.keys())
        csPressuresMiddleSystem = [f'"{store} Pressure"' for store in csStoresMiddleSystem]
        csTemperaturesMiddleSystem = [f'"{store} Temperature"' for store in csStoresMiddleSystem]

        # Define plots for branches in MiddleSystem
        csBranchesMiddleSystem = list(self.oSimulationContainer.toChildren.Example.toChildren.MiddleSystem.toBranches.keys())
        csFlowRatesMiddleSystem = [f'"{branch} Flowrate"' for branch in csBranchesMiddleSystem]

        # Combine plots
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(csPressures + csPressuresMiddleSystem, 'Pressures', tPlotOptions)
        coPlots[2, 1] = oPlotter.definePlot(csFlowRates + csFlowRatesMiddleSystem, 'Flow Rates', tPlotOptions)
        coPlots[1, 2] = oPlotter.definePlot(csTemperatures + csTemperaturesMiddleSystem, 'Temperatures', tPlotOptions)

        # Create figure and plot
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)
        oPlotter.plot()
