import numpy as np

class PHLimitation:
    """
    PHLimitation calculates the pH growth factor as a function of temperature.
    The growth factor is determined by how the current pH falls within
    temperature-dependent growth boundaries. 
    """

    def __init__(self, oGrowthPhase):
        """
        Initializes the PHLimitation object.

        :param oGrowthPhase: The growth medium phase
        """
        self.oPhase = oGrowthPhase
        self.fCurrentTemperature = 0.0  # Current temperature [K]

        # pH behavior definition (temperature-dependent), data from Mayo, 1997
        self.mfTemp = [283.15, 293.15, 303.15, 313.15]  # Temperature vector [K]

        # Polynomial fit for pH boundaries
        self.mfLowOpt = [4.75, 4.25, 3.65, 4.9]
        self.mfHighOpt = [8.6, 9.2, 10, 9]
        self.mfLowZero = [2.6, 2.2, 1.7, 2.9]
        self.mfHighZero = [10.4, 11, 11.8, 11]

        self.mfLowOptPoly = self._polyfit(self.mfTemp, self.mfLowOpt, 3)
        self.mfHighOptPoly = self._polyfit(self.mfTemp, self.mfHighOpt, 3)
        self.mfLowZeroPoly = self._polyfit(self.mfTemp, self.mfLowZero, 3)
        self.mfHighZeroPoly = self._polyfit(self.mfTemp, self.mfHighZero, 3)

        # Calculated values
        self.fPH = 0.0  # Current pH
        self.fMinPH = 0.0  # Absolute minimum pH for growth
        self.fMinPHFullGrowth = 0.0  # Minimum pH for full growth
        self.fMaxPHFullGrowth = 0.0  # Maximum pH for full growth
        self.fMaxPH = 0.0  # Absolute maximum pH for growth
        self.rPHGrowthFactor = 0.0  # Relative growth factor

    def _polyfit(self, x, y, degree):
        """
        Fits a polynomial of given degree to the provided x and y data.

        :param x: Independent variable
        :param y: Dependent variable
        :param degree: Degree of the polynomial
        :return: Coefficients of the polynomial
        """
        return list(np.polyfit(x, y, degree))

    def _evaluate_poly(self, poly, x):
        """
        Evaluates a polynomial at a given value.

        :param poly: Polynomial coefficients
        :param x: Value at which to evaluate the polynomial
        :return: Evaluated result
        """
        return sum(c * (x ** i) for i, c in enumerate(reversed(poly)))

    def UpdatePHRelativeGrowth(self):
        """
        Updates the relative growth rate based on the current pH and temperature.

        :return: The updated pH relative growth factor (unitless)
        """
        # Calculate current pH
        fH2OVolume = (
            1000
            * self.oPhase.afMass[self.oPhase.oMT.tiN2I["H2O"]]
            / self.oPhase.oMT.ttxMatter["H2O"]["fStandardDensity"]
        )  # [L]
        fHPlusMoles = (
            self.oPhase.afMass[self.oPhase.oMT.tiN2I["Hplus"]]
            / self.oPhase.oMT.afMolarMass[self.oPhase.oMT.tiN2I["Hplus"]]
        )  # [mol]
        fHPlusConcentration = fHPlusMoles / fH2OVolume  # [mol/m3]
        self.fPH = -np.log10(fHPlusConcentration)  # pH

        # Get current temperature
        self.fCurrentTemperature = self.oPhase.fTemperature  # [K]

        # Calculate growth boundaries based on temperature
        self.fMinPH = self._evaluate_poly(self.mfLowZeroPoly, self.fCurrentTemperature)
        self.fMaxPH = self._evaluate_poly(self.mfHighZeroPoly, self.fCurrentTemperature)
        self.fMinPHFullGrowth = self._evaluate_poly(
            self.mfLowOptPoly, self.fCurrentTemperature
        )
        self.fMaxPHFullGrowth = self._evaluate_poly(
            self.mfHighOptPoly, self.fCurrentTemperature
        )

        # Calculate pH Growth Factor
        if self.fPH <= self.fMinPHFullGrowth:
            if self.fPH <= self.fMinPH:
                self.rPHGrowthFactor = 0  # No growth
            else:
                self.rPHGrowthFactor = (self.fPH - self.fMinPH) / (
                    self.fMinPHFullGrowth - self.fMinPH
                )
        elif self.fPH <= self.fMaxPHFullGrowth:
            self.rPHGrowthFactor = 1  # Full growth
        elif self.fPH <= self.fMaxPH:
            self.rPHGrowthFactor = (self.fMaxPH - self.fPH) / (
                self.fMaxPH - self.fMaxPHFullGrowth
            )
        else:
            self.rPHGrowthFactor = 0  # No growth

        return self.rPHGrowthFactor
