class Setup(simulation.infrastructure):
    """
    Setup class for the Test Solver MultiBranch simulation.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig, fSimTime=None):
        """
        Constructor for the Setup class.
        """
        super().__init__('Test_Solver_MultiBranch', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Create the 'Example' system as a child of the root system
        tests.multibranch_solver.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation length
        if fSimTime is None or fSimTime == 0:
            fSimTime = 3600 * 5

        if fSimTime < 0:
            self.fSimTime = 3600
            self.iSimTicks = abs(fSimTime)
            self.bUseTime = False
        else:
            # Stop when specific time in simulation is reached or after
            # specific number of ticks (bUseTime True/False).
            self.fSimTime = fSimTime  # In seconds
            self.iSimTicks = 1950
            self.bUseTime = True

    def configure_monitors(self):
        """
        Configures monitors for logging and debugging.
        """
        # Console Output
        oConsOut = self.toMonitors.oConsoleOutput

        # Example filters for debugging (uncomment as needed)
        # oConsOut.setLogOn().setVerbosity(3)
        # oConsOut.addMethodFilter('updatePressure')
        # oConsOut.addMethodFilter('massupdate')
        # oConsOut.addIdentFilter('changing-boundary-conditions')
        # oConsOut.addTypeToFilter('matter.phases.gas_flow_node')

        # Set minimum timestep for the simulation timer
        self.oSimulationContainer.oTimer.setMinStep(1e-16)

        # Logging
        oLog = self.toMonitors.oLogger

        # Log values from stores
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        for store in csStores:
            oLog.addValue(
                f"Example.toStores.{store}.aoPhases(1)",
                "this.fMass * this.fMassToPressure",
                "Pa",
                f"{store} Pressure"
            )
            oLog.addValue(
                f"Example.toStores.{store}.aoPhases(1)",
                "fTemperature",
                "K",
                f"{store} Temperature"
            )

        # Log values from branches
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        for branch in csBranches:
            oLog.addValue(
                f"Example.toBranches.{branch}",
                "fFlowRate",
                "kg/s",
                f"{branch} Flowrate"
            )

    def plot(self):
        """
        Plots the results of the simulation.
        """
        # Close all existing plots
        import matplotlib.pyplot as plt
        plt.close('all')

        # Define plots
        oPlotter = plot.simulation.infrastructure(self)

        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{store} Pressure"' for store in csStores]
        csTemperatures = [f'"{store} Temperature"' for store in csStores]

        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{branch} Flowrate"' for branch in csBranches]

        # Define options for plots and figures
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        coPlots = {
            (1, 1): oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions),
            (2, 1): oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions),
            (1, 2): oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions),
        }
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)

        # Plot all figures
        oPlotter.plot()
