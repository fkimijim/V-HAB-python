class Example(vsys):
    """
    Example simulation for a simple thermal problem in V-HAB 2.
    Two tanks filled with gas at different temperatures with a
    conductive thermal interface (metal bar) connecting them.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.
        """
        super().__init__(oParent, sName, 30)

    def createMatterStructure(self):
        """
        Create all simulation objects in the matter domain.
        """
        # Call the parent class's createMatterStructure method
        super().createMatterStructure()

        # Create Tank_1 with a cold air phase
        matter.store(self, 'Tank_1', 1)
        self.toStores.Tank_1.createPhase('air', 'Cold', 1, 293.15)

        # Create Tank_2 with a hot air phase
        matter.store(self, 'Tank_2', 1)
        self.toStores.Tank_2.createPhase('air', 'Hot', 1, 493.15)

    def createThermalStructure(self):
        """
        Create all simulation objects in the thermal domain.
        """
        # Call the parent class's createThermalStructure method
        super().createThermalStructure()

        # Create a thermal conductor between the two tanks with a resistance of 1 K/W
        thermal.procs.conductors.conductive(self, 'Thermal_Connection', 1)

        # Get references to both capacities
        oCapacityCold = self.toStores.Tank_1.toPhases.Cold.oCapacity
        oCapacityHot = self.toStores.Tank_2.toPhases.Hot.oCapacity

        # Add a thermal branch between the two phases
        thermal.branch(self, oCapacityCold, ['Thermal_Connection'], oCapacityHot)

    def createSolverStructure(self):
        """
        Create all solver objects for the simulation.
        """
        # Call the parent class's createSolverStructure method
        super().createSolverStructure()

        # Assign the basic thermal solvers to all thermal branches
        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute method for the Example class.
        """
        # Call the parent class's exec method
        super().exec()
