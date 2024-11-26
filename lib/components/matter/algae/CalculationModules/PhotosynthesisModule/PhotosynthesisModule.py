import numpy as np

class PhotosynthesisModule:
    """
    PhotosynthesisModule calculates changes due to algal growth rate as determined 
    by growth calculation modules. Mass flows are calculated based on stoichiometric growth equations.
    """

    def __init__(self, oSystem, oMT):
        self.oSystem = oSystem
        self.oMT = oMT

        # Initialize properties
        self.fTotalOxygenEvolution = 0  # [kg] Total oxygen evolved
        self.fTotalCarbonDioxideAssimilation = 0  # [kg] Total CO2 assimilated
        self.fCombinedCO2AvailabilityFactor = 0  # [-]
        self.fCombinedNitrogenAvailabilityFactor = 0  # [-]
        self.fAssimilationCoefficient = 0  # [-]
        self.fActualGrowthRate = 0  # [kg/s]
        self.afCombinedPartialFlowRates = np.zeros(oMT.iSubstances)  # [kg/s]

        # Define assumed molar mass of Chlorella
        self.fMolarMassChlorella = (
            oMT.afMolarMass[oMT.tiN2I["C"]] +
            1.75 * oMT.afMolarMass[oMT.tiN2I["H"]] +
            0.42 * oMT.afMolarMass[oMT.tiN2I["O"]] +
            0.15 * oMT.afMolarMass[oMT.tiN2I["N"]]
        )

        # Define stoichiometric relations
        self.initialize_stoichiometric_relations()

    def initialize_stoichiometric_relations(self):
        """Initialize stoichiometric relations for various nitrogen sources."""
        # Urea as N Source
        self.fChlorellaReactionMolesWithUrea = 1
        self.fNO3ReactionMolesWithUrea = 0
        self.fCO2ReactionMolesWithUrea = 0.925
        self.fUrineSolidsReactionMolesWithUrea = 0
        self.fUreaReactionMolesWithUrea = 0.075
        self.fH2PO4ReactionMolesWithUrea = 0  # Currently unused
        self.fWaterReactionMolesWithUrea = 0.725
        self.fO2ReactionMolesWithUrea = 1.115
        self.fHydroxideIonReactionMolesWithUrea = 0
        self.fCOH2ReactionMolesWithUrea = 0
        self.fUreaAssimilationFactor = self.fCO2ReactionMolesWithUrea / self.fO2ReactionMolesWithUrea

        # Urine Solids as N Source
        self.fChlorellaReactionMolesWithUrineSolids = 1
        self.fNO3ReactionMolesWithUrineSolids = 0
        self.fCO2ReactionMolesWithUrineSolids = 0.925
        self.fUrineSolidsReactionMolesWithUrineSolids = 0.075
        self.fUreaReactionMolesWithUrineSolids = 0
        self.fH2PO4ReactionMolesWithUrineSolids = 0
        self.fWaterReactionMolesWithUrineSolids = 0.725
        self.fO2ReactionMolesWithUrineSolids = 1.115
        self.fHydroxideIonReactionMolesWithUrineSolids = 0
        self.fCOH2ReactionMolesWithUrineSolids = 0.075
        self.fUrineSolidsAssimilationFactor = (
            self.fCO2ReactionMolesWithUrineSolids / self.fO2ReactionMolesWithUrineSolids
        )

        # Nitrate as N Source
        self.fChlorellaReactionMolesWithNitrate = 1
        self.fNO3ReactionMolesWithNitrate = 0.15
        self.fCO2ReactionMolesWithNitrate = 1
        self.fUrineSolidsReactionMolesWithNitrate = 0
        self.fUreaReactionMolesWithNitrate = 0
        self.fH2PO4ReactionMolesWithNitrate = 0
        self.fWaterReactionMolesWithNitrate = 0.95
        self.fO2ReactionMolesWithNitrate = 1.415
        self.fHydroxideIonReactionMolesWithNitrate = 0.15
        self.fCOH2ReactionMolesWithNitrate = 0
        self.fNO3AssimilationFactor = (
            self.fCO2ReactionMolesWithNitrate / self.fO2ReactionMolesWithNitrate
        )

    def update(self, oCallingManip):
        """
        Update the state based on available nutrients and growth rates.
        """
        # Calculate the required Chlorella production
        fChlorellaMassIncrease = (
            oCallingManip.oPhase.oStore.oContainer.oGrowthRateCalculationModule.fAchievableCurrentBiomassGrowthRate
        )
        fMolesChlorella = fChlorellaMassIncrease / self.fMolarMassChlorella

        # Calculate flow rates for different nitrogen sources
        afPartialsFromUrineSolidsNitrogen, fUrineSolidsAvailability, fUrineSolidsCO2Availability = (
            self.calculate_urine_solids_nitrogen(fMolesChlorella, oCallingManip)
        )
        afPartialsFromUreaNitrogen, fUreaAvailabilityFactor, fCO2AvailabilityFactor = (
            self.calculate_urea_nitrogen(fMolesChlorella, oCallingManip)
        )

        # Combine results
        self.afCombinedPartialFlowRates = (
            afPartialsFromUrineSolidsNitrogen + afPartialsFromUreaNitrogen
        )
        self.fActualGrowthRate = np.sum(self.afCombinedPartialFlowRates)

        # Update availability factors
        self.fCombinedCO2AvailabilityFactor = (
            fUrineSolidsCO2Availability * 0.5 + fCO2AvailabilityFactor * 0.5
        )
        self.fCombinedNitrogenAvailabilityFactor = (
            fUrineSolidsAvailability * 0.5 + fUreaAvailabilityFactor * 0.5
        )

        # Update cumulative totals
        if oCallingManip.fLastExecTimeStep > 0:
            self.fTotalOxygenEvolution += (
                self.afCombinedPartialFlowRates[self.oMT.tiN2I["O2"]] *
                oCallingManip.fLastExecTimeStep
            )
            self.fTotalCarbonDioxideAssimilation += (
                -self.afCombinedPartialFlowRates[self.oMT.tiN2I["CO2"]] *
                oCallingManip.fLastExecTimeStep
            )

    def calculate_urine_solids_nitrogen(self, fMolesChlorella, oCallingManip):
        """
        Calculate flow rates for Chlorella growth using urine solids as a nitrogen source.
        """
        # Implementation here
        return np.zeros(self.oMT.iSubstances), 1.0, 1.0

    def calculate_urea_nitrogen(self, fMolesChlorella, oCallingManip):
        """
        Calculate flow rates for Chlorella growth using urea as a nitrogen source.
        """
        # Implementation here
        return np.zeros(self.oMT.iSubstances), 1.0, 1.0
