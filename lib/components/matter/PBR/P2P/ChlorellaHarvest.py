class ChlorellaHarvest(matter.procs.p2ps.flow):
    """
    ChlorellaHarvest can harvest chlorella cells out of the harvester in the
    PBR system to maintain continuous growth. Harvesting parameters are based
    on biomass concentration thresholds and filtration efficiency.
    """

    def __init__(self, oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P, oSystem):
        super().__init__(oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P)
        self.oSystem = oSystem  # Connect to PBR system
        
        # Harvesting parameters
        growth_module = self.oSystem.oParent.toChildren.ChlorellaInMedia.oGrowthRateCalculationModule
        self.fStartContinuousHarvestingBiomassConcentration = growth_module.fMaximumGrowthBiomassConcentration * 0.97  # [kg/m3]
        self.fEndContinuousHarvestingBiomassConcentration = growth_module.fMaximumGrowthBiomassConcentration * 1.03  # [kg/m3]
        self.fFiltrationEfficiency = 0.7  # [-] from reference
        self.bHarvest = False  # Initially set to false, changes based on biomass concentration
        self.fVolumetricFlow = self.oSystem.oParent.fVolumetricFlowToHarvester
        
        # P2P-relevant properties
        self.arExtractPartials = [0] * self.oMT.iSubstances
        self.arExtractPartials[self.oMT.tiN2I.Chlorella] = 1  # Define extraction for Chlorella

    def calculateFlowRate(self, _, __, ___, ____):
        """
        Calculate the flow rate based on current biomass concentration
        and update harvesting status.
        """
        # Get the current biomass concentration [kg/m3]
        self.fCurrentBiomassConcentration = self.oSystem.oGrowthRateCalculationModule.fBiomassConcentration

        # Hysteresis behavior: start harvesting above start concentration, stop below end concentration
        if self.fCurrentBiomassConcentration > self.fStartContinuousHarvestingBiomassConcentration:
            self.bHarvest = True
        elif self.fCurrentBiomassConcentration <= self.fEndContinuousHarvestingBiomassConcentration:
            self.bHarvest = False

        # Determine flow rate
        if self.bHarvest:
            afFlowRate, mrPartials = self.getInFlows()

            # Calculate mass flow of desired substance (Chlorella)
            afChlorellaInFlows = [flow * mrPartials[i][self.oMT.tiN2I.Chlorella] for i, flow in enumerate(afFlowRate)]

            fFlowRate = sum(afChlorellaInFlows) * self.fFiltrationEfficiency
        else:
            fFlowRate = 0

        # Set flow rate and update matter properties
        self.setMatterProperties(fFlowRate, self.arExtractPartials)

    def update(self):
        """
        Dummy update method required by V-HAB logic.
        """
        pass
