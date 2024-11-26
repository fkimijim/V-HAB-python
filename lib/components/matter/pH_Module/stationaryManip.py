class StationaryManip(matter.manips.substance.Stationary, components.matter.pH_Module.BaseManip):
    """
    StationaryManip: A pH manipulator for stationary phases.

    This manipulator calculates the pH value in an aqueous solution and 
    adjusts participating substances correspondingly. Adjust `miComplex` 
    for new substances in the matter table.
    """

    def __init__(self, sName, oPhase, fConversionTime=20):
        """
        Initialize the StationaryManip instance.

        Args:
            sName (str): Name of the manipulator.
            oPhase: Phase object associated with the manipulator.
            fConversionTime (float): Time in seconds for pH manipulator to reach the new value.
        """
        super().__init__(sName, oPhase)
        components.matter.pH_Module.BaseManip.__init__(self, oPhase)
        self.fConversionTime = fConversionTime

    def update(self):
        """
        Update the manipulator with the current conversion rates.
        """
        if any(self.oPhase.arPartialMass[self.abDissociation]) and self.oPhase.afMass[self.oMT.tiN2I.H2O] > 1e-12:
            arPartials = self.oPhase.arPartialMass[self.abRelevantSubstances]

            # Skip update if partial changes are below threshold
            if all(abs((self.arLastPartials - arPartials) / (arPartials + 1e-8)) < self.rMaxChange):
                return

            self.arLastPartials = arPartials

            # Calculate volume in liters
            fVolume = (self.oPhase.fMass / self.oPhase.fDensity) * 1000

            # Calculate initial concentrations in mol/L
            afInitialConcentrations = (self.oPhase.afMass / self.oMT.afMolarMass) / fVolume

            # Calculate pH value
            self.fpH = self.calculate_pHValue(afInitialConcentrations)
            if float("inf") == self.fpH:
                self.fpH = 7

            # Initial mass sum in kg/L
            fInitialMassSum = sum(self.oPhase.afMass[self.abRelevantSubstances]) / fVolume

            # Calculate new concentrations
            afConcentrations = self.calculateNewConcentrations(
                afInitialConcentrations, fInitialMassSum, self.fpH
            )

            # Calculate the difference in concentrations
            afConcentrationDifference = np.zeros(self.oMT.iSubstances)
            afConcentrationDifference[self.abRelevantSubstances] = (
                afConcentrations[self.abRelevantSubstances] - afInitialConcentrations[self.abRelevantSubstances]
            )

            # Set very small concentration changes to zero
            afConcentrationDifference[np.abs(afConcentrationDifference) < 1e-16] = 0

            # Calculate conversion rates in kg/s (assumes 20s conversion time)
            self.afConversionRates = (
                afConcentrationDifference * fVolume * self.oMT.afMolarMass / self.fConversionTime
            )
        else:
            # No dissociation or insufficient water, set conversion rates to zero
            self.afConversionRates = np.zeros(self.oMT.iSubstances)

        # Call parent class update with the calculated conversion rates
        super().update(self.afConversionRates)
