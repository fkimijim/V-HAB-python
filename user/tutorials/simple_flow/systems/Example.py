class Example(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0
    Two tanks filled with gas at different temperatures and pressures
    with a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Initialize the Example class.
        :param oParent: Parent system
        :param sName: Name of the system
        """
        # Call the parent constructor
        super().__init__(oParent, sName, 30)

    def createMatterStructure(self):
        """
        Create all simulation objects in the matter domain.
        """
        # Call the parent class's createMatterStructure method
        super().createMatterStructure()

        # Create a store, volume 1 m^3
        matter.store(self, 'Tank_1', 1)

        # Add a phase to the store 'Tank_1', 1 m^3 air at 20 deg C
        oGasPhase = self.toStores.Tank_1.createPhase('air', 1, 293.15)

        # Create a second store, volume 1 m^3
        matter.store(self, 'Tank_2', 1)

        # Add a phase to the store 'Tank_2', 1 m^3 air at 50 deg C,
        # relative humidity of 50% and at a pressure of 2e5 Pa
        oAirPhase = self.toStores.Tank_2.createPhase('air', 1, 323.15, 0.5, 2e5)

        # Add a pipe to connect the tanks, 1.5 m long, 5 mm in diameter
        components.matter.pipe(self, 'Pipe', 1.5, 0.005)

        # Create the flowpath (branch) between the components
        matter.branch(self, oGasPhase, ['Pipe'], oAirPhase, 'Branch')

    def createThermalStructure(self):
        """
        Create all simulation objects in the thermal domain.
        """
        # Call the parent class's createThermalStructure method
        super().createThermalStructure()

        # No additional thermal objects are needed for this simple model.
        # Thermal solvers for advective heat transfer will be created
        # automatically by the setThermalSolvers method.

    def createSolverStructure(self):
        """
        Create all of the solver objects required for a simulation.
        """
        # Call the parent class's createSolverStructure method
        super().createSolverStructure()

        # Create an interval solver object for the branch flow rate
        solver.matter.interval.branch(self.toBranches.Branch)

        # Set up thermal solvers for temperature calculations
        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute function for this system.
        This function can be used to change the system state dynamically.
        """
        # Call the parent class's exec method
        super().exec()
