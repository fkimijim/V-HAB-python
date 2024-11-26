class WaterHarvest(matter.procs.p2ps.flow):
    """
    WaterHarvest harvests water from the harvester in the PBR system. This P2P
    operates on the logic that an equal amount of water is harvested as is supplied
    through urine. The flow rate is determined by the urine supply branch and has
    no further logic implemented.
    """

    def __init__(self, oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P, oSystem):
        super().__init__(oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P)
        self.oSystem = oSystem  # Chlorella in Media

        # P2P-relevant Properties
        # Instantiate Extract Partials array
        self.arExtractPartials = [0] * self.oMT.iSubstances
        # Define water (H2O) as the substance to extract
        self.arExtractPartials[self.oMT.tiN2I.H2O] = 1

    def calculateFlowRate(self, *_):
        """
        Calculate the flow rate and set it for the P2P process.
        The flow rate is based on the urine flow rate, nitrate flow rate, and water surplus.
        """
        # Urine flow comes from the parent system and is defined as negative.
        # PhaseIn for this P2P is harvester, and out is water storage, so it must be positive.

        # Urine flow
        oFlowUrine = self.oSystem.toBranches.Urine_from_PBR.aoFlows
        arResolvedMassesUrine = self.oMT.resolveCompoundMass(
            oFlowUrine.arPartialMass, oFlowUrine.arCompoundMass
        )
        fFlowRateUrine = -oFlowUrine.fFlowRate * arResolvedMassesUrine[self.oMT.tiN2I.H2O]

        # Nitrate flow
        oFlowNitrate = self.oSystem.toBranches.NO3_from_Maintenance.aoFlows
        arResolvedMassesNitrate = self.oMT.resolveCompoundMass(
            oFlowNitrate.arPartialMass, oFlowNitrate.arCompoundMass
        )
        fFlowRateNitrate = -oFlowNitrate.fFlowRate * arResolvedMassesNitrate[self.oMT.tiN2I.H2O]

        # Water surplus in the growth chamber
        oChlorella = self.oStore.oContainer.toChildren.ChlorellaInMedia
        fWaterSurplus = (
            oChlorella.toStores.GrowthChamber.toPhases.GrowthMedium.afMass[self.oMT.tiN2I.H2O]
            - oChlorella.tfGrowthChamberComponents.H2O
        ) / (2 * self.oStore.oContainer.fTimeStep)

        # Total flow rate
        fFlowRate = fFlowRateUrine + fFlowRateNitrate + fWaterSurplus
        if fFlowRate < 0:
            fFlowRate = 0

        # Set the flow rate and update the matter properties
        self.setMatterProperties(fFlowRate, self.arExtractPartials)

    def update(self):
        """
        Placeholder for the update method, required by V-HAB logic.
        """
        pass
