class MiddleSystem(vsys):
    """
    MiddleSystem
    A subsystem containing another subsystem. This demonstrates
    "pass-through" branches and hierarchical subsystems in V-HAB.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the MiddleSystem class.
        """
        super().__init__(oParent, sName)

        # Evaluating the configuration code for the system
        eval(self.oRoot.oCfgParams.configCode(self))

        # Adding the subsystem. Reuses the subsystem from the subsystem example
        tutorials.subsystems.subsystems.ExampleSubsystem(self, 'SubSystem')

    def createMatterStructure(self):
        """
        Creates the matter structure for the MiddleSystem.
        """
        super().createMatterStructure()

        # Adding pipes
        components.matter.pipe(self, 'Pipe3', 1, 0.005)
        components.matter.pipe(self, 'Pipe4', 1, 0.005)

        # Pass-through branches connect the subsystem with the parent system
        matter.branch(self, 'FromSubOut', ['Pipe3'], 'ToSupIn')
        matter.branch(self, 'FromSubIn', ['Pipe4'], 'ToSupOut')

        # Connecting the subsystem branches
        self.toChildren.SubSystem.setIfFlows('FromSubIn', 'FromSubOut')

    def createSolverStructure(self):
        """
        Creates the solver structure for the MiddleSystem.
        """
        super().createSolverStructure()
        self.setThermalSolvers()

    def setIfFlows(self, sToSupIn, sToSupOut):
        """
        Sets the interface flows for the MiddleSystem.
        """
        self.connectIF('ToSupIn', sToSupIn)
        self.connectIF('ToSupOut', sToSupOut)

    def exec(self, *args):
        """
        Executes the MiddleSystem logic.
        """
        super().exec(*args)
