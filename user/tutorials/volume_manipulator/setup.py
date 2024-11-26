class Setup(simulation.infrastructure):
    """
    SETUP: This class is used to setup a simulation for the Volume Manipulator Tutorial.
    """

    def __init__(self, *args):
        # Call parent constructor with the simulation name
        super().__init__('Tutorial_Volume_Manipulator', {}, {}, {})

        # Add the Example system to the simulation container
        tutorials.volume_manipulator.systems.Example(self.oSimulationContainer, 'Example')

        # Set the simulation time to one hour (3600 seconds)
        self.fSimTime = 3600

    def configureMonitors(self):
        """
        Configures the monitors for the simulation.
        """
        oLogger = self.toMonitors.oLogger

        # Add temperature values for the phases
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'fTemperature', 'K', 'Temperature Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'fTemperature', 'K', 'Temperature Phase 2')

        # Add volume values for the phases
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'fVolume', 'm^3', 'Volume Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'fVolume', 'm^3', 'Volume Phase 2')

        # Add pressure values for the phases
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2')

        # Add flow rate for the branch
        oLogger.addValue('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate')

    def plot(self):
        """
        Plots the results of the simulation.
        """
        oPlotter = plot@simulation.infrastructure(self)

        # Define plots
        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures')
        coPlots[1, 2] = oPlotter.definePlot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure')
        coPlots[2, 1] = oPlotter.definePlot(['"Branch Flow Rate"'], 'Flowrate')
        coPlots[2, 2] = oPlotter.definePlot(['"Volume Phase 1"', '"Volume Phase 2"'], 'Volume')

        # Define the figure and include a time plot
        oPlotter.defineFigure(coPlots, 'Tank Temperatures', {'bTimePlot': True})

        # Execute plotting
        oPlotter.plot()
