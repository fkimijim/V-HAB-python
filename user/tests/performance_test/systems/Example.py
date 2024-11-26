class Example(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0
    Two tanks filled with gas at different pressures and a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.

        Args:
            oParent: Parent object of this system.
            sName: Name of the system.
        """
        # Call parent constructor
        super().__init__(oParent, sName, 5000)

        # Properties
        self.sSolvers = 'manual'  # Options: manual, linear, iterative
        self.sMode = 'flow'       # Options: none, flow, filter
        self.fStoreVolumes = 1000  # Main stores - volumes
        self.fLastUpdate = -1     # Track last update

        # Make the system configurable
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Create the matter structure for the system.
        """
        super().createMatterStructure()

        if self.sMode in ['flow', 'filter']:
            # Create Tank_1
            matter.store(self, 'Tank_1', self.fStoreVolumes)
            self.toStores.Tank_1.createPhase('air', self.toStores.Tank_1.fVolume, [], [], 2e5)
            matter.procs.exmes.gas(self.toStores.Tank_1.aoPhases[0], 'Port')

            # Create Tank_2
            matter.store(self, 'Tank_2', self.fStoreVolumes)
            self.toStores.Tank_2.createPhase('air', 0)
            matter.procs.exmes.gas(self.toStores.Tank_2.aoPhases[0], 'Port')

            # Create Tank_Mid
            matter.store(self, 'Tank_Mid', self.fStoreVolumes)
            self.toStores.Tank_Mid.createPhase('air', 'flow_phase', self.toStores.Tank_Mid.fVolume)
            matter.procs.exmes.gas(self.toStores.Tank_Mid.aoPhases[0], 'Port_Left')
            matter.procs.exmes.gas(self.toStores.Tank_Mid.aoPhases[0], 'Port_Right')

            # Add filtered phase and DummyAdsorber
            self.toStores.Tank_Mid.createPhase('air', 'filtered', 0)
            tests.performance_test.comps.DummyAdsorber(
                self.toStores.Tank_Mid, 'dummyDing', 'flow_phase', 'filtered', 'O2', float('inf')
            )

        if self.sMode == 'flow':
            # Create pipes and branches
            components.matter.pipe(self, 'Pipe_1', 2.5, 0.005)
            components.matter.pipe(self, 'Pipe_2', 2.5, 0.005)
            matter.branch(self, 'Tank_1.Port', ['Pipe_1'], 'Tank_Mid.Port_Left')
            matter.branch(self, 'Tank_Mid.Port_Right', ['Pipe_2'], 'Tank_2.Port')

    def createSolverStructure(self):
        """
        Create solver structure for the system.
        """
        super().createSolverStructure()

        if self.sSolvers == 'manual':
            # Create solvers for branches
            solver.matter.manual.branch(self.aoBranches[0])
            solver.matter.residual.branch(self.aoBranches[1])

        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute the system logic.
        """
        super().exec()

        # Update logic based on the timer
        if self.oTimer.fTime > self.fLastUpdate:
            fFlowRate = self.aoBranches[0].oHandler.fFlowRate + 0.002

            if fFlowRate > 0.01 or fFlowRate == 0:
                fFlowRate = 0.002

            self.aoBranches[0].oHandler.setFlowRate(fFlowRate)
