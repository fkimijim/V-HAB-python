class Setup(simulation.infrastructure):
    """
    SETUP class for simulation setup.
    Responsible for:
    - Instantiating the root object
    - Registering branches to solvers
    - Logging
    - Setting simulation duration
    - Plotting results
    """
    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor function.
        """
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        # Call parent constructor with simulation name
        super().__init__('Test_Manipulator', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Creating the root object
        tutorials.manipulator.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation length
        self.fSimTime = fSimTime if fSimTime is not None else 2000

    def configure_monitors(self):
        """
        Configure the logging for the simulation.
        """
        oLog = self.toMonitors.oLogger

        # Logging values for stores
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for store in csStores:
            oLog.addValue(
                f'Example.toStores.{store}.aoPhases(1)',
                'this.fMass * this.fMassToPressure',
                'Pa',
                f'{store} Pressure'
            )
            oLog.addValue(
                f'Example.toStores.{store}.aoPhases(1)',
                'fTemperature',
                'K',
                f'{store} Temperature'
            )

        # Logging values for branches
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for branch in csBranches:
            oLog.addValue(
                f'Example.toBranches.{branch}',
                'fFlowRate',
                'kg/s',
                f'{branch} Flowrate'
            )

        # Additional specific logging
        oLog.addValue(
            'Example:s:Reactor.toProcsP2P.FilterProc',
            'fFlowRate',
            'kg/s',
            'P2P Flow Rate'
        )
        oLog.addValue(
            'Example:s:Reactor.toPhases.FlowPhase.toManips.substance',
            'afPartialFlows(this.oMT.tiN2I.O2)',
            'kg/s',
            'Bosch O2 Flow Rate'
        )
        oLog.addValue(
            'Example:s:Reactor.toPhases.FlowPhase.toManips.substance',
            'afPartialFlows(this.oMT.tiN2I.CO2)',
            'kg/s',
            'Bosch CO2 Flow Rate'
        )
        oLog.addValue(
            'Example:s:Reactor.toPhases.FlowPhase.toManips.substance',
            'afPartialFlows(this.oMT.tiN2I.C)',
            'kg/s',
            'Bosch C Flow Rate'
        )

    def plot(self):
        """
        Plot the results of the simulation.
        """
        import matplotlib.pyplot as plt

        # Define Plots
        plt.close('all')
        oPlotter = super().plot()

        # Gather store data for plots
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        # Gather branch data for plots
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        # Bosch Reactor Flows
        csBoschReactorFlows = [
            '"P2P Flow Rate"', '"Bosch O2 Flow Rate"',
            '"Bosch CO2 Flow Rate"', '"Bosch C Flow Rate"'
        ]

        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Define plots
        coPlots = [
            [oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)],
            [oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)],
            [oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)],
            [oPlotter.definePlot(csBoschReactorFlows, 'Bosch Reactor Flowrates', tPlotOptions)]
        ]

        # Define figure and plot
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)
        oPlotter.plot()
