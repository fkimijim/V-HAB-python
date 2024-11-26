class Setup(simulation.infrastructure):
    """
    Setup class for the Test_P2P simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor for the setup class.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration (optional).
            fSimTime: Simulation time in seconds (optional).
        """
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        # Set default solver parameters if not provided
        if 'rUpdateFrequency' not in tSolverParams:
            tSolverParams['rUpdateFrequency'] = 0.1

        if 'rHighestMaxChangeDecrease' not in tSolverParams:
            tSolverParams['rHighestMaxChangeDecrease'] = 1000

        # Initialize the parent class
        super().__init__('Test_P2P', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Create the Example system
        tutorials.p2p.stationary.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation length
        self.fSimTime = 5000
        if fSimTime is not None:
            self.fSimTime = fSimTime
        self.iSimTicks = 3000
        self.bUseTime = True

        # Register callback for debug state
        self.oSimulationContainer.oTimer.bind(self.switch_debug_state, -1, {
            'sMethod': 'switchDebugState',
            'sDescription': 'setup - logdbg ctrl fct'
        })

    def switch_debug_state(self, oTimer):
        """
        A method to control debugging states based on simulation ticks.
        """
        iTick = oTimer.iTick
        oOut = self.toMonitors.oConsoleOutput

        if iTick == 1015:
            oOut.setLogOn()
        elif iTick == 1020:
            oOut.addIdentFilter('update')
        elif iTick == 1030:
            oOut.resetIdentFilters()
            oOut.toggleShowStack()
        elif iTick == 1035:
            oOut.toggleShowStack()
        elif iTick == 1040:
            oOut.setVerbosity(3)
        elif iTick == 1045:
            oOut.setVerbosity(1)
        elif iTick == 1050:
            oOut.setLevel(2)
        elif iTick == 1055:
            oOut.setLogOff()

    def configure_monitors(self):
        """
        Configure the monitors for logging and console output.
        """
        oLog = self.toMonitors.oLogger

        # Log pressures and temperatures for all stores
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        for csStore in csStores:
            oLog.addValue(
                f"Example.toStores.{csStore}.aoPhases(1)",
                "this.fMass * this.fMassToPressure",
                "Pa",
                f"{csStore} Pressure"
            )
            oLog.addValue(
                f"Example.toStores.{csStore}.aoPhases(1)",
                "fTemperature",
                "K",
                f"{csStore} Temperature"
            )

        # Log flow rates for all branches
        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        for csBranch in csBranches:
            oLog.addValue(
                f"Example.toBranches.{csBranch}",
                "fFlowRate",
                "kg/s",
                f"{csBranch} Flowrate"
            )

        # Log specific parameters
        oLog.addValue(
            'Example:s:Atmos.aoPhases(1)',
            'afMass(this.oMT.tiN2I.O2)',
            'kg',
            'O_2 Mass in Atmosphere'
        )
        oLog.addValue(
            'Example:s:Filter.aoPhases(2)',
            'afMass(this.oMT.tiN2I.O2)',
            'kg',
            'O_2 Mass in Filter'
        )
        oLog.addValue(
            'Example:s:Filter.toProcsP2P.filterproc',
            'fFlowRate',
            'kg/s',
            'P2P Filter Flow Rate'
        )

    def plot(self):
        """
        Plot the simulation results.
        """
        import matplotlib.pyplot as plt
        plt.close('all')

        # Create a plotter object
        oPlotter = super().plot()

        # Prepare plot data for pressures, temperatures, flow rates, and specific values
        csStores = list(self.oSimulationContainer.toChildren.Example.toStores.keys())
        csPressures = [f'"{csStore} Pressure"' for csStore in csStores]
        csTemperatures = [f'"{csStore} Temperature"' for csStore in csStores]

        csBranches = list(self.oSimulationContainer.toChildren.Example.toBranches.keys())
        csFlowRates = [f'"{csBranch} Flowrate"' for csBranch in csBranches]

        csIndividualPlots = [
            '"O_2 Mass in Atmosphere"',
            '"O_2 Mass in Filter"',
            '"P2P Filter Flow Rate"'
        ]

        # Define plot options
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Create subplots
        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)
        coPlots[2, 1] = oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)
        coPlots[1, 2] = oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)
        coPlots[2, 2] = oPlotter.definePlot(csIndividualPlots, 'Random Plots', tPlotOptions)

        # Define the figure with subplots
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)

        # Plot the data
        oPlotter.plot()
