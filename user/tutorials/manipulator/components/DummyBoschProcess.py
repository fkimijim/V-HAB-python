class DummyBoschProcess(matter.manips.substance.stationary):
    """
    DummyBoschProcess - A dummy model of the Bosch Process
    This manipulator converts all of the CO2 in the connected phase to
    the corresponding amount of pure carbon and oxygen.
    """

    def __init__(self, sName, oPhase, rMaximumConversion=0.9):
        """
        Initialize the DummyBoschProcess.

        Args:
            sName (str): The name of the manipulator.
            oPhase (object): The phase to which this manipulator is attached.
            rMaximumConversion (float): Maximum ratio of CO2 that can be converted to O2 and C.
        """
        super().__init__(sName, oPhase)
        self.rMaximumConversion = rMaximumConversion

    def update(self):
        """
        Update method for the manipulator.
        Called automatically in the post-tick phase whenever the phase updates.
        """
        # Get the current mass flows entering the phase
        afMassFlows = self.getTotalFlowRates()

        # Abbreviating some variables for readability
        afMolMass = self.oPhase.oMT.afMolarMass
        tiN2I = self.oPhase.oMT.tiN2I

        # Calculate the total CO2 mass flow entering the phase and its converted fraction
        fMassFlowCO2 = self.rMaximumConversion * afMassFlows[tiN2I["CO2"]]

        # Stoichiometric conversion of CO2 -> C + O2
        fMassC = (fMassFlowCO2 / afMolMass[tiN2I["CO2"]]) * afMolMass[tiN2I["C"]]
        fMassO2 = (fMassFlowCO2 / afMolMass[tiN2I["CO2"]]) * afMolMass[tiN2I["O2"]]

        # Initialize a zero vector for the partial flows
        afPartialFlows = [0] * self.oPhase.oMT.iSubstances

        # Set the specific mass flow rates for the substances
        afPartialFlows[tiN2I["CO2"]] = -1 * fMassFlowCO2
        afPartialFlows[tiN2I["C"]] = fMassC
        afPartialFlows[tiN2I["O2"]] = fMassO2

        # Call the parent update method with the computed partial flows
        super().update(afPartialFlows)
