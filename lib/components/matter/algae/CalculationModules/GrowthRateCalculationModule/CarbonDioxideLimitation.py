class CarbonDioxideLimitation:
    """
    CarbonDioxideLimitation calculates the relative growth rate depending
    on the current CO2 concentration in the medium. High CO2 concentrations 
    can limit the growth of Chlorella vulgaris.
    """
    def __init__(self, oGrowthPhase):
        """
        Initializes the CarbonDioxideLimitation class.
        :param oGrowthPhase: Growth phase object
        """
        self.oGrowthPhase = oGrowthPhase

        # Vectors to define CO2 relative growth behavior
        self.mfPressures = [65000, 100000]  # Pressures in Pa
        self.mrRelativeGrowth = [1, 0.14]  # Ratios between 0 and 1

        # Model parameters
        self.fMaximumPartialPressureFullGrowth = self.mfPressures[0]  # Pa
        self.f100kPaGrowthFactor = self.mrRelativeGrowth[1]  # Factor between 0 and 1

        # Current phase conditions
        self.fEquivalentPartialPressure = 0  # Pa

        # Output
        self.rCarbonDioxideRelativeGrowth = 1  # Default growth factor

    def UpdateCarbonDioxideRelativeGrowth(self):
        """
        Updates and calculates the relative growth rate based on CO2 concentration.
        :return: rCarbonDioxideRelativeGrowth (unitless factor between 0 and 1)
        """
        # Get the equivalent partial pressure from the growth phase
        self.fEquivalentPartialPressure = self.oGrowthPhase.toProcsEXME.CO2_from_Air.oFlow.fEquivalentPartialPressure  # Pa

        # If below the maximum pressure for full growth, growth rate is 1
        if self.fEquivalentPartialPressure < self.fMaximumPartialPressureFullGrowth:
            self.rCarbonDioxideRelativeGrowth = 1
        else:
            # Calculate growth factor for pressures above the maximum
            self.rCarbonDioxideRelativeGrowth = (
                ((1 - (self.f100kPaGrowthFactor - (100000 / self.fMaximumPartialPressureFullGrowth))
                  / (1 - (100000 / self.fMaximumPartialPressureFullGrowth)))
                 / self.fMaximumPartialPressureFullGrowth)
                * self.fEquivalentPartialPressure
                + ((self.f100kPaGrowthFactor - (100000 / self.fMaximumPartialPressureFullGrowth))
                   / (1 - (100000 / self.fMaximumPartialPressureFullGrowth)))
            )

            # Ensure the growth factor does not fall below 0
            if self.rCarbonDioxideRelativeGrowth < 0:
                self.rCarbonDioxideRelativeGrowth = 0

        # Return the calculated growth factor
        return self.rCarbonDioxideRelativeGrowth
