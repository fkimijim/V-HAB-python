import numpy as np

class AcidOnCalcite:
    """
    AcidOnCalcite class for simulating the effect of acid on calcite dissolution.
    """

    def __init__(self, sName, oPhase):
        # Properties
        self.fCurrentpH = None
        self.fVolume = None
        self.afPolynomialCoeff = np.zeros(11)
        self.fCalculatedCaConcentration = None
        self.fCalculatedMolesCalcium = None
        self.fCalculatedMolesCarbonate = None
        self.fCalculatedCO3Concentration = None
        self.fCalculatedMassCarbonate = None
        self.fCarbonateMassDifference = None
        self.fMolesDifference = None
        self.oTankSolution = None
        self.opH_Manip = None
        self.fStep = 20
        self.oPhase = oPhase

        # Load polynomial coefficients
        self.afPolynomialCoeff = [
            1.5845e-04, -0.0123, 0.4128, -7.9503, 96.7064, -774.4675,
            4.1295e+03, -1.4478e+04, 3.2032e+04, -4.0637e+04, 2.2722e+04
        ]

        # Initialize references
        self.oTankSolution = oPhase.oStore.oContainer.toStores.CROP_Tank.toPhases.TankSolution
        self.opH_Manip = oPhase.oStore.oContainer.toStores.CROP_Tank.toPhases.Aeration.toManips.substance
        self.fStep = oPhase.oStore.oContainer.fTimeStep

    def update(self):
        """
        Update function to calculate and adjust flow rates based on calcite dissolution.
        """
        if not self.oPhase.oStore.oContainer.bResetInitialMass and self.oPhase.afMass[self.oPhase.oMT.tiN2I["CaCO3"]] > 0:

            # Get current pH value
            self.fCurrentpH = self.opH_Manip.fpH

            # Get current volume of the TankSolution phase
            self.fVolume = self.oTankSolution.fVolume

            # Calculate calcium concentration in TankSolution after acidic dissolution (mg/L)
            self.fCalculatedCaConcentration = 2470 / (self.fCurrentpH ** 3)

            # Convert to corresponding number of moles
            self.fCalculatedMolesCalcium = (
                self.fCalculatedCaConcentration * 1000 * self.fVolume
            ) / (1e6 * self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I["Ca2plus"]])

            # Moles of calcium and carbonate are equal
            self.fCalculatedMolesCarbonate = self.fCalculatedMolesCalcium

            # Calculate CO3 concentration in TankSolution (mg/L)
            self.fCalculatedCO3Concentration = (
                self.fCalculatedMolesCarbonate
                * 1e6
                * self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I["CO3"]]
            ) / (1000 * self.fVolume)

            # Convert to corresponding mass (kg)
            self.fCalculatedMassCarbonate = (
                1e-6 * self.fCalculatedCO3Concentration * 1000 * self.fVolume
            )

            # Compare calculated carbonate mass with current mass
            afPartialFlowRates = np.zeros(self.oPhase.oMT.iSubstances)

            if self.oPhase.afMass[self.oPhase.oMT.tiN2I["CO3"]] >= self.fCalculatedMassCarbonate:
                # No action needed if current mass is greater or equal
                fpHManipCO3Flow = self.opH_Manip.afPartialFlows[self.oPhase.oMT.tiN2I["CO3"]]
                fCO3FlowRate = -fpHManipCO3Flow if fpHManipCO3Flow < 0 else 0
            else:
                # Calculate the mass difference
                self.fCarbonateMassDifference = self.fCalculatedMassCarbonate - self.oTankSolution.afMass[self.oPhase.oMT.tiN2I["CO3"]]
                self.fCarbonateMassDifference = max(self.fCarbonateMassDifference, 0)

                # Convert to number of moles
                self.fMolesDifference = self.fCarbonateMassDifference / self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I["CO3"]]
                self.fMolesDifference = max(self.fMolesDifference, 0)

                # Adjust flow rates
                fpHManipCO3Flow = self.opH_Manip.afPartialFlows[self.oPhase.oMT.tiN2I["CO3"]]
                fCO3FlowRate = self.fCarbonateMassDifference / self.fStep
                if fpHManipCO3Flow < 0:
                    fCO3FlowRate -= 1.3 * fpHManipCO3Flow

            fCO3FlowRateMolar = fCO3FlowRate / self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I["CO3"]]

            afPartialFlowRates[self.oPhase.oMT.tiN2I["CO3"]] = fCO3FlowRate
            afPartialFlowRates[self.oPhase.oMT.tiN2I["Ca2plus"]] = fCO3FlowRateMolar * self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I["Ca2plus"]]
            afPartialFlowRates[self.oPhase.oMT.tiN2I["CaCO3"]] = -fCO3FlowRateMolar * self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I["CaCO3"]]
        else:
            afPartialFlowRates = np.zeros(self.oPhase.oMT.iSubstances)

        # Update the parent class with adjusted flow rates
        self.update_substance_stationary(afPartialFlowRates)

        # Adjust flow rates for P2P processes
        afFlowRates = np.zeros(self.oPhase.oMT.iSubstances)
        afFlowRates[self.oPhase.oMT.tiN2I["Ca2plus"]] = afPartialFlowRates[self.oPhase.oMT.tiN2I["Ca2plus"]]
        afFlowRates[self.oPhase.oMT.tiN2I["CO3"]] = afPartialFlowRates[self.oPhase.oMT.tiN2I["CO3"]]
        self.oPhase.oStore.toProcsP2P["Calcite_to_TankSolution"].setFlowRate(afFlowRates)

    def update_substance_stationary(self, afPartialFlowRates):
        """
        Placeholder for updating substance.stationary parent class.
        Implement this method in the context of the broader simulation framework.
        """
        pass
