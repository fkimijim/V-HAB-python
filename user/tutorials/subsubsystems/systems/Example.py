class Example(vsys):
    """
    Example simulation for a system with subsystems in V-HAB 2.0
    This system includes a parent system, a subsystem called MiddleSystem, 
    and another subsystem containing a filter from the subsystems tutorial. 
    This demonstrates hierarchical layers of systems and "pass-through" branches
    that connect a subsystem of the current system to the parent system.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.
        """
        super().__init__(oParent, sName, 10)

        # Adding the MiddleSystem as a subsystem
        tutorials.subsubsystems.subsystems.MiddleSystem(self, 'MiddleSystem')

        # Evaluating the configuration code
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Creates the matter structure for the Example system.
        """
        super().createMatterStructure()

        # Creating Tank_1 with 20 m^3 volume
        matter.store(self, 'Tank_1', 20)
        oGasPhase = self.toStores.Tank_1.createPhase('air', 20, 293, 0.5, 2e5)

        # Creating Tank_2 with 20 m^3 volume
        matter.store(self, 'Tank_2', 20)
        oAirPhase = self.toStores.Tank_2.createPhase('air', 20)

        # Adding pipes
        components.matter.pipe(self, 'Pipe1', 1, 0.005)
        components.matter.pipe(self, 'Pipe2', 1, 0.005)

        # Defining branches for the MiddleSystem
        matter.branch(self, 'MiddleSystemInput', ['Pipe1'], oGasPhase)
        matter.branch(self, 'MiddleSystemOutput', ['Pipe2'], oAirPhase)

        # Connecting the MiddleSystem branches
        self.toChildren.MiddleSystem.setIfFlows('MiddleSystemOutput', 'MiddleSystemInput')

    def createSolverStructure(self):
        """
        Creates the solver structure for the Example system.
        """
        super().createSolverStructure()

        # Setting thermal solvers
        self.setThermalSolvers()

    def exec(self, *args):
        """
        Executes the Example system logic.
        """
        super().exec(*args)
