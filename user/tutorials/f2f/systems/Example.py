class Example(vsys):
    """
    Example simulation demonstrating the use of f2f processors.
    The model contains three tanks filled with gas at different pressures.
    Between each tank are two pipes with a valve in the middle, connecting the tanks in series.
    """

    # Fixed properties
    fPipeLength = 1.0  # Standard pipe length for this tutorial
    fPipeDiameter = 0.0035  # Standard pipe diameter for this tutorial
    aiExmes = [1, 2, 1]  # How many exmes to create?

    # Editable properties
    afStoreVolumes = [50, 50, 50]  # Store volumes in m^3
    arPressures = [2, 1, 3]  # Pressures for each tank

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 100)
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        iNumberOfTanks = len(self.afStoreVolumes)

        # Create stores with phases and exmes
        for iStore in range(1, iNumberOfTanks + 1):
            sStoreName = f"Tank_{iStore}"
            matter.store(self, sStoreName, self.afStoreVolumes[iStore - 1])

            self.toStores[sStoreName].createPhase(
                'air',
                self.toStores[sStoreName].fVolume,
                293,
                0.5,
                10**5 * self.arPressures[iStore - 1]
            )

            if self.aiExmes[iStore - 1] == 1:
                matter.procs.exmes.gas(self.toStores[sStoreName].aoPhases[0], 'Port')
            else:
                for iExMe in range(1, self.aiExmes[iStore - 1] + 1):
                    matter.procs.exmes.gas(
                        self.toStores[sStoreName].aoPhases[0], f"Port_{iExMe}"
                    )

        # Create branches with pipes and valves
        iNumberOfBranches = iNumberOfTanks - 1

        for iBranch in range(1, iNumberOfBranches + 1):
            csFlowProcs = [
                components.matter.pipe(
                    self, f"Pipe_{iBranch}{iBranch + 1}_1", self.fPipeLength, self.fPipeDiameter
                ).sName,
                components.matter.valve(
                    self, f"Valve_{iBranch}{iBranch + 1}"
                ).sName,
                components.matter.pipe(
                    self, f"Pipe_{iBranch}{iBranch + 1}_2", self.fPipeLength, self.fPipeDiameter
                ).sName,
            ]

            if iBranch == 1:
                csFlowProcs.append(
                    components.matter.checkvalve(
                        self, f"Checkvalve_{iBranch}{iBranch + 1}"
                    ).sName
                )

            sStoreLeft = f"Tank_{iBranch}.Port"
            sStoreRight = (
                f"Tank_{iBranch + 1}.Port"
                if iBranch == iNumberOfBranches
                else f"Tank_{iBranch + 1}.Port_1"
            )

            matter.branch(self, sStoreLeft, csFlowProcs, sStoreRight)

    def createSolverStructure(self):
        super().createSolverStructure()

        for iB in range(len(self.afStoreVolumes) - 1):
            solver.matter.interval.branch(self.aoBranches[iB])

        self.setThermalSolvers()

    def exec(self, _):
        super().exec(_)

        # Open/Close valves every 50 seconds between 7200 and 9000 seconds
        if 7200 - self.fTimeStep < self.oTimer.fTime < 9000:
            if self.fTimeStep != 1:
                self.setTimeStep(50)

            if not self.toProcsF2F.Valve_12.bOpen and not self.toProcsF2F.Valve_23.bOpen:
                self.toProcsF2F.Valve_12.setOpen(True)
            elif self.toProcsF2F.Valve_12.bOpen and not self.toProcsF2F.Valve_23.bOpen:
                self.toProcsF2F.Valve_23.setOpen(True)
            elif not self.toProcsF2F.Valve_12.bOpen and self.toProcsF2F.Valve_23.bOpen:
                self.toProcsF2F.Valve_23.setOpen(False)
            else:  # both open
                self.toProcsF2F.Valve_12.setOpen(False)

        # Emulate Cvs
        elif 1800 - self.fTimeStep < self.oTimer.fTime < 5400:
            if self.fTimeStep != 5:
                self.setTimeStep(5)

        # Reset to defaults
        else:
            if self.fTimeStep != 100:
                self.setTimeStep(100)

            if not self.toProcsF2F.Valve_12.bOpen:
                self.toProcsF2F.Valve_12.setOpen(True)
            if not self.toProcsF2F.Valve_23.bOpen:
                self.toProcsF2F.Valve_23.setOpen(True)
