class Setup(simulation.infrastructure):
    """
    SETUP This class is used to setup a simulation.
    Used for the following:
      - Instantiate the root object
      - Determine which items are logged
      - Set the simulation duration
      - Provide methods for plotting the results
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor function.
        """
        # Call the parent constructor with the name of the simulation.
        super().__init__('Example_HeatOfExpansion', {}, {}, {})

        # Creating the 'Example' system as a child of the root system of this simulation.
        examples.HeatOfExpansion.systems.Example(self.oSimulationContainer, 'Example')

        # Setting the simulation duration to one hour (time in seconds).
        self.fSimTime = 3600

    def configureMonitors(self):
        """
        Logging function to configure which values to monitor during the simulation.
        """
        # Create a local variable for the logger object.
        oLogger = self.toMonitors.oLogger

        # Adding the tank temperatures to the log.
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'fTemperature', 'K', 'Temperature Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'fTemperature', 'K', 'Temperature Phase 2')

        # Adding the heat flows to the log.
        oLogger.addValue(
            'Example:s:Tank_1.aoPhases(0).oCapacity.toHeatSources.JouleThomsonSource_1',
            'fHeatFlow',
            'W',
            'Joule Thomson Heat Flow Phase 1',
        )
        oLogger.addValue(
            'Example:s:Tank_2.aoPhases(0).oCapacity.toHeatSources.JouleThomsonSource_2',
            'fHeatFlow',
            'W',
            'Joule Thomson Heat Flow Phase 2',
        )
        oLogger.addValue('Example.toBranches.Branch.aoFlowProcs(0)', 'fHeatFlow', 'W', 'Joule Thomson Heat Flow Pipe')

        # Adding the tank pressures to the log.
        oLogger.addValue(
            'Example:s:Tank_1:p:Tank_1_Phase_1',
            'this.fMass * this.fMassToPressure',
            'Pa',
            'Pressure Phase 1',
        )
        oLogger.addValue(
            'Example:s:Tank_2:p:Tank_2_Phase_1',
            'this.fMass * this.fMassToPressure',
            'Pa',
            'Pressure Phase 2',
        )

        # Adding the branch flow rate to the log.
        oLogger.addValue('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate')

    def plot(self):
        """
        Plotting function to visualize the results of the simulation.
        """
        # Get a handle to the plotter object associated with this simulation.
        oPlotter = super().plot()

        # Create three plots arranged in a 2x2 matrix:
        # 1. Two temperatures
        # 2. Two pressures
        # 3. Branch flow rate
        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures')
        coPlots[1, 2] = oPlotter.definePlot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure')
        coPlots[2, 1] = oPlotter.definePlot(['"Branch Flow Rate"'], 'Flowrate')
        coPlots[2, 2] = oPlotter.definePlot(
            [
                '"Joule Thomson Heat Flow Phase 1"',
                '"Joule Thomson Heat Flow Phase 2"',
                '"Joule Thomson Heat Flow Pipe"',
            ],
            'Heat Flows',
        )

        # Create a figure containing the plots and enable the time plot.
        oPlotter.defineFigure(coPlots, 'Tank Temperatures', {'bTimePlot': True})

        # Plotting all figures.
        oPlotter.plot()
