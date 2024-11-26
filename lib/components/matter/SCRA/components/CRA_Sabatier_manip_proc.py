class CRA_Sabatier_manip_proc:
    """
    A phase manipulator to simulate the Sabatier reaction.
    This calculates the conversion of CO2 and H2 into H2O and CH4
    according to the chemical reaction and specified efficiency.
    """

    def __init__(self, sName, oPhase, fEfficiency=1):
        self.sName = sName
        self.oPhase = oPhase
        self.fEfficiency = fEfficiency  # Conversion efficiency
        
        self.fH2OProduction = 0
        self.fCH4Production = 0
        self.fH2Reduction = 0
        self.fCO2Reduction = 0
        
        self.mPartialConversionFlowRates = [0] * self.oPhase.oMT.iSubstances
        self.fHeatFlowProduced = 0

    def calculateConversionRate(self, afInFlowRates, aarInPartials, *args):
        """
        Calculate the conversion rates of CO2 and H2 into H2O and CH4
        based on the Sabatier reaction.
        """
        # Initialize the flow rates for substances
        self.mPartialConversionFlowRates = [0] * self.oPhase.oMT.iSubstances

        if not (afInFlowRates and any(sum(aarInPartials))):
            self.reset_production()
            self.update()
            return

        afPartialInFlowRates = [sum(a * b for a, b in zip(afInFlowRates, col)) for col in zip(*aarInPartials)]
        tiN2I = self.oPhase.oMT.tiN2I  # Substance identifiers

        fMolMassCO2 = self.oPhase.oMT.afMolarMass[tiN2I["CO2"]]  # kg/mol
        fMolMassH2 = self.oPhase.oMT.afMolarMass[tiN2I["H2"]]  # kg/mol

        fMolCO2 = afPartialInFlowRates[tiN2I["CO2"]] / fMolMassCO2 if self.oPhase.afMass[tiN2I["CO2"]] > 0 else 0
        fMolH2 = afPartialInFlowRates[tiN2I["H2"]] / fMolMassH2 if self.oPhase.afMass[tiN2I["H2"]] > 0 else 0

        if fMolCO2 == 0 or fMolH2 == 0:
            self.reset_production()
            self.update()
            return

        # Determine the molar amounts used in the reaction
        if fMolH2 > 4 * fMolCO2:
            fMolH2used = 4 * fMolCO2 * self.fEfficiency
            fMolCO2used = fMolCO2 * self.fEfficiency
        elif fMolH2 < 4 * fMolCO2:
            fMolH2used = fMolH2 * self.fEfficiency
            fMolCO2used = 0.25 * fMolH2 * self.fEfficiency
        else:
            fMolH2used = fMolH2 * self.fEfficiency
            fMolCO2used = fMolCO2 * self.fEfficiency

        # Reaction enthalpy (J/mol)
        fReactionEnthalpy = abs(
            1.8 * (-16.4 * self.oPhase.fTemperature + (0.00557 * self.oPhase.fTemperature**2) -
                   (112000 / self.oPhase.fTemperature) - 34633) * 4.184
        )

        self.fHeatFlowProduced = fReactionEnthalpy * fMolCO2used  # J/s

        self.fCO2Reduction = fMolCO2used * fMolMassCO2  # kg/s
        self.fH2Reduction = fMolH2used * fMolMassH2  # kg/s

        fMolMassWater = self.oPhase.oMT.afMolarMass[tiN2I["H2O"]]  # kg/mol
        fMolMassMethane = self.oPhase.oMT.afMolarMass[tiN2I["CH4"]]  # kg/mol

        rCH4Ratio = fMolMassMethane / (2 * fMolMassWater + fMolMassMethane)
        rH2ORatio = 1 - rCH4Ratio

        fTotalMassFlowUsed = self.fCO2Reduction + self.fH2Reduction  # kg/s

        self.fCH4Production = fTotalMassFlowUsed * rCH4Ratio  # kg/s
        self.fH2OProduction = fTotalMassFlowUsed * rH2ORatio  # kg/s

        # Update flow rates for substances
        self.mPartialConversionFlowRates[tiN2I["CO2"]] = -self.fCO2Reduction
        self.mPartialConversionFlowRates[tiN2I["H2"]] = -self.fH2Reduction
        self.mPartialConversionFlowRates[tiN2I["H2O"]] = self.fH2OProduction
        self.mPartialConversionFlowRates[tiN2I["CH4"]] = self.fCH4Production

        # Correct small numerical mass balance discrepancies
        total_mass_error = sum(self.mPartialConversionFlowRates) * 0.5
        self.mPartialConversionFlowRates[tiN2I["CH4"]] -= total_mass_error
        self.mPartialConversionFlowRates[tiN2I["H2O"]] -= total_mass_error

        self.update()

    def reset_production(self):
        """
        Reset all production rates to zero.
        """
        self.fH2OProduction = 0
        self.fCH4Production = 0
        self.fH2Reduction = 0
        self.fCO2Reduction = 0
        self.fHeatFlowProduced = 0

    def update(self):
        """
        Update the manipulator with the current flow rates.
        """
        # Simulate the manipulator update process
        # This method needs to interact with the simulation's update logic.
        pass
