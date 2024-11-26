import numpy as np

class FlowManip(matter.manips.substance.Flow, components.matter.pH_Module.BaseManip):
    """
    FlowManip: A pH manipulator for flow phases.
    
    This manipulator calculates the pH value in an aqueous solution and 
    converts participating substances accordingly. Adjust `miComplex` for 
    new substances in the matter table.
    """

    def __init__(self, sName, oPhase):
        super().__init__(sName, oPhase)
        components.matter.pH_Module.BaseManip.__init__(self, oPhase)
        
        if not oPhase.bFlow:
            raise ValueError("FlowManip only works with flow phases.")
        
        self.fpH_Inlet = None

    def calculateConversionRate(self, afInFlowRates, aarInPartials, _):
        """
        Calculate the conversion rate based on input flow rates and partials.
        """
        # Calculate inflow rates for all substances
        afPartialInFlows = np.sum((afInFlowRates[:, np.newaxis] * aarInPartials), axis=0)
        afPartialInFlows[afPartialInFlows < 0] = 0  # Ensure non-negative inflow rates

        if np.any(afPartialInFlows[self.abDissociation]) and afPartialInFlows[self.oMT.tiN2I.H2O] > 1e-12:
            afFlows = afPartialInFlows[self.abRelevantSubstances]
            arPartials = afFlows / np.sum(afFlows)

            # Skip calculation if changes are below the threshold
            if np.all(np.abs((self.arLastPartials - arPartials) / (self.arLastPartials + 1e-18)) < self.rMaxChange):
                return

            self.arLastPartials = arPartials

            # Volumetric flow rate in liters per second
            fVolumetricFlowRate = (np.sum(afPartialInFlows) / self.oPhase.fDensity) * 1000

            # Concentrations in mol/L
            afInitialConcentrations = (afPartialInFlows / self.oMT.afMolarMass) / fVolumetricFlowRate

            # Calculate inlet pH value
            self.fpH_Inlet = self.calculate_pHValue(afInitialConcentrations)

            # Initial mass sum in kg/L
            fInitialMassSum = np.sum(afPartialInFlows[self.abRelevantSubstances]) / fVolumetricFlowRate

            if fInitialMassSum == 0:
                afConcentrationDifference = np.zeros_like(afInitialConcentrations)
            else:
                # Calculate new concentrations
                afConcentrations = self.calculateNewConcentrations(
                    afInitialConcentrations, fInitialMassSum, self.fpH_Inlet
                )

                # Calculate the difference in concentrations
                afConcentrationDifference = afConcentrations - afInitialConcentrations

            # Set small concentration changes to zero
            afConcentrationDifference[np.abs(afConcentrationDifference) < 1e-16] = 0

            # Calculate conversion rates in kg/s
            self.afConversionRates = afConcentrationDifference * fVolumetricFlowRate * self.oMT.afMolarMass

            # Final concentrations in mol/L
            afFinalConcentrations = (
                (afPartialInFlows + self.afConversionRates) / self.oMT.afMolarMass
            ) / fVolumetricFlowRate

            # Calculate outlet pH value
            self.fpH = self.calculate_pHValue(afFinalConcentrations)
        else:
            # No dissociation or insufficient water, set conversion rates to zero
            self.afConversionRates = np.zeros(self.oMT.iSubstances)

        self.update()

    def update(self):
        """
        Update the manipulator with the current conversion rates.
        """
        super().update(self.afConversionRates)
