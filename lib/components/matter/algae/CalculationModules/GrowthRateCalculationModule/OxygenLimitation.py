class OxygenLimitation:
    """
    OxygenLimitation calculates the relative growth rate depending on the current O2 concentration
    in the medium. It models the effect of oxygen partial pressure on growth rates based on the
    behavior defined during initialization.
    """

    def __init__(self, oGrowthPhase):
        """
        Initializes the OxygenLimitation class.
        :param oGrowthPhase: The growth phase object containing information about the oxygen flow.
        """
        self.oGrowthPhase = oGrowthPhase

        # Behavior definition based on Watts Pirt, 1979
        self.mfPressures = [80000, 100000]  # [Pa] Partial pressures
        self.mrRelativeGrowth = [1, 0.5]  # Growth factor between 0 and 1

        # Model parameters
        self.fMaximumPartialPressureFullGrowth = self.mfPressures[0]  # [Pa]
        self.f100kPaGrowthFactor = self.mrRelativeGrowth[1]  # Factor between 0 and 1

        # Current phase conditions
        self.fEquivalentPartialPressure = 0  # [Pa]

        # Output
        self.rOxygenRelativeGrowth = 1  # Growth factor between 0 and 1

    def UpdateOxygenRelativeGrowth(self):
        """
        Updates the relative growth rate based on the equivalent partial pressure of oxygen.
        :return: rOxygenRelativeGrowth - The relative growth factor (0 to 1).
        """
        # Get equivalent partial pressure (in equilibrium with surrounding atmosphere)
        self.fEquivalentPartialPressure = (
            self.oGrowthPhase.toProcsEXME.O2_to_Air.oFlow.fEquivalentPartialPressure
        )

        if self.fEquivalentPartialPressure < self.fMaximumPartialPressureFullGrowth:
            # Below the inhibition threshold, growth factor is 1
            self.rOxygenRelativeGrowth = 1
        else:
            # Above the inhibition threshold, calculate growth factor
            slope = (1 - (self.f100kPaGrowthFactor - (100000 / self.fMaximumPartialPressureFullGrowth))
                     / (1 - (100000 / self.fMaximumPartialPressureFullGrowth))) \
                     / self.fMaximumPartialPressureFullGrowth

            intercept = (self.f100kPaGrowthFactor - (100000 / self.fMaximumPartialPressureFullGrowth)) \
                        / (1 - (100000 / self.fMaximumPartialPressureFullGrowth))

            self.rOxygenRelativeGrowth = slope * self.fEquivalentPartialPressure + intercept

            # Ensure growth factor is not less than 0
            if self.rOxygenRelativeGrowth < 0:
                self.rOxygenRelativeGrowth = 0

        return self.rOxygenRelativeGrowth
