class Example(vsys):
    """
    Example simulation for a system with subsystems in V-HAB 2.0.
    Two Tanks are connected to each other via pipes with a filter in
    between. The filter is modeled as a store with two phases, one
    being the connection (via exmes) to the system level branch. The
    filter itself is in a subsystem of this system called 'SubSystem'.
    This example demonstrates how to create branches between subsystems.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.

        Args:
            oParent: The parent object.
            sName: The name of the system.
        """
        super().__init__(oParent, sName)

        # Adding a subsystem
        tutorials.subsystems.subsystems.ExampleSubsystem(self, 'SubSystem')

        # Additional configuration
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Creates the matter structure for the system.
        """
        super().createMatterStructure()

        # Create two tanks
        matter.store(self, 'Tank_1', 100)
        oGasPhase = self.toStores.Tank_1.createPhase('air', 20, 293, 0.5, 2e5)

        matter.store(self, 'Tank_2', 100)
        oAirPhase = self.toStores.Tank_2.createPhase('air', 20)

        # Create pipes
        components.matter.pipe(self, 'Pipe1', 1, 0.005)
        components.matter.pipe(self, 'Pipe2', 1, 0.005)

        # Create Subsystem Connections
        # Interface branches between the system and its subsystems are
        # always from the subsystem to the parent system. A positive
        # flowrate indicates matter entering the parent system and
        # leaving the subsystem.
        matter.branch(self, 'SubsystemInput', ['Pipe1'], oGasPhase)
        matter.branch(self, 'SubsystemOutput', ['Pipe2'], oAirPhase)

        # Set subsystem interface flows
        self.toChildren.SubSystem.setIfFlows('SubsystemInput', 'SubsystemOutput')

    def createSolverStructure(self):
        """
        Creates the solver structure for the system.
        """
        super().createSolverStructure()

        # Set thermal solvers
        self.setThermalSolvers()

    def exec(self, *args):
        """
        Execute function for the system.
        """
        super().exec(*args)
