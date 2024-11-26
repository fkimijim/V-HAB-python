class ExampleSubsystem(vsys):
    """
    ExampleSubsystem
    A subsystem containing a filter and a pipe.
    Demonstrates a vsys child representing a subsystem of a larger system.
    It has a filter that removes O2 from the mass flow through the subsystem
    and provides the necessary setIfFlows() method to connect subsystem
    branches to system-level branches.
    """

    def __init__(self, oParent, sName):
        """
        Initializes the ExampleSubsystem.
        """
        super().__init__(oParent, sName)

        # Execute additional configuration code if available
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Creates the matter structure for the subsystem.
        """
        super().createMatterStructure()

        # Define filter volume
        fFilterVolume = 1
        matter.store(self, 'Filter', fFilterVolume)

        # Create phases
        oFlow = self.toStores.Filter.createPhase(
            'gas', 'flow', 'FlowPhase', 1e-6,
            {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5
        )
        oFiltered = matter.phases.mixture(
            self.toStores.Filter, 'FilteredPhase', 'solid',
            {'Zeolite13x': 1}, 293, 1e5
        )

        # Add an absorber example flow processor
        tutorials.p2p.flow.components.AbsorberExampleFlow(
            self.toStores.Filter, 'filterproc', oFlow, oFiltered
        )

        # Add subsystem pipes with unique names
        components.matter.pipe(self, 'SubsystemPipe1', 1, 0.005)
        components.matter.pipe(self, 'SubsystemPipe2', 1, 0.005)

        # Define interfaces to the parent system
        matter.branch(self, oFlow, ['SubsystemPipe1'], 'Inlet')
        matter.branch(self, oFlow, ['SubsystemPipe2'], 'Outlet')

    def createSolverStructure(self):
        """
        Creates the solver structure for the subsystem.
        """
        super().createSolverStructure()

        # Assign iterative solver to subsystem branches
        solver.matter_multibranch.iterative.branch(self.aoBranches, 'complex')

        # Set thermal solvers
        self.setThermalSolvers()

    def setIfFlows(self, *args):
        """
        Connects the parent system and subsystem level branches.

        Args:
            *args: Strings representing parent system interfaces (e.g., Inlet and Outlet).
        """
        if len(args) != 2:
            raise ValueError('Wrong number of interfaces provided to ExampleSubsystem')

        # Connect subsystem interfaces to parent system interfaces
        self.connectIF('Inlet', args[0])
        self.connectIF('Outlet', args[1])

    def exec(self, *args):
        """
        Execute function for the subsystem.
        """
        super().exec(*args)
