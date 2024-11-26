class Example4(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0.
    Two tanks filled with gas at different pressures and a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example_4 class.

        Args:
            oParent: Parent object.
            sName: Name of the system.
        """
        super().__init__(oParent, sName, 100)

        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Creates the matter structure of the simulation.
        """
        super().createMatterStructure()

        # Main Store
        matter.store(self, "Store", 100)
        self.toStores.Store.createPhase("N2Atmosphere", self.toStores.Store.fVolume)
        matter.procs.exmes.gas(self.toStores.Store.aoPhases[0], "Port_Out")
        matter.procs.exmes.gas(self.toStores.Store.aoPhases[0], "Port_Rtn")

        # Plenum
        oPlenum = matter.store(self, "Plenum", 0.001)
        oPhase = oPlenum.createPhase("N2Atmosphere", "flow", oPlenum.fVolume)

        # Valves
        iValves = 4
        for iT in range(1, iValves + 1):
            sN = f"Valve_{iT}"
            matter.store(self, sN, 1e-6)
            cParams = matter.helper.phase.create.N2Atmosphere(self, self.toStores[sN].fVolume)
            matter.phases.flow.gas(self.toStores[sN], "flow", *cParams)
            matter.procs.exmes.gas(self.toStores[sN].aoPhases[0], "Port_1")
            matter.procs.exmes.gas(self.toStores[sN].aoPhases[0], "Port_2")
            matter.procs.exmes.gas(self.toStores[sN].aoPhases[0], "Port_3")

        # Pipes
        for iP in range(1, iValves + 4):
            components.matter.pipe(self, f"Pipe_{iP}", self.fPipeLength, self.fPipeDiameter)

        # Resistors
        components.matter.pipe(self, "R_1", 0.1, 0.001)
        components.matter.pipe(self, "R_4", 0.1, 0.001)
        components.matter.pipe(self, "R_5", 0.1, 0.001)

        # Fan
        components.matter.fan_simple(self, "Fan", 600, False)

        # Branches
        matter.branch(self, "Store.Port_Out", ["Pipe_1"], oPhase)

        matter.branch(self, oPhase, ["Fan"], "Valve_1.Port_1")
        matter.branch(self, "Valve_1.Port_2", ["Pipe_2"], "Valve_2.Port_1")
        matter.branch(self, "Valve_1.Port_3", ["Pipe_3"], "Valve_3.Port_1")

        matter.branch(self, "Valve_2.Port_2", ["Pipe_4", "R_4", "R_5"], "Valve_3.Port_2")
        matter.branch(self, "Valve_2.Port_3", ["Pipe_5", "R_1"], "Valve_4.Port_1")

        matter.branch(self, "Valve_3.Port_3", ["Pipe_6"], "Valve_4.Port_2")
        matter.branch(self, "Valve_4.Port_3", ["Pipe_7"], "Store.Port_Rtn")

    def createSolverStructure(self):
        """
        Configures the solver structure for the system.
        """
        super().createSolverStructure()

        solver.matter_multibranch.iterative.branch(self.aoBranches, "complex")
        self.setThermalSolvers()

    def exec(self, _):
        """
        Executes the system logic at each time step.
        """
        super().exec()
