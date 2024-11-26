class Example(vsys):
    """
    Example simulation for V-HAB including a manipulator.
    Creates two tanks with 1 and 2 atmospheres of pressure, respectively.
    The tanks are connected via two pipes. In between the pipes, there is
    a simple model of a Bosch reactor system, removing CO2 from the air flow
    and reducing it to C and O2.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example simulation class.

        Args:
            oParent (object): Parent system.
            sName (str): Name of the simulation.
        """
        super().__init__(oParent, sName, 30)

    def createMatterStructure(self):
        """
        Create the matter structure for the simulation.
        """
        super().createMatterStructure()

        # Create Tank_1 with air and an outlet
        self.toStores["Tank_1"] = matter.store(self, "Tank_1", 10)
        oAir = self.toStores["Tank_1"].createPhase("air", 10, 293, 0.5, 2e5)
        matter.procs.exmes.gas(oAir, "Outlet")

        # Create Tank_2 with air and an inlet
        self.toStores["Tank_2"] = matter.store(self, "Tank_2", 10)
        oAir = self.toStores["Tank_2"].createPhase("air", 10)
        matter.procs.exmes.gas(oAir, "Inlet")

        # Create Reactor with two phases
        fReactorVolume = 1
        self.toStores["Reactor"] = matter.store(self, "Reactor", fReactorVolume)
        oFlowPhase = self.toStores["Reactor"].createPhase("air", "FlowPhase", fReactorVolume / 2)
        oFilteredPhase = self.toStores["Reactor"].createPhase("air", "FilteredPhase", fReactorVolume / 2)

        # Add exmes to the reactor phases
        matter.procs.exmes.gas(oFlowPhase, "Inlet")
        matter.procs.exmes.gas(oFlowPhase, "Outlet")
        matter.procs.exmes.gas(oFlowPhase, "FilterPortIn")
        matter.procs.exmes.gas(oFilteredPhase, "FilterPortOut")

        # Create the DummyBoschProcess manipulator
        tutorials.manipulator.components.DummyBoschProcess("DummyBoschProcess", oFlowPhase)

        # Add a P2P process for carbon transfer between phases
        components.matter.P2Ps.ConstantMassP2P(
            self.toStores["Reactor"],
            "FilterProc",
            "FlowPhase.FilterPortIn",
            "FilteredPhase.FilterPortOut",
            ["C"],
            1
        )

        # Add pipes connecting the tanks and reactor
        components.matter.pipe(self, "Pipe_1", 0.5, 0.005)
        components.matter.pipe(self, "Pipe_2", 0.5, 0.005)

        # Create branches
        matter.branch(self, "Tank_1.Outlet", ["Pipe_1"], "Reactor.Inlet")
        matter.branch(self, "Reactor.Outlet", ["Pipe_2"], "Tank_2.Inlet")

    def createSolverStructure(self):
        """
        Create the solver structure for the simulation.
        """
        super().createSolverStructure()

        solver.matter.interval.branch(self.aoBranches[0])
        solver.matter.interval.branch(self.aoBranches[1])

        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute the simulation.
        """
        super().exec()
