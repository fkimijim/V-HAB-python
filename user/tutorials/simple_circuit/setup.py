class Setup(simulation.infrastructure):
    """
    Setup class for the Tutorial_Simple_Circuit simulation
    """

    def __init__(self, ptConfigParams, tSolverParams):
        super().__init__('Tutorial_Simple_Circuit', ptConfigParams, tSolverParams, {})

        # Create the Example system
        tutorials.simple_circuit.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation length
        self.fSimTime = 100  # In seconds
        self.iSimTicks = 1500
        self.bUseTime = True

        # Placeholder for log items
        self.ciLogValues = None

    def configureMonitors(self):
        """
        Configure logging
        """
        # Access the logger
        oLog = self.toMonitors.oLogger

        # Add log values for electrical properties
        self.ciLogValues = oLog.add('Example', 'electricalProperties')

    def plot(self):
        """
        Define and display plots
        """
        # Access the plotter
        oPlotter = super().plot()

        # Initialize plot options
        tPlotOptions = {}

        # Define and create voltage plot
        tPlotOptions['tFilter'] = {'sUnit': 'V'}
        coPlots = [[oPlotter.definePlot(self.ciLogValues, 'Voltages', tPlotOptions)]]

        # Define and create current plot
        tPlotOptions['tFilter'] = {'sUnit': 'A'}
        coPlots.append([oPlotter.definePlot(self.ciLogValues, 'Currents', tPlotOptions)])

        # Define the figure
        oPlotter.defineFigure(coPlots, 'Results')

        # Plot the data
        oPlotter.plot()
