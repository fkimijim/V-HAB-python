class Setup(simulation.infrastructure):
    """
    Setup class for Example Mixture Flow simulation.
    This class is used to configure and run the simulation.
    """

    def __init__(self, ptConfigParams=None, tSolverParams=None, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor for the Setup class.

        Args:
            ptConfigParams: Configuration parameters for the simulation.
            tSolverParams: Solver parameters for the simulation.
            ttMonitorConfig: Monitor configuration for logging.
            fSimTime: Simulation time duration.
        """
        super().__init__('Example_Mixture_Flow', ptConfigParams, tSolverParams, ttMonitorConfig)
        tests.mixture_flow.systems.Example(self.oSimulationContainer, 'Example')
        self.fSimTime = 3000 if fSimTime is None or not fSimTime else fSimTime

    def configure_monitors(self):
        """
        Configure the logging monitors for the simulation.
        """
        oLog = self.toMonitors.oLogger

        # Configure logging for stores
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for iStore in csStores:
            oLog.add_value(f'Example.toStores.{iStore}.aoPhases[0]', 'fMass', 'kg', f'{iStore} Mass')
            oLog.add_value(f'Example.toStores.{iStore}.aoPhases[0]', 'fVolume', 'm^3', f'{iStore} Volume')
            oLog.add_value(f'Example.toStores.{iStore}.aoPhases[0]', 'fPressure', 'Pa', f'{iStore} Pressure')
            oLog.add_value(f'Example.toStores.{iStore}.aoPhases[0]', 'fTemperature', 'K', f'{iStore} Temperature')
            oLog.add_value(
                f'Example.toStores.{iStore}.aoPhases[0]', 'afMass(this.oMT.tiN2I.CO2)', 'kg', f'{iStore} CO2 Mass'
            )

        # Additional logging for specific pressures
        oLog.add_value('Example.toStores.WaterTank_1.toPhases.WaterTank_1_Phase_2', 'fPressure', 'Pa', 'Water Tank 1 Air Pressure')
        oLog.add_value('Example.toStores.WaterTank_2.toPhases.WaterTank_2_Phase_2', 'fPressure', 'Pa', 'Water Tank 2 Air Pressure')

        # Configure logging for branches
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for iBranch in csBranches:
            oLog.add_value(f'Example.toBranches.{iBranch}', 'fFlowRate', 'kg/s', f'{iBranch} Flowrate')

    def plot(self):
        """
        Plot the results of the simulation.
        """
        import matplotlib.pyplot as plt

        plt.close('all')
        oPlotter = super().plot()

        # Extract store and branch names
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csMasses, csPressures, csVolumes, csTemperatures, csCO2Masses = [], [], [], [], []

        for iStore in csStores:
            csMasses.append(f'"{iStore} Mass"')
            csPressures.append(f'"{iStore} Pressure"')
            csVolumes.append(f'"{iStore} Volume"')
            csTemperatures.append(f'"{iStore} Temperature"')
            csCO2Masses.append(f'"{iStore} CO2 Mass"')

        csPressures.append('"Water Tank 1 Air Pressure"')
        csPressures.append('"Water Tank 2 Air Pressure"')

        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{iBranch} Flowrate"' for iBranch in csBranches]

        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Define plots
        coPlots = {
            (1, 1): oPlotter.define_plot(csMasses, 'Masses', tPlotOptions),
            (1, 2): oPlotter.define_plot(csPressures, 'Pressures', tPlotOptions),
            (2, 1): oPlotter.define_plot(csFlowRates, 'Flow Rates', tPlotOptions),
            (2, 2): oPlotter.define_plot(csTemperatures, 'Temperatures', tPlotOptions),
            (3, 1): oPlotter.define_plot(csVolumes, 'Volumes', tPlotOptions),
            (3, 2): oPlotter.define_plot(csCO2Masses, 'CO2 Masses', tPlotOptions),
        }
        oPlotter.define_figure(coPlots, 'Plots', tFigureOptions)

        # Generate plots
        oPlotter.plot()
