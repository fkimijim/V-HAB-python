class Example(vsys):
    """
    EXAMPLE: A system that contains variable volumes.
    An example for this would be the bladder in a space suit, which is
    flexible and therefore changes its volume.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 30)

    def createMatterStructure(self):
        """
        Creates the matter structure for the system.
        """
        super().createMatterStructure()

        # Creating stores and phases
        self.toStores['Tank_1'] = matter.store(self, 'Tank_1', 1)
        oTank1Phase = self.toStores['Tank_1'].createPhase('air', 1, 293.15)

        self.toStores['Tank_2'] = matter.store(self, 'Tank_2', 1)
        oTank2Phase = self.toStores['Tank_2'].createPhase('air', 1, 323.15, 0.5, 1e5)

        # Adding a volume manipulator to the phase in Tank_1
        tutorials.volume_manipulator.components.VolumeChanger('Compressor', oTank1Phase)

        # Adding a pipe and branch
        components.matter.pipe(self, 'Pipe', 1.5, 0.005)
        matter.branch(self, oTank1Phase, ['Pipe'], oTank2Phase, 'Branch')

    def createSolverStructure(self):
        """
        Creates the solver structure for the system.
        """
        super().createSolverStructure()

        # Adding an interval solver for the branch
        solver.matter.interval.branch(self.toBranches['Branch'])

        # Setting thermal solvers
        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute function for this system.
        """
        super().exec()
