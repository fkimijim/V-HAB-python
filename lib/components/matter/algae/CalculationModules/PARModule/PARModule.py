import math
import numpy as np

class PARModule:
    """
    PARModule determines the availability of radiation power for photosynthesis in the medium 
    and calculates the heat transfer into the medium due to absorbed but unused energy.
    """

    def __init__(self, oCallingSystem):
        self.oCallingSystem = oCallingSystem

        # Light properties set through the PBR system definition
        self.sLightColor = self.oCallingSystem.oParent.sLightColor  # Light color
        self.fSurfacePPFD = self.oCallingSystem.oParent.fSurfacePPFD  # [μmol/m2s]
        self.fDepthBelowSurface = self.oCallingSystem.oParent.fDepthBelowSurface  # [m]
        self.fWaterVolume = (
            self.oCallingSystem.toStores.GrowthChamber.toPhases.GrowthMedium.afMass[
                self.oCallingSystem.oMT.tiN2I.H2O
            ]
            / self.oCallingSystem.fCurrentGrowthMediumDensity
        )  # [m3]
        self.fIlluminatedSurface = self.fWaterVolume / self.fDepthBelowSurface  # [m2]

        # Algae parameters (defined experimentally)
        self.fMinimumPPFD = 1  # [μmol/m2s]
        self.fSaturationPPFD = 100  # [μmol/m2s]
        self.fInhibitionPPFD = 400  # [μmol/m2s]

        # Hyperbolic model parameters (Yun and Park, 2001)
        self.fAmaxRed = 1283
        self.fBRed = 1.36
        self.fAmaxYellow = 1025
        self.fBYellow = 1.04
        self.fAmaxGreen = 945.6
        self.fBGreen = 0.92
        self.fAmaxBlue = 1719
        self.fBBlue = 1.79
        self.fAmaxDaylight = 1041
        self.fBDaylight = 1.03
        self.fAmaxRedExperimental = 3619
        self.fBRedExperimental = 8.369

        # Set the attenuation coefficient parameters based on the light color
        if self.sLightColor == "Red":
            self.fAmax = self.fAmaxRed
            self.fBconstant = self.fBRed
            self.fReferenceWavelength = 660e-9  # [m]
        elif self.sLightColor == "Blue":
            self.fAmax = self.fAmaxBlue
            self.fBconstant = self.fBBlue
            self.fReferenceWavelength = 450e-9  # [m]
        elif self.sLightColor == "Yellow":
            self.fAmax = self.fAmaxYellow
            self.fBconstant = self.fBYellow
            self.fReferenceWavelength = 600e-9  # [m]
        elif self.sLightColor == "Green":
            self.fAmax = self.fAmaxGreen
            self.fBconstant = self.fBGreen
            self.fReferenceWavelength = 550e-9  # [m]
        elif self.sLightColor == "Daylight":
            self.fAmax = self.fAmaxDaylight
            self.fBconstant = self.fBDaylight
            self.fReferenceWavelength = 495e-9  # [m]
        elif self.sLightColor == "RedExperimental":
            self.fAmax = self.fAmaxRedExperimental
            self.fBconstant = self.fBRedExperimental
            self.fReferenceWavelength = 670e-9  # [m]

        # Heat parameters
        self.fPhotosyntheticEfficiency = 0.05  # Fraction of PS energy over absorbed energy
        self.fPlancksConstant = 6.63e-34  # [J*s]
        self.fSpeedOfLight = 3e8  # [m/s]

    def update(self):
        """
        Update the PAR calculations. If the culture is dead, skip growth calculations.
        """
        bDead = self.oCallingSystem.oGrowthRateCalculationModule.bDead
        if not bDead:
            self.CalculateAttenuationCoefficient()
            self.CalculateAlgalRadiationBoundaryPositions()
            self.CalculateGrowthVolumes()
            self.CalculateAverageRadiationInLinearGrowthVolume()
        self.CalculateHeatFromRadiation(bDead)

    def CalculateAttenuationCoefficient(self):
        """
        Calculate the attenuation coefficient using the hyperbolic model.
        """
        fCurrentBiomass = (
            self.oCallingSystem.toStores.GrowthChamber.toPhases.GrowthMedium.afMass[
                self.oCallingSystem.oMT.tiN2I.Chlorella
            ]
        )
        self.fBiomassConcentration = fCurrentBiomass / self.fWaterVolume  # [kg/m3]
        self.fAttenuationCoefficient = (
            self.fAmax * self.fBiomassConcentration
        ) / (self.fBconstant + self.fBiomassConcentration)  # [1/m]

    def CalculateAlgalRadiationBoundaryPositions(self):
        """
        Calculate the positions of minimum, saturation, and inhibition PPFD.
        """
        self.fPositionMinimumPPFD = (-math.log(self.fMinimumPPFD / self.fSurfacePPFD)) / self.fAttenuationCoefficient
        self.fPositionSaturationPPFD = (-math.log(self.fSaturationPPFD / self.fSurfacePPFD)) / self.fAttenuationCoefficient
        self.fPositionInhibitionPPFD = (-math.log(self.fInhibitionPPFD / self.fSurfacePPFD)) / self.fAttenuationCoefficient

        # Adjust positions to stay within the depth of the reactor
        self.fPositionMinimumPPFD = max(0, min(self.fDepthBelowSurface, self.fPositionMinimumPPFD))
        self.fPositionSaturationPPFD = max(0, min(self.fDepthBelowSurface, self.fPositionSaturationPPFD))
        self.fPositionInhibitionPPFD = max(0, min(self.fDepthBelowSurface, self.fPositionInhibitionPPFD))

    def CalculateGrowthVolumes(self):
        """
        Calculate the reactor's growth volumes in different PPFD zones.
        """
        self.fNoGrowthVolume = (
            self.fDepthBelowSurface - self.fPositionMinimumPPFD + self.fPositionInhibitionPPFD
        ) * self.fIlluminatedSurface  # [m3]
        self.fLinearGrowthVolume = (
            self.fPositionMinimumPPFD - self.fPositionSaturationPPFD
        ) * self.fIlluminatedSurface  # [m3]
        self.fSaturatedGrowthVolume = (
            self.fPositionSaturationPPFD - self.fPositionInhibitionPPFD
        ) * self.fIlluminatedSurface  # [m3]

    def CalculateAverageRadiationInLinearGrowthVolume(self):
        """
        Calculate the average PPFD in the linear growth volume.
        """
        if self.fPositionMinimumPPFD != self.fPositionSaturationPPFD:
            self.fAveragePPFDLinearGrowth = (
                self.fSurfacePPFD / (self.fPositionMinimumPPFD - self.fPositionSaturationPPFD)
            ) * (
                math.exp(-self.fAttenuationCoefficient * self.fPositionSaturationPPFD)
                - math.exp(-self.fAttenuationCoefficient * self.fPositionMinimumPPFD)
            ) / self.fAttenuationCoefficient
        else:
            self.fAveragePPFDLinearGrowth = 0  # [μmol/(m2s)]

    def CalculateHeatFromRadiation(self, bDead):
        """
        Calculate the heat generated from radiation absorption.
        """
        if bDead:
            self.fPPFDtoHeat = self.fSurfacePPFD  # All absorbed photons go to heat
        else:
            # Absorption and heat calculations
            pass
