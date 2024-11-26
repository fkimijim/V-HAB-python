class Setup(simulation.infrastructure):
    """
    Setup class for the simulation.
    This class is used to:
    - Instantiate the root object
    - Determine which items are logged
    - Set the simulation duration
    - Provide methods for plotting the results
    """
    
    def __init__(self, *args):
        """
        Constructor function for the Setup class.
        """
        # Call the parent constructor and set the name of the simulation
        super().__init__('Tutorial_Simple_Flow', {}, {}, {})
        
        # Create the 'Example' system as a child of the root system
        tutorials.simple_flow.systems.Example(self.oSimulationContainer, 'Example')
        
        # Set the simulation duration to one hour (in seconds)
        self.fSimTime = 3600
    
    def configureMonitors(self):
        """
        Configure logging for the simulation.
        """
        # Get the logger object for convenience
        oLogger = self.toMonitors.oLogger
        
        # Add the tank temperatures to the log
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'fTemperature', 'K', 'Temperature Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'fTemperature', 'K', 'Temperature Phase 2')
        
        # Add the tank pressures to the log
        oLogger.addValue('Example:s:Tank_1:p:Tank_1_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1')
        oLogger.addValue('Example:s:Tank_2:p:Tank_2_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2')
        
        # Add the branch flow rate to the log
        oLogger.addValue('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate')
    
    def plot(self):
        """
        Create and display plots for the simulation.
        """
        # Get a handle to the plotter object
        oPlotter = super().plot()
        
        # Define the plots
        coPlots = {}
        coPlots[1, 1] = oPlotter.definePlot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures')
        coPlots[1, 2] = oPlotter.definePlot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure')
        coPlots[2, 1] = oPlotter.definePlot(['"Branch Flow Rate"'], 'Flowrate')
        
        # Create a figure containing the plots
        oPlotter.defineFigure(coPlots, 'Tank Temperatures', {'bTimePlot': True})
        
        # Plot all figures
        oPlotter.plot()
