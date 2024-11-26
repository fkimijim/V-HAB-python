class Example(vsys):
    """
    Example class demonstrating a simple vsys system in Python.
    """

    def __init__(self, oParent, sName):
        # Initialize the parent vsys class with a time step of 30 seconds
        super().__init__(oParent, sName, 30)
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Creates the matter structure for the system.
        """
        super().createMatterStructure()

        # -- Additional Section --
        matter.store(self, 'Cabin', 1)
        matter.phases.gas(self.toStores.Cabin, 'CabinAir', {'N2': 1}, 1, 293.15)
        # -- End of Additional Section --

    def createSolverStructure(self):
        """
        Creates the solver structure for the system.
        """
        super().createSolverStructure()

    def exec(self, _):
        """
        Execute function for this system, called at defined time steps.
        """
        super().exec()
