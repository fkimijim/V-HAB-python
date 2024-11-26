import math

class RWGSr:
    """
    RWGSr Reverse Water Gas Shift Reactor
    
    - CO2 + H2 --> H2O + CO
    - Temperature > 828°C to ensure no side reactions occur.
    - Reaction runs spontaneously and almost reaches equilibrium.
    """

    # Constants
    fGasConstant = 8.3145  # J/(K*mol)
    fAlpha = 0.56         # [-]
    fBeta = 0.37          # [-]
    fPreExpFactor = 28125.68944  # [-]
    fActivationEnergy = 75600    # J/mol
    fPressure = 100000           # Pa

    def __init__(self, sName, oPhase):
        """
        Initializes the RWGSr manipulator.

        :param sName: Name of the manipulator.
        :param oPhase: Associated phase object.
        """
        self.sName = sName
        self.oPhase = oPhase
        self.afConversionRates = [0] * self.oPhase.oMT.iSubstances

        # Initialize properties
        self.fTemperature = -1
        self.fEquilibriumConstant = -1
        self.fVelocityConstant = -1
        self.fReactionRate = -1
        self.fMolarFluxInH2 = -1
        self.fMolarFluxInCO2 = -1
        self.fTotalMolarFlux = -1
        self.fVolumeFlowIn = -1
        self.fMolarFluxOutH2 = -1
        self.fMolarFluxOutCO2 = -1
        self.fMolarFluxOutCO = -1
        self.fMolarFluxOutH2O = -1
        self.fConversionCO2 = -1
        self.fPartialPressureInH2 = -1
        self.fPartialPressureInCO2 = -1
        self.fTotalMassFlowOut = 0

    def calculateConversionRate(self, afInFlowRates, aarInPartials, *_):
        """
        Calculates conversion rates based on inflow rates.

        :param afInFlowRates: Array of incoming flow rates [kg/s].
        :param aarInPartials: Array of incoming partial flows.
        """
        # Compute partial inflows for each substance
        afPartialInFlows = [
            sum(afInFlowRates[i] * aarInPartials[i][j] for i in range(len(afInFlowRates)))
            for j in range(len(aarInPartials[0]))
        ]

        # Ignore negative inflows
        afPartialInFlows = [max(0, flow) for flow in afPartialInFlows]

        # Abbreviate variable names for readability
        afMolarMass = self.oPhase.oMT.afMolarMass
        tiN2I = self.oPhase.oMT.tiN2I

        self.afConversionRates = [0] * self.oPhase.oMT.iSubstances

        if sum(afPartialInFlows) <= 0:
            self.update()
            return

        # Convert mass flow to molar flow
        fMolarFlowCO2 = afPartialInFlows[tiN2I['CO2']] / afMolarMass[tiN2I['CO2']]
        fMolarFlowH2 = afPartialInFlows[tiN2I['H2']] / afMolarMass[tiN2I['H2']]

        # Perform reaction calculations
        fMolarFlowOutCO2, fMolarFlowOutH2, fMolarFlowOutCO, fMolarFlowOutH2O = self.calculateReaction(
            fMolarFlowCO2, fMolarFlowH2
        )

        # Convert molar flows to mass flows
        fMassFlowOutCO2 = fMolarFlowOutCO2 * afMolarMass[tiN2I['CO2']]
        fMassFlowOutH2 = fMolarFlowOutH2 * afMolarMass[tiN2I['H2']]
        fMassFlowOutCO = fMolarFlowOutCO * afMolarMass[tiN2I['CO']]
        fMassFlowOutH2O = fMolarFlowOutH2O * afMolarMass[tiN2I['H2O']]

        self.fTotalMassFlowOut = fMassFlowOutCO2 + fMassFlowOutH2 + fMassFlowOutCO + fMassFlowOutH2O

        # Compute mass flow differences
        afMassFlowDiff = [0] * self.oPhase.oMT.iSubstances
        afMassFlowDiff[tiN2I['CO2']] = -1 * (afPartialInFlows[tiN2I['CO2']] - fMassFlowOutCO2)
        afMassFlowDiff[tiN2I['H2']] = -1 * (afPartialInFlows[tiN2I['H2']] - fMassFlowOutH2)
        afMassFlowDiff[tiN2I['CO']] = fMassFlowOutCO
        afMassFlowDiff[tiN2I['H2O']] = fMassFlowOutH2O

        # Update conversion rates
        self.afConversionRates = afMassFlowDiff
        self.update()

    def calculateReaction(self, fMolarFlowInCO2, fMolarFlowInH2):
        """
        Calculates the reaction equilibrium and outputs.

        :param fMolarFlowInCO2: Incoming molar flow of CO2 [mol/s].
        :param fMolarFlowInH2: Incoming molar flow of H2 [mol/s].
        :return: Molar flows out for CO2, H2, CO, and H2O [mol/s].
        """
        # Set incoming flows
        self.fMolarFluxInH2 = fMolarFlowInH2
        self.fMolarFluxInCO2 = fMolarFlowInCO2

        # Set fixed temperature
        self.fTemperature = 1102  # Kelvin

        # Calculate equilibrium constant
        self.fEquilibriumConstant = self.calculateEqConstant()

        # Total molar flux
        self.fTotalMolarFlux = self.fMolarFluxInH2 + self.fMolarFluxInCO2

        # Calculate molar fluxes
        fMolarFlowOutCO = self.calculateMolFluxOut1()
        fMolarFlowOutH2O = fMolarFlowOutCO
        fMolarFlowOutCO2 = self.calculateMolFluxOut2()
        fMolarFlowOutH2 = fMolarFlowOutCO2

        return fMolarFlowOutCO2, fMolarFlowOutH2, fMolarFlowOutCO, fMolarFlowOutH2O

    def calculateEqConstant(self):
        """Calculate the equilibrium constant."""
        return 1 / math.exp((4577.8 / self.fTemperature) - 4.33)

    def calculateMolFluxOut1(self):
        """Calculate molar flux out for products (CO, H2O)."""
        return self.fTotalMolarFlux / (2 * (1 / (self.fEquilibriumConstant**0.5) + 1))

    def calculateMolFluxOut2(self):
        """Calculate molar flux out for reactants (CO2, H2)."""
        return self.fTotalMolarFlux / (2 * (1 + self.fEquilibriumConstant**0.5))

    def update(self):
        """Update conversion rates."""
        # Here, integrate with system update logic.
        pass
