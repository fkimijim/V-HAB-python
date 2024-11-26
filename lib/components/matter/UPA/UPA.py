class UPA(vsys):
    """
    UPA: A simple model of the Urine Processing Assembly used on the ISS.
    It models delays and recovery rates and is not based on first principles.
    """

    def __init__(self, oParent, sName, fTimeStep=60, *args):
        super().__init__(oParent, sName, fTimeStep)
        self.fBaseFlowRate = 1.7361e-4  # Flowrate in kg/s
        self.fWSTACapacity = 13 * 0.998  # WSTA capacity in liters
        self.fARTFACapacity = 22.5 * 0.998  # ARTFA capacity in liters
        self.bProcessing = False
        self.fProcessingFinishTime = -20000
        self.fUPAActivationFill = 0.70 * self.fWSTACapacity
        self.fTankCapacityNotProcessed = 0.08 * self.fWSTACapacity
        self.fPower = 56  # Power usage in standby [W]
        self.bManualUrineSupply = False
        self.fInitialMassParentUrineSupply = 0

    def createMatterStructure(self):
        super().createMatterStructure()

        # WSTA (Wastewater Storage Tank Assembly)
        matter.store(self, "WSTA", self.fWSTACapacity / 998)
        matter.phases.mixture(
            self.toStores.WSTA, "Urine", "liquid", {"Urine": self.fUPAActivationFill + 0.1}, 293, 1e5
        )

        # ARTFA (Advanced Recycle Filter Tank Assembly)
        matter.store(self, "ARTFA", self.fARTFACapacity / 998)
        matter.phases.mixture(
            self.toStores.ARTFA, "Brine", "liquid", {"Brine": 0.1}, 293, 1e5
        )

        # Distillation Assembly
        matter.store(self, "DistillationAssembly", 3e-3)
        self.toStores.DistillationAssembly.createPhase(
            "mixture", "Urine", "liquid", 1e-3, {"Urine": 1}, 293, 1e5
        )
        self.toStores.DistillationAssembly.createPhase(
            "mixture", "Brine", "liquid", 1e-3, {"Brine": 1}, 293, 1e5
        )
        self.toStores.DistillationAssembly.createPhase(
            "liquid", "H2O", 1e-3, {"H2O": 1}, 293, 1e5
        )

        # ExMes for WSTA and ARTFA
        matter.procs.exmes.mixture(self.toStores.WSTA.toPhases.Urine, "Inlet")
        matter.procs.exmes.mixture(self.toStores.WSTA.toPhases.Urine, "WSTA_to_Distillation")
        matter.procs.exmes.liquid(self.toStores.DistillationAssembly.toPhases.H2O, "Outlet")
        matter.procs.exmes.liquid(self.toStores.DistillationAssembly.toPhases.H2O, "Water_from_P2P")
        matter.procs.exmes.mixture(self.toStores.DistillationAssembly.toPhases.Urine, "Water_from_WSTA")
        matter.procs.exmes.mixture(self.toStores.DistillationAssembly.toPhases.Urine, "Brine_to_P2P")
        matter.procs.exmes.mixture(self.toStores.DistillationAssembly.toPhases.Urine, "Water_to_P2P")
        matter.procs.exmes.mixture(self.toStores.DistillationAssembly.toPhases.Brine, "Brine_to_ARTFA")
        matter.procs.exmes.mixture(self.toStores.DistillationAssembly.toPhases.Brine, "Brine_from_P2P")
        matter.procs.exmes.mixture(self.toStores.ARTFA.toPhases.Brine, "Brine_from_Distillation")
        matter.procs.exmes.mixture(self.toStores.ARTFA.toPhases.Brine, "Brine_to_Outlet")

        # P2Ps for Distillation Assembly
        components.matter.P2Ps.ManualP2P(
            self.toStores.DistillationAssembly, "BrineP2P", "Urine.Brine_to_P2P", "Brine.Brine_from_P2P"
        )
        components.matter.P2Ps.ManualP2P(
            self.toStores.DistillationAssembly, "WaterP2P", "Urine.Water_to_P2P", "H2O.Water_from_P2P"
        )

        # Branches
        matter.branch(self, "WSTA.Inlet", {}, "Inlet", "Inlet")
        matter.branch(self, "DistillationAssembly.Outlet", {}, "Outlet", "Outlet")
        matter.branch(self, "ARTFA.Brine_to_Outlet", {}, "BrineOutlet", "BrineOutlet")
        matter.branch(self, "WSTA.WSTA_to_Distillation", {}, "DistillationAssembly.Water_from_WSTA", "WSTA_to_DA")
        matter.branch(self, "DistillationAssembly.Brine_to_ARTFA", {}, "ARTFA.Brine_from_Distillation", "DA_to_ARTFA")

        # Manipulator
        components.matter.UPA.components.UPA_Manip(
            "UPA_Manip", self.toStores.DistillationAssembly.toPhases.Urine
        )

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.manual.branch(self.toBranches.Inlet)
        solver.matter.manual.branch(self.toBranches.Outlet)
        solver.matter.manual.branch(self.toBranches.BrineOutlet)
        solver.matter.manual.branch(self.toBranches.WSTA_to_DA)
        solver.matter.residual.branch(self.toBranches.DA_to_ARTFA)

        # ARTFA timestep properties
        tTimeStepProperties = {"rMaxChange": float("inf"), "fMaxStep": 5 * self.fTimeStep}
        self.toStores.ARTFA.toPhases.Brine.setTimeStepProperties(tTimeStepProperties)

        tTimeStepProperties = {"rMaxChange": float("inf"), "fMaxStep": 5 * self.fTimeStep}
        self.toStores.WSTA.toPhases.Urine.setTimeStepProperties(tTimeStepProperties)

        self.setThermalSolvers()

    def setUrineSupplyToManual(self, bManualUrineSupply):
        self.bManualUrineSupply = bManualUrineSupply

    def setIfFlows(self, sInlet, sOutlet, sBrineOutlet):
        self.connectIF("Inlet", sInlet)
        self.connectIF("Outlet", sOutlet)
        self.connectIF("BrineOutlet", sBrineOutlet)
        self.fInitialMassParentUrineSupply = self.toBranches.Inlet.coExmes[1].oPhase.fMass

    def exec(self, _):
        super().exec()

        if not self.bManualUrineSupply and self.toStores.WSTA.toPhases.Urine.fMass < self.fWSTACapacity:
            fDesiredUrineMass = self.fWSTACapacity - self.toStores.WSTA.toPhases.Urine.fMass
            fCurrentlyAvailableUrineParent = (
                self.toBranches.Inlet.coExmes[1].oPhase.fMass - self.fInitialMassParentUrineSupply
            )
            if fCurrentlyAvailableUrineParent > 0:
                if not self.toBranches.Inlet.oHandler.bMassTransferActive:
                    if fCurrentlyAvailableUrineParent > fDesiredUrineMass:
                        self.toBranches.Inlet.oHandler.setMassTransfer(-fDesiredUrineMass, 60)
                    else:
                        self.toBranches.Inlet.oHandler.setMassTransfer(-fCurrentlyAvailableUrineParent, 60)

        if (
            self.toStores.WSTA.toPhases.Urine.fMass >= self.fUPAActivationFill
            and self.oTimer.fTime - self.fProcessingFinishTime > 18000
        ):
            self.bProcessing = True
            self.fProcessingFinishTime = float("inf")

        if self.bProcessing:
            if self.oTimer.fTime >= self.fProcessingFinishTime:
                self.toStores.DistillationAssembly.toPhases.Urine.toManips.substance.setActive(False)
                self.bProcessing = False
                self.fPower = 56
            elif self.toStores.WSTA.toPhases.Urine.fMass >= self.fTankCapacityNotProcessed:
                if not self.toBranches.WSTA_to_DA.oHandler.bMassTransferActive:
                    self.toStores.DistillationAssembly.toPhases.Urine.toManips.substance.setActive(True)
                    fMassToProcess = self.toStores.WSTA.toPhases.Urine.fMass - self.fTankCapacityNotProcessed
                    fTimeToProcess = fMassToProcess / self.fBaseFlowRate
                    self.fProcessingFinishTime = self.oTimer.fTime + fTimeToProcess
                    self.toBranches.WSTA_to_DA.oHandler.setMassTransfer(fMassToProcess, fTimeToProcess)
                    self.fPower = 315

        if self.toStores.ARTFA.toPhases.Brine.fMass >= self.fARTFACapacity + 0.1:
            self.toBranches.BrineOutlet.oHandler.setMassTransfer(
                self.toStores.ARTFA.toPhases.Brine.fMass - 0.1, 300
            )
