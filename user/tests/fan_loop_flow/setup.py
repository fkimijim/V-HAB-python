class setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig, fSimTime=None):
        """
        Initializes the setup class for the Example Fan Loop Flow simulation.
        """
        super().__init__('Example_Fan_Loop_Flow', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Add the Example system
        tests.fan_loop_flow.systems.Example(self.oSimulationContainer, 'Example')

        # Set the simulation time
        if fSimTime is None:
            fSimTime = 3600
        self.fSimTime = fSimTime
        self.iSimTicks = 600
        self.bUseTime = True

    def configureMonitors(self):
        """
        Configures the simulation monitors to log values.
        """
        oLog = self.toMonitors.oLogger

        # Log pressures and temperatures for each store
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        for csStore in csStores:
            oLog.addValue(f"Example.toStores.{csStore}.aoPhases(1)",
                          "this.fMass * this.fMassToPressure", "Pa", f"{csStore} Pressure")
            oLog.addValue(f"Example.toStores.{csStore}.aoPhases(1)",
                          "fTemperature", "K", f"{csStore} Temperature")

        # Log flow rates for each branch
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        for csBranch in csBranches:
            oLog.addValue(f"Example.toBranches.{csBranch}", "fFlowRate", "kg/s", f"{csBranch} Flowrate")

    def plot(self, *args):
        """
        Plots the logged data.
        """
        import matplotlib.pyplot as plt

        # Close all existing plots
        plt.close('all')

        oPlotter = super().plot()

        # Prepare data for pressures and temperatures
        csStores = self.oSimulationContainer.toChildren.Example.toStores.keys()
        csPressures = [f'"{csStore} Pressure"' for csStore in csStores]
        csTemperatures = [f'"{csStore} Temperature"' for csStore in csStores]

        # Prepare data for flow rates
        csBranches = self.oSimulationContainer.toChildren.Example.toBranches.keys()
        csFlowRates = [f'"{csBranch} Flowrate"' for csBranch in csBranches]

        # Define plot options
        tPlotOptions = {'sTimeUnit': 'seconds'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        # Define plots
        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(csPressures, 'Pressures', tPlotOptions)
        coPlots[2, 1] = oPlotter.definePlot(csFlowRates, 'Flow Rates', tPlotOptions)
        coPlots[1, 2] = oPlotter.definePlot(csTemperatures, 'Temperatures', tPlotOptions)

        # Define a figure with the plots
        oPlotter.defineFigure(coPlots, 'Plots', tFigureOptions)

        # Generate the plots
        oPlotter.plot()
