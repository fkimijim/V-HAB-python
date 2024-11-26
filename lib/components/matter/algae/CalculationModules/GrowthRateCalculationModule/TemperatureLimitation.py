import numpy as np

class TemperatureLimitation:
    """
    TemperatureLimitation calculates the relative growth rate based on the medium's temperature.
    The class also handles determining if the culture is dead due to exceeding maximum temperature.
    """

    def __init__(self, oGrowthPhase):
        """
        Initialize the TemperatureLimitation object.

        :param oGrowthPhase: The growth medium phase object.
        """
        self.oGrowthPhase = oGrowthPhase
        self.fMinimumTemperature = 274.0  # Minimum temperature [K]
        self.fMaximumTemperature = 313.0  # Maximum temperature [K]
        self.bDead = False  # Initially, the culture is not dead
        self.rTemperatureRelativeGrowth = 0.0  # Growth factor (0 to 1)
        self.fCurrentTemperature = 0.0  # Current temperature [K]

        # Define temperature and growth rate data points
        self.mfTemp = np.array([self.fMinimumTemperature, 284, 289, 294, 298, 302, 309, 313])  # [K]
        self.mrGrowthrate = 2.0833 * np.array([0, 0.25, 0.325, 0.4, 0.44, 0.48, 0.45, 0.35])  # [-]

        # Fit a 4th-order polynomial to the temperature-growth data
        self.mfFactors = np.polyfit(self.mfTemp, self.mrGrowthrate, 4)  # Polynomial coefficients

    def UpdateTemperatureRelativeGrowth(self):
        """
        Updates the relative growth factor and checks if the culture is dead due to temperature.

        :return: rTemperatureRelativeGrowth (growth factor, 0 to 1),
                 bDead (boolean, True if the culture is dead)
        """
        self.fCurrentTemperature = self.oGrowthPhase.fTemperature  # Get current temperature [K]

        # Calculate growth factor using the polynomial
        self.rTemperatureRelativeGrowth = (
            self.mfFactors[0] * self.fCurrentTemperature**4 +
            self.mfFactors[1] * self.fCurrentTemperature**3 +
            self.mfFactors[2] * self.fCurrentTemperature**2 +
            self.mfFactors[3] * self.fCurrentTemperature +
            self.mfFactors[4]
        )

        # Ensure growth factor is within valid bounds
        if self.rTemperatureRelativeGrowth > 1:
            self.rTemperatureRelativeGrowth = 1
        elif self.rTemperatureRelativeGrowth < 0:
            self.rTemperatureRelativeGrowth = 0

        # Check if the temperature exceeds the maximum allowed
        if self.fCurrentTemperature > self.fMaximumTemperature:
            self.rTemperatureRelativeGrowth = 0  # No growth above max temperature
            self.bDead = True  # Culture is dead

        return self.rTemperatureRelativeGrowth, self.bDead
