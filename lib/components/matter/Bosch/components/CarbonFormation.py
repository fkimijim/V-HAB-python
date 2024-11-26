import numpy as np
from scipy.interpolate import interp1d

class CarbonFormation:
    """
    Carbon Formation Reactor
    Two reactions take place simultaneously:
        H2 + CO --> C(s) + H2O (CO Hydrogenation)
        2CO --> C(s) + CO2 (Boudouard)
    Side reactions (e.g., Sabatier) are assumed not to occur.
    The Boudouard reaction reaches equilibrium, and 50% of the remaining CO is
    transformed via the CO Hydrogenation reaction.
    """

    fPressure = 100000  # Pa

    # Equilibrium percentages for CO2 in the Boudouard reaction
    mfBoudouardCO2 = np.array([0.966, 0.895, 0.8, 0.703, 0.6, 0.41, 0.21, 0.165, 0.075, 0.03])
    mfBoudouardTemperature = np.array([673.15, 753.15, 828.15, 873.15, 908.15, 973.15, 
                                        1053.15, 1073.15, 1168.15, 1273.15])  # K

    def __init__(self, sName, oPhase):
        """
        Constructor for the CarbonFormation manipulator.
        :param sName: Name of the manipulator.
        :param oPhase: Phase object.
        """
        self.sName = sName
        self.oPhase = oPhase
        self.afConversionRates = np.zeros(oPhase.oMT.iSubstances)
        
        # Initialize attributes
        self.reset_fluxes()

    def reset_fluxes(self):
        """Resets all flux-related attributes to initial values."""
        self.fTemperature = -1
        self.fMolarFluxInH2 = -1
        self.fMolarFluxInCO2 = -1
        self.fMolarFluxInCO = -1
        self.fMolarFluxOutH2 = -1
        self.fMolarFluxOutCO2 = -1
        self.fMolarFluxOutCO = -1
        self.fMolarFluxOutH2O = -1
        self.fConvertedH2 = -1
        self.fConvertedCO_1 = -1
        self.fProducedH2O = -1
        self.fProducedC_1 = -1
        self.fAvailableCO = -1
        self.fBoudouardCO2 = -1
        self.fConvertedCO_2 = -1
        self.fProducedCO2 = -1
        self.fProducedC_2 = -1
        self.fProducedC = -1
        self.fTotalMassFlowBack = 0
        self.fMassFlowOutC = 0

    def calculateConversionRate(self, afInFlowRates, aarInPartials, _):
        """
        Calculates the conversion rates based on incoming flow rates.
        :param afInFlowRates: Array of incoming flow rates [kg/s].
        :param aarInPartials: Array of incoming partial flows.
        """
        afPartialInFlows = np.sum(afInFlowRates[:, None] * aarInPartials, axis=0)
        afPartialInFlows[afPartialInFlows < 0] = 0  # Ensure non-negative flows

        afMolarMass = self.oPhase.oMT.afMolarMass
        tiN2I = self.oPhase.oMT.tiN2I

        if np.sum(afPartialInFlows) <= 0:
            self.update()
            return

        fMassFlowCO2 = afPartialInFlows[tiN2I["CO2"]]
        fMassFlowH2 = afPartialInFlows[tiN2I["H2"]]
        fMassFlowCO = afPartialInFlows[tiN2I["CO"]]

        # Convert mass flow to molar flow
        fMolarFlowCO2 = fMassFlowCO2 / afMolarMass[tiN2I["CO2"]]
        fMolarFlowH2 = fMassFlowH2 / afMolarMass[tiN2I["H2"]]
        fMolarFlowCO = fMassFlowCO / afMolarMass[tiN2I["CO"]]

        # Perform reaction calculations
        fMolarFlowOutCO2, fMolarFlowOutH2, fMolarFlowOutCO, fMolarFlowOutH2O, fMolarFlowOutC = \
            self.calculateReaction(fMolarFlowCO2, fMolarFlowH2, fMolarFlowCO)

        # Convert molar flow to mass flow
        fMassFlowOutCO2 = fMolarFlowOutCO2 * afMolarMass[tiN2I["CO2"]]
        fMassFlowOutH2 = fMolarFlowOutH2 * afMolarMass[tiN2I["H2"]]
        fMassFlowOutCO = fMolarFlowOutCO * afMolarMass[tiN2I["CO"]]
        fMassFlowOutH2O = fMolarFlowOutH2O * afMolarMass[tiN2I["H2O"]]
        self.fMassFlowOutC = fMolarFlowOutC * afMolarMass[tiN2I["C"]]

        self.fTotalMassFlowBack = fMassFlowOutCO2 + fMassFlowOutH2 + fMassFlowOutCO + fMassFlowOutH2O

        # Compute mass flow differences for the manipulator
        afMassFlowDiff = np.zeros_like(afMolarMass)
        afMassFlowDiff[tiN2I["CO2"]] = fMassFlowOutCO2 - fMassFlowCO2
        afMassFlowDiff[tiN2I["H2"]] = -(fMassFlowH2 - fMassFlowOutH2)
        afMassFlowDiff[tiN2I["CO"]] = -(fMassFlowCO - fMassFlowOutCO)
        afMassFlowDiff[tiN2I["H2O"]] = fMassFlowOutH2O
        afMassFlowDiff[tiN2I["C"]] = self.fMassFlowOutC

        self.afConversionRates = afMassFlowDiff
        self.update()

    def calculateReaction(self, fMolarFlowInCO2, fMolarFlowInH2, fMolarFlowInCO):
        """
        Performs the reaction calculations and returns molar outflows.
        """
        self.fTemperature = 823.15
        self.fMolarFluxInH2 = fMolarFlowInH2
        self.fMolarFluxInCO2 = fMolarFlowInCO2
        self.fMolarFluxInCO = fMolarFlowInCO

        self.fBoudouardCO2 = self.calculateEqBoudouardCO2()
        self.fProducedCO2 = self.fBoudouardCO2 * (fMolarFlowInCO / (1 + self.fBoudouardCO2))
        self.fConvertedCO_2 = 2 * self.fProducedCO2
        self.fAvailableCO = fMolarFlowInCO - self.fConvertedCO_2
        self.fConvertedH2 = 0.5 * self.fAvailableCO
        self.fConvertedCO_1 = 0.5 * self.fAvailableCO
        self.fProducedH2O = self.fConvertedH2
        self.fProducedC_1 = self.fConvertedH2
        self.fProducedC_2 = self.fProducedCO2
        self.fProducedC = self.fProducedC_1 + self.fProducedC_2

        fMolarFlowOutH2 = fMolarFlowInH2 - self.fConvertedH2
        fMolarFlowOutCO2 = fMolarFlowInCO2 + self.fProducedCO2
        fMolarFlowOutCO = fMolarFlowInCO - self.fConvertedCO_1 - self.fConvertedCO_2
        fMolarFlowOutH2O = self.fProducedH2O

        return fMolarFlowOutCO2, fMolarFlowOutH2, fMolarFlowOutCO, fMolarFlowOutH2O, self.fProducedC

    def calculateEqBoudouardCO2(self):
        """
        Interpolates to calculate the equilibrium CO2 percentage for the Boudouard reaction.
        """
        interp_func = interp1d(self.mfBoudouardTemperature, self.mfBoudouardCO2, kind='linear', fill_value="extrapolate")
        return interp_func(self.fTemperature)

    def update(self):
        """
        Updates the manipulator with the calculated conversion rates.
        """
        # Update the parent class (if applicable) with the conversion rates
        pass
