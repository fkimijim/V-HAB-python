class Example_5(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0
    Two tanks filled with gas at different pressures and a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Initialize the system.

        Args:
            oParent: Parent system.
            sName: Name of the system.
        """
        super().__init__(oParent, sName, 100)
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Create the matter structure for the system.
        """
        super().createMatterStructure()

        # Define properties for stores
        aafStores = [
            [1, 1, 3, 0, 5],     # Pressure factors
            [1, 1, 2.5, 100, 0.5]  # Volumes
        ]

        iValves = 2

        # Connections between stores and valves
        # Format: ['Store1', pipe_length, 'Store2']
        cConnections = [
            ['S1', 1, 'V1'],
            ['S2', 2, 'V1'],
            ['V1', 1, 'S3'],
            ['S3', 2, 'V2'],
            ['V2', 5, 'S4'],
            ['V2', 1, 'S5']
        ]

        # Auto-create stores
        for iStore in range(len(aafStores[0])):
            sStore = f"S{iStore + 1}"
            oStore = matter.store(self, sStore, aafStores[1][iStore])
            oStore.createPhase(
                "N2Atmosphere",
                oStore.fVolume,
                293,
                0.5,
                10 ** 5 * aafStores[0][iStore]
            )

        # Auto-create valves
        for iValve in range(1, iValves + 1):
            sValve = f"V{iValve}"
            oStore = matter.store(self, sValve, 1e-6)
            cParams = matter.helper.phase.create.N2Atmosphere(self, oStore.fVolume)
            matter.phases.flow.gas(oStore, "flow", *cParams)

        # Auto-create connections
        for connection in cConnections:
            sBranch = f"{connection[0]}_{connection[2]}"
            sPipe = f"Pipe__{sBranch}"
            sExmeL = f"To__{sBranch}"
            sExmeR = f"From__{sBranch}"

            # Create pipe with specified length
            components.matter.pipe(self, sPipe, connection[1], 0.0035)

            # Create exmes
            oStoreLeft = self.toStores[connection[0]]
            oStoreRight = self.toStores[connection[2]]

            matter.procs.exmes.gas(oStoreLeft.aoPhases[0], sExmeL)
            matter.procs.exmes.gas(oStoreRight.aoPhases[0], sExmeR)

            # Create branch
            matter.branch(
                self,
                f"{connection[0]}.{sExmeL}",
                [sPipe],
                f"{connection[2]}.{sExmeR}"
            )

    def createSolverStructure(self):
        """
        Create the solver structure for the system.
        """
        super().createSolverStructure()
        solver.matter_multibranch.iterative.branch(self.aoBranches, "complex")
        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute the system's main logic.
        """
        super().exec()
