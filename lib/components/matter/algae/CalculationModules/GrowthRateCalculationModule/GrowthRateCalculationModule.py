import numpy as np

class GrowthRateCalculationModule:
    """
    GrowthRateCalculationModule determines the optimum biomass concentration increase rate
    depending on the current biomass concentration in the medium. It calculates growth rates
    influenced by factors such as temperature, pH, light, oxygen, and carbon dioxide.
    """

    def __init__(self, oSystem):
        """
        Initializes the GrowthRateCalculationModule class.
        :param oSystem: System object that initiates and manages growth calculations.
        """
        # System and general properties
        self.oSystem = oSystem
        self.fTime = 0  # [s] Current time from system timer

        # Theoretical growth parameters
        self.fLagTime = 0  # [s]
        self.fMaxSpecificGrowthRate = 3.89 * 10 ** -4  # [1/s]
        self.fMaximumBiomassConcentration = 18.15  # [kg/m^3]
        self.bDead = False  # True if culture is dead (no growth possible)

        self.fMaximumGrowthBiomassConcentration = 0.368 * self.fMaximumBiomassConcentration

        # Initialize growth variables
        self.fLastExecute = 0  # [s]
        self.fBiomassConcentration = 0  # [kg/m^3]

        self.fInitialBiomassConcentration = (
            self.fMaximumBiomassConcentration
            * np.exp(
                -np.exp(
                    ((self.fMaxSpecificGrowthRate * np.exp(1)) / self.fMaximumBiomassConcentration)
                    * (self.fLagTime - 0)
                    + 1
                )
            )
        )  # [kg/m^3]

        # Growth rate calculation model
        self.sCalculationModel = "multiplicative"  # 'multiplicative' or 'minimum'

        # Influence factors
        self.rTemperatureRelativeGrowth = 1
        self.rPhRelativeGrowth = 1
        self.rO2RelativeGrowth = 1
        self.rCO2RelativeGrowth = 1
        self.rPARRelativeGrowth = 1

        # Growth rate results
        self.fAchievableCurrentBiomassGrowthRate = 0  # [kg/s]

    def update(self):
        """
        Updates the growth rate calculations.
        """
        self.CalculateTheoreticalGrowthRate()
        self.CalculateInfluenceParameters()
        self.CalculateAchievableGrowthRate()

    def CalculateTheoreticalGrowthRate(self):
        """
        Calculates the theoretical growth rate based on cell density and growth phases.
        """
        if not self.bDead:
            self.fTime = self.oSystem.oTimer.fTime

            # Get current biomass and medium volume
            self.fCurrentBiomass = self.oSystem.toStores.GrowthChamber.toPhases.GrowthMedium.afMass[
                self.oSystem.oMT.tiN2I.Chlorella
            ]
            self.fMediumVolume = (
                self.oSystem.toStores.GrowthChamber.toPhases.GrowthMedium.afMass[
                    self.oSystem.oMT.tiN2I.H2O
                ]
                / self.oSystem.fCurrentGrowthMediumDensity
            )
            self.fBiomassConcentration = self.fCurrentBiomass / self.fMediumVolume

            if self.fTime < self.fLagTime:
                # Growth rate during lag phase
                self.fTheoreticalCurrentBiomassConcentrationIncrease = (
                    self.fMaxSpecificGrowthRate
                    * np.exp(
                        -np.exp(
                            (
                                (self.fMaxSpecificGrowthRate * np.exp(1))
                                / self.fMaximumBiomassConcentration
                            )
                            * (self.fLagTime - self.fTime)
                            + 1
                        )
                    )
                )
            else:
                # Growth rate after lag phase
                self.fTheoreticalCurrentBiomassConcentrationIncrease = (
                    self.fMaxSpecificGrowthRate
                    * np.exp(
                        -np.exp(
                            (
                                (self.fMaxSpecificGrowthRate * np.exp(1))
                                / self.fMaximumBiomassConcentration
                            )
                            * (
                                self.fLagTime
                                - (
                                    self.fLagTime
                                    - (
                                        self.fMaximumBiomassConcentration
                                        * (
                                            np.log(
                                                -np.log(
                                                    self.fBiomassConcentration
                                                    / self.fMaximumBiomassConcentration
                                                )
                                            )
                                            - 1
                                        )
                                        / (self.fMaxSpecificGrowthRate * np.exp(1))
                                    )
                                )
                            )
                            + 1
                        )
                    )
                )

        else:
            self.fTheoreticalCurrentBiomassConcentrationIncrease = 0

        # Convert density growth to mass growth
        self.fTheoreticalCurrentBiomassGrowthRate = (
            self.fTheoreticalCurrentBiomassConcentrationIncrease * self.fMediumVolume
        )  # [kg/s]

    def CalculateInfluenceParameters(self):
        """
        Updates the influence of environmental factors on growth rates.
        """
        self.rTemperatureRelativeGrowth, self.bDead = (
            self.oTemperatureLimitation.UpdateTemperatureRelativeGrowth()
        )
        self.rPARRelativeGrowth = self.oPARLimitation.UpdatePARRelativeGrowth()
        self.rPhRelativeGrowth = self.oPhLimitation.UpdatePHRelativeGrowth()
        self.rO2RelativeGrowth = self.oO2Limitation.UpdateOxygenRelativeGrowth()
        self.rCO2RelativeGrowth = self.oCO2Limitation.UpdateCarbonDioxideRelativeGrowth()

    def CalculateAchievableGrowthRate(self):
        """
        Calculates the achievable growth rate based on the limiting factors.
        """
        if self.fTime > self.fLagTime:
            if self.sCalculationModel == "multiplicative":
                self.fAchievableCurrentBiomassGrowthRate = (
                    self.fTheoreticalCurrentBiomassGrowthRate
                    * self.rTemperatureRelativeGrowth
                    * self.rPhRelativeGrowth
                    * self.rO2RelativeGrowth
                    * self.rCO2RelativeGrowth
                    * self.rPARRelativeGrowth
                )
            elif self.sCalculationModel == "minimum":
                limiting_factors = [
                    self.rTemperatureRelativeGrowth,
                    self.rPhRelativeGrowth,
                    self.rO2RelativeGrowth,
                    self.rCO2RelativeGrowth,
                    self.rPARRelativeGrowth,
                ]
                fMinimumLimit = min(limiting_factors)
                self.fAchievableCurrentBiomassGrowthRate = (
                    self.fTheoreticalCurrentBiomassGrowthRate * fMinimumLimit
                )
        else:
            self.fAchievableCurrentBiomassGrowthRate = (
                self.fTheoreticalCurrentBiomassGrowthRate
            )
