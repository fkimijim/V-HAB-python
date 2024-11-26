class BPA_Manip:
    """
    BPA_Manip is a manipulator that processes brine into water and concentrated brine
    based on the given conversion efficiency.
    """

    def __init__(self, sName, oPhase):
        """
        Constructor for BPA_Manip.

        :param sName: Name of the manipulator.
        :param oPhase: Phase object associated with the manipulator.
        """
        self.sName = sName
        self.oPhase = oPhase

        # Brine conversion efficiency
        self.rBrineConversionEfficiency = 0.8

        # Activity status of the manipulator
        self.bActive = False

        # Initial and last calculated water content in brine
        self.rInitialWaterInBrine = 0
        self.rLastCalcWaterInBrine = 0

        # Flow rates for concentrated brine
        self.aarConcentratedBrineFlowsToCompound = None

    def setActive(self, bActive):
        """
        Set the active state of the manipulator.

        :param bActive: Boolean indicating whether the manipulator is active.
        """
        self.bActive = bActive

    def update(self):
        """
        Updates the manipulator's state and calculates brine processing.
        """
        # Initialize the array to pass back to the phase
        afPartialFlows = [0] * self.oPhase.oMT.iSubstances

        if self.bActive and self.oPhase.afMass[self.oPhase.oMT.tiN2I['Brine']] > 0:
            # Abbreviate some variables for clarity
            tiN2I = self.oPhase.oMT.tiN2I

            afResolvedMass = self.oPhase.oMT.resolveCompoundMass(
                self.oPhase.afMass, self.oPhase.arCompoundMass
            )

            afResolvedMass = [resolved - mass for resolved, mass in zip(afResolvedMass, self.oPhase.afMass)]
            for i, is_compound in enumerate(self.oPhase.oMT.abCompound):
                if is_compound:
                    afResolvedMass[i] = 0

            rWaterInBrine = afResolvedMass[tiN2I['H2O']] / self.oPhase.fMass

            if rWaterInBrine > self.rLastCalcWaterInBrine:
                # Processing a new batch
                self.rInitialWaterInBrine = rWaterInBrine

                rConcentratedBrineWaterContent = (
                    (1 - self.rBrineConversionEfficiency) * self.rInitialWaterInBrine
                )
                afConcentratedBrineMasses = afResolvedMass[:]
                afConcentratedBrineMasses[tiN2I['H2O']] = (
                    afResolvedMass[tiN2I['H2O']] * rConcentratedBrineWaterContent
                )
                total_concentrated_mass = sum(afConcentratedBrineMasses)
                self.aarConcentratedBrineFlowsToCompound = [
                    [
                        mass / total_concentrated_mass if total_concentrated_mass > 0 else 0
                        for mass in afConcentratedBrineMasses
                    ]
                ]

            # Update partial flows for the manipulator
            afPartialFlows[tiN2I['Brine']] = -1 * self.oPhase.oStore.oContainer.fBaseFlowRate

            afPartialFlows[tiN2I['H2O']] = (
                self.rBrineConversionEfficiency
                * self.rInitialWaterInBrine
                * self.oPhase.oStore.oContainer.fBaseFlowRate
            )

            afPartialFlows[tiN2I['ConcentratedBrine']] = (
                self.oPhase.oStore.oContainer.fBaseFlowRate - afPartialFlows[tiN2I['H2O']]
            )

            # Call the parent update method
            self.update_substance(afPartialFlows, self.aarConcentratedBrineFlowsToCompound)

            # Handle water P2P flows
            afWaterP2PFlows = [0] * self.oPhase.oMT.iSubstances
            afWaterP2PFlows[tiN2I['H2O']] = afPartialFlows[tiN2I['H2O']]
            self.oPhase.oStore.toProcsP2P['WaterP2P'].setFlowRate(afWaterP2PFlows)

            self.rLastCalcWaterInBrine = rWaterInBrine
        else:
            # If inactive or no brine available, reset flow rates
            self.update_substance(afPartialFlows)

            afWaterP2PFlows = [0] * self.oPhase.oMT.iSubstances
            self.oPhase.oStore.toProcsP2P['WaterP2P'].setFlowRate(afWaterP2PFlows)

    def update_substance(self, afPartialFlows, aarConcentratedBrineFlowsToCompound=None):
        """
        Placeholder for the parent `update` method from `matter.manips.substance.stationary`.

        :param afPartialFlows: List of partial flows to update.
        :param aarConcentratedBrineFlowsToCompound: Optional matrix for brine flow composition.
        """
        # Implementation required to integrate with the simulation framework
        pass
