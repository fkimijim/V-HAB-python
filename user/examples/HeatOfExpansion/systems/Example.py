class Example(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0.
    Two tanks filled with gas at different temperatures and pressures
    with a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.
        :param oParent: Parent system
        :param sName: Name of the system
        """
        # Call parent constructor with the execution interval set to 30 seconds
        super().__init__(oParent, sName, 30)

    def createMatterStructure(self):
        """
        Create the matter structure for the simulation.
        """
        # Call the parent class method
        super().createMatterStructure()

        # Creating a store, volume 1 m^3
        matter.store(self, 'Tank_1', 1)

        # Adding a phase to the store 'Tank_1', 1 m^3 air at 20°C
        oGasPhase = self.toStores.Tank_1.createPhase('air', 1, 293.15)

        # Creating a second store, volume 1 m^3
        matter.store(self, 'Tank_2', 1)

        # Adding a phase to the store 'Tank_2', 1 m^3 air at 50°C, with a pressure of 5e5 Pa
        oAirPhase = self.toStores.Tank_2.createPhase('air', 1, 293.15, 0.5, 5e5)

        # Adding a pipe to connect the tanks, 1.5 m long, 5 mm in diameter
        examples.HeatOfExpansion.components.ThermallyActivePipe(
            self, 'Pipe', 1.5, 0.005, 2e-3
        )

        # Creating the flowpath (branch) between the components
        matter.branch(self, oGasPhase, ['Pipe'], oAirPhase, 'Branch')

    def createThermalStructure(self):
        """
        Create the thermal structure for the simulation.
        """
        # Call the parent class method
        super().createThermalStructure()

        # Adding Joule-Thomson heat sources to the tanks
        oHeatSource1 = components.thermal.heatsources.JouleThomson('JouleThomsonSource_1')
        oHeatSource2 = components.thermal.heatsources.JouleThomson('JouleThomsonSource_2')

        # Adding the heat sources to the tank capacities
        self.toStores.Tank_1.aoPhases[0].oCapacity.addHeatSource(oHeatSource1)
        self.toStores.Tank_2.aoPhases[0].oCapacity.addHeatSource(oHeatSource2)

    def createSolverStructure(self):
        """
        Create the solver structure for the simulation.
        """
        # Call the parent class method
        super().createSolverStructure()

        # Creating an interval solver for the branch
        solver.matter.interval.branch(self.toBranches.Branch)

        # Set thermal solvers for temperature changes
        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute function for this system.
        This function can be used to change the system state, e.g.,
        close valves or switch on/off components.
        """
        # Call the parent class method
        super().exec()
