from .. import Phase

MatterPhase = Phase()

class Gas(MatterPhase):
    """
    Gas class

    Describes a volume of ideally mixed gas using ideal gas assumptions.
    Must be located inside a store to work.
    """

    sType = 'gas'

    def __init__(self, oStore, sName, tfMasses, fVolume=None, fTemperature=None):
        """
        Initializes the gas phase.

        Args:
            oStore (object): Parent store instance.
            sName (str): Name of the phase.
            tfMasses (dict): Dictionary containing mass value for each species.
            fVolume (float, optional): Volume of the phase in m^3. Defaults to store's volume if not provided.
            fTemperature (float): Temperature of matter in the phase.
        """
        super().__init__(oStore, sName, tfMasses, fTemperature)

        # Use store volume if not explicitly provided
        self.fVolume = fVolume or oStore.fVolume
        self.fDensity = self.fMass / self.fVolume if self.fVolume else 0

        if self.fMass == 0:
            self.fMassToPressure = 0
            self.afPP = [0] * self.oMT.iSubstances
        else:
            fPressure = self.oMT.calculatePressure(self)
            if fPressure < self.oStore.oContainer.fMaxIdealGasLawPressure:
                # Ideal gas law: p V = m R T
                self.afPP = [
                    (self.afMass[i] * (self.oMT.Const.fUniversalGas / self.oMT.afMolarMass[i]) * fTemperature) / self.fVolume
                    for i in range(self.oMT.iSubstances)
                ]
                fPressure = sum(self.afPP)
                self.fMassToPressure = fPressure / self.fMass
            else:
                self.fMassToPressure = fPressure / self.fMass
                self.afPP = self.oMT.calculatePartialPressures(self)

        if self.afPP[self.oMT.tiN2I.H2O]:
            fSaturationVapourPressure = self.oMT.calculateVaporPressure(self.fTemperature, 'H2O')
            self.rRelHumidity = self.afPP[self.oMT.tiN2I.H2O] / fSaturationVapourPressure
        else:
            self.rRelHumidity = 0

    def calculatePressureCoefficient(self):
        """
        Calculate the pressure coefficient from the ideal gas law.

        Returns:
            float: Coefficient for pressure calculation.
        """
        if self.fPressure < self.oStore.oContainer.fMaxIdealGasLawPressure:
            return (self.oMT.Const.fUniversalGas * self.fTemperature) / (self.fMolarMass * self.fVolume)
        else:
            return self.oMT.calculatePressure(self) / self.fMass

    @property
    def afPartsPerMillion(self):
        """
        Calculate parts per million (PPM) values on demand.

        Returns:
            list: PPM values for each substance.
        """
        return self.oMT.calculatePartsPerMillion(self)

    def setTemperature(self, fTemperature):
        """
        Sets the temperature of the gas phase.

        Args:
            fTemperature (float): New temperature.
        """
        self.fTemperature = fTemperature
        if self.fVolume:
            self.fMassToPressure = self.calculatePressureCoefficient()

    def update(self):
        """
        Updates the gas phase properties.
        """
        super().update()

        if self.fVolume:
            self.fDensity = self.fMass / self.fVolume
            self.fMassToPressure = self.calculatePressureCoefficient()
            self.afPP = self.oMT.calculatePartialPressures(self)

            if self.afMass[self.oMT.tiN2I.H2O]:
                fSaturationVapourPressure = self.oMT.calculateVaporPressure(self.fTemperature, 'H2O')
                self.rRelHumidity = self.afPP[self.oMT.tiN2I.H2O] / fSaturationVapourPressure
            else:
                self.rRelHumidity = 0
        else:
            self.fMassToPressure = 0
