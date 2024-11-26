class ElectrolyzerReaction:
    """
    Manipulator to model the water splitting reaction occurring within the electrolyzer.
    """

    def __init__(self, sName, oPhase):
        self.sName = sName
        self.oPhase = oPhase

    def update(self):
        # Calculate the resulting molar flow
        fMolarH2Flow = (
            self.oPhase.oStore.oContainer.iCells
            * self.oPhase.oStore.oContainer.fStackCurrent
            / (2 * self.oPhase.oMT.Const.fFaraday)
        )

        # Initialize the array we pass back to the phase once we're done
        afPartialFlows = [0] * self.oPhase.oMT.iSubstances

        # Set the flowrates of the manip
        afPartialFlows[self.oPhase.oMT.tiN2I.H2] = (
            fMolarH2Flow * self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I.H2]
        )
        afPartialFlows[self.oPhase.oMT.tiN2I.O2] = (
            0.5
            * fMolarH2Flow
            * self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I.O2]
        )
        afPartialFlows[self.oPhase.oMT.tiN2I.H2O] = -sum(afPartialFlows)

        # Update the parent class method with the flow rates
        self._update_parent(afPartialFlows)

        # Set the corresponding P2P Flowrates
        afPartialFlowsH2 = [0] * self.oPhase.oMT.iSubstances
        afPartialFlowsH2[self.oPhase.oMT.tiN2I.H2] = afPartialFlows[
            self.oPhase.oMT.tiN2I.H2
        ]
        self.oPhase.oStore.toProcsP2P.H2_from_Membrane.setFlowRate(
            afPartialFlowsH2
        )

        afPartialFlowsO2 = [0] * self.oPhase.oMT.iSubstances
        afPartialFlowsO2[self.oPhase.oMT.tiN2I.O2] = afPartialFlows[
            self.oPhase.oMT.tiN2I.O2
        ]
        self.oPhase.oStore.toProcsP2P.O2_from_Membrane.setFlowRate(
            afPartialFlowsO2
        )

        afPartialFlowsH2O = [0] * self.oPhase.oMT.iSubstances
        afPartialFlowsH2O[self.oPhase.oMT.tiN2I.H2O] = -afPartialFlows[
            self.oPhase.oMT.tiN2I.H2O
        ]
        self.oPhase.oStore.toProcsP2P.H2O_to_Membrane.setFlowRate(
            afPartialFlowsH2O
        )

    def _update_parent(self, afPartialFlows):
        """
        Placeholder for parent class update logic, should be overridden or extended
        based on specific parent behavior.
        """
        # Implement the base class update logic as necessary
        pass
