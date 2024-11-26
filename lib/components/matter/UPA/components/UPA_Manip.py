class UPA_Manip(matter.manips.substance.stationary):
    """
    UPA_Manip: A manipulator for processing urine into water and brine, 
    using a defined conversion efficiency.
    """
    def __init__(self, sName, oPhase):
        super().__init__(sName, oPhase)
        # Urine conversion efficiency from literature
        self.rUrineConversionEfficiency = 0.85
        self.bActive = False

    def setActive(self, bActive):
        """
        Set the activity state of the manipulator.
        """
        self.bActive = bActive

    def update(self):
        """
        Update the manipulator's behavior based on current conditions.
        """
        # Initialize the array for changes to the phase's partial flows
        afPartialFlows = [0] * self.oPhase.oMT.iSubstances

        if self.bActive:
            # Abbreviating for clarity
            tiN2I = self.oPhase.oMT.tiN2I

            # Resolve the compound mass in the current phase
            afResolvedMass = self.oPhase.oMT.resolveCompoundMass(self.oPhase.afMass, self.oPhase.arCompoundMass)

            # Calculate differences and isolate non-compound substances
            afResolvedMass = [resolved - mass for resolved, mass in zip(afResolvedMass, self.oPhase.afMass)]
            for i, isCompound in enumerate(self.oMT.abCompound):
                if isCompound:
                    afResolvedMass[i] = 0

            rWaterInUrine = afResolvedMass[tiN2I["H2O"]] / self.oPhase.afMass[tiN2I["Urine"]]
            rBrineWaterContent = (1 - self.rUrineConversionEfficiency) * rWaterInUrine

            afBrineMasses = afResolvedMass[:]
            afBrineMasses[tiN2I["H2O"]] = afResolvedMass[tiN2I["H2O"]] * rBrineWaterContent

            aarFlowsToCompound = [[0] * self.oMT.iSubstances for _ in range(self.oMT.iSubstances)]
            totalBrineMass = sum(afBrineMasses)
            if totalBrineMass > 0:
                for i in range(self.oMT.iSubstances):
                    aarFlowsToCompound[tiN2I["Brine"]][i] = afBrineMasses[i] / totalBrineMass

            # Update the partial flows for urine, water, and brine
            fBaseFlowRate = self.oPhase.oStore.oContainer.fBaseFlowRate
            afPartialFlows[tiN2I["Urine"]] = -fBaseFlowRate
            afPartialFlows[tiN2I["H2O"]] = self.rUrineConversionEfficiency * rWaterInUrine * fBaseFlowRate
            afPartialFlows[tiN2I["Brine"]] = fBaseFlowRate - afPartialFlows[tiN2I["H2O"]]

            # Update the parent class and set flow rates
            super().update(afPartialFlows, aarFlowsToCompound)

            afBrineP2PFlows = [0] * self.oPhase.oMT.iSubstances
            afBrineP2PFlows[tiN2I["Brine"]] = afPartialFlows[tiN2I["Brine"]]
            self.oPhase.oStore.toProcsP2P.BrineP2P.setFlowRate(afBrineP2PFlows)

            afWaterP2PFlows = [0] * self.oPhase.oMT.iSubstances
            afWaterP2PFlows[tiN2I["H2O"]] = afPartialFlows[tiN2I["H2O"]]
            self.oPhase.oStore.toProcsP2P.WaterP2P.setFlowRate(afWaterP2PFlows)

            self.oPhase.oStore.oContainer.toBranches.Outlet.oHandler.setFlowRate(afPartialFlows[tiN2I["H2O"]])
        else:
            # If inactive, set all flows to zero
            self.oPhase.oStore.toProcsP2P.BrineP2P.setFlowRate([0] * self.oPhase.oMT.iSubstances)
            self.oPhase.oStore.toProcsP2P.WaterP2P.setFlowRate([0] * self.oPhase.oMT.iSubstances)
            self.oPhase.oStore.oContainer.toBranches.Outlet.oHandler.setFlowRate(0)

            # Update the parent class with zero flows
            super().update(afPartialFlows)
