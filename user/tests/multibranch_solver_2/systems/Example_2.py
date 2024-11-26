class Example2(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0.
    Two tanks filled with gas at different pressures and a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for Example2 class.
        """
        # Call parent constructor with an interval of 30 seconds.
        super().__init__(oParent, sName, 30)

        # Make the system configurable.
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Create the matter structure for the simulation.
        """
        super().createMatterStructure()

        # Tank 1 with a gas phase
        matter.store(self, "Tank_1", 1)
        oGasPhase = self.toStores.Tank_1.createPhase(
            "gas", "Tank1Air", self.toStores.Tank_1.fVolume,
            {"N2": 8e4, "O2": 2e4, "CO2": 500}, 293, 0.5
        )
        matter.procs.exmes.gas(oGasPhase, "Port_1")
        matter.procs.exmes.gas(oGasPhase, "Port_2")

        # Tank 2 with a gas phase
        matter.store(self, "Tank_2", 1)
        oGasPhase = self.toStores.Tank_2.createPhase(
            "gas", "Tank2Air", self.toStores.Tank_2.fVolume,
            {"N2": 2e5}, 353, 0.5
        )
        matter.procs.exmes.gas(oGasPhase, "Port_1")
        matter.procs.exmes.gas(oGasPhase, "Port_2")

        # Vacuum store
        matter.store(self, "Vacuum", 1e4)
        oVacuum = self.toStores.Vacuum.createPhase(
            "gas", "Vacuum", self.toStores.Vacuum.fVolume,
            {"N2": 1e3}, 293, 0
        )
        matter.procs.exmes.gas(oVacuum, "Port_1")

        # Flow stores
        for i in range(1, 4):
            matter.store(self, f"Flow_{i}", 1e-5)
            oGasPhase = self.toStores[f"Flow_{i}"].createPhase(
                "gas", "flow", "FlowPhase", self.toStores[f"Flow_{i}"].fVolume,
                {"N2": 8e4, "O2": 2e4, "CO2": 500}, 293, 0.5
            )
            matter.procs.exmes.gas(oGasPhase, "Port_1")
            matter.procs.exmes.gas(oGasPhase, "Port_2")
            if i == 2:
                matter.procs.exmes.gas(oGasPhase, "Port_3")

        # Pipes
        for i in range(1, 7):
            components.matter.pipe(
                self, f"Pipe{i}", self.fPipeLength, self.fPipeDiameter, 2e-3
            )

        # Branches
        matter.branch(self, "Tank_1.Port_1", ["Pipe1"], "Flow_1.Port_1", "Branch1")
        matter.branch(self, "Flow_1.Port_2", ["Pipe2"], "Tank_2.Port_1", "Branch2")
        matter.branch(self, "Tank_2.Port_2", ["Pipe3"], "Flow_2.Port_1", "Branch3")
        matter.branch(self, "Flow_2.Port_2", ["Pipe4"], "Tank_1.Port_2", "Branch4")
        matter.branch(self, "Flow_2.Port_3", ["Pipe5"], "Flow_3.Port_1", "Branch5")
        matter.branch(self, "Flow_3.Port_2", ["Pipe6"], "Vacuum.Port_1", "Branch6")

    def createSolverStructure(self):
        """
        Create the solver structure for the simulation.
        """
        super().createSolverStructure()

        # Use iterative solver for all branches.
        solver.matter_multibranch.iterative.branch(self.aoBranches[:], "complex")

        # Set time step properties for Tank_1 and Tank_2
        tTimeProps = {"rMaxChange": 0.1}
        self.toStores.Tank_1.aoPhases[0].setTimeStepProperties(tTimeProps)
        self.toStores.Tank_2.aoPhases[0].setTimeStepProperties(tTimeProps)

        self.setThermalSolvers()

    def exec(self, *args):
        """
        Execute function for this system. Calls the parent exec method.
        """
        super().exec(*args)

        if not base.oDebug.bOff:
            self.out(2, 1, "exec", f"Exec vsys {self.sName}")
