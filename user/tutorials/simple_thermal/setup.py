class setup(simulation.infrastructure):
    """
    Setup class for the Tutorial_Simple_Thermal simulation.
    """

    def __init__(self, *args):
        """
        Constructor function.
        """
        super().__init__('Tutorial_Simple_Thermal', containers.Map(), {}, {})
        
        # Creating the 'Example' system as a child of the root system
        tutorials.simple_thermal.systems.Example(self.oSimulationContainer, 'Example')
        
        # Setting the simulation duration to one hour (in seconds)
        self.fSimTime = 3600

    def configureMonitors(self):
        """
        Configure logging for the simulation.
        """
        self.toMonitors.oLogger.add('Example', 'thermalProperties')

    def plot(self):
        """
        Plotting the simulation results.
        """
        oPlotter = super().plot()
        oPlotter.plot()
