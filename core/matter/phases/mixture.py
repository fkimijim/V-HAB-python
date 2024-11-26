from .. import Phase

MatterPhase = Phase()

class Mixture(MatterPhase):
    """
    Mixture class

    This phase can be used to implement mixture phases that consist of different 
    substances that are normally in different phases (gas, liquid, solid). For 
    example, it can represent a phase containing zeolite (solid), CO2 (gas), and 
    water (liquid) simultaneously. Each substance is placed into a subtype.
    """

    sType = 'mixture'

    def __init__(self, oStore, sName, sPhaseType, tfMasses, fTemperature, fPressure):
        """
        Initializes the mixture phase.

        Args:
            oStore (object): Parent store instance.
            sName (str): Name of the phase.
            sPhaseType (str): Primary state of the matter ('gas', 'liquid', 'solid').
            tfMasses (dict): Dictionary containing mass value for each species.
            fTemperature (float): Temperature of matter in the phase.
            fPressure (float): Pressure of matter in the phase.
        """
        super().__init__(oStore, sName, tfMasses, fTemperature)

        self.sPhaseType = sPhaseType
        self.fInitialPressure = fPressure
        self.bGasPhase = sPhaseType == 'gas'
        self.fMassToPressure = fPressure / self.fMass if self.fMass != 0 else 0

        self.fDensity = self.oMT.calculateDensity(self)
        self.fVolume = self.fMass / self.fDensity if self.fMass != 0 else 0

        self.bMixture = True

    @property
    def afPP(self):
        """
        Partial pressures in the mixture (only valid for gas phases).

        Returns:
            list: Partial pressures [Pa].
        """
        if not self.bGasPhase:
            raise ValueError("Invalid access: Partial pressures are only available for gas phases.")
        return self.oMT.calculatePartialPressures(self)

    @property
    def rRelHumidity(self):
        """
        Relative humidity in the phase (only valid for gas phases).

        Returns:
            float: Relative humidity.
        """
        if not self.bGasPhase:
            raise ValueError("Invalid access: Relative humidity is only available for gas phases.")
        if self.afPP[self.oMT.tiN2I.H2O]:
            fSaturationVapourPressure = self.oMT.calculateVaporPressure(self.fTemperature, 'H2O')
            return self.afPP[self.oMT.tiN2I.H2O] / fSaturationVapourPressure
        else:
            return 0

    @property
    def afPartsPerMillion(self):
        """
        Substance concentrations in ppm (only valid for gas phases).

        Returns:
            list: Parts per million (PPM) values for each substance.
        """
        if not self.bGasPhase:
            raise ValueError("Invalid access: Parts per million are only available for gas phases.")
        return self.oMT.calculatePartsPerMillion(self)

    def update(self):
        """
        Updates the current state of the mixture. Pressure is calculated only for gas phases.
        """
        super().update()

        self.fDensity = self.fMass / self.fVolume if self.fVolume else 0

        if self.sPhaseType == 'gas':
            self.fMassToPressure = self.oMT.calculatePressure(self) / self.fMass if self.fMass != 0 else 0

    def get_fPressure(self):
        """
        Calculates the pressure of the mixture phase.

        Returns:
            float: Pressure of the phase.
        """
        if self.iVolumeManipulators == 0:
            # No volume manipulators, assume constant initial pressure
            return self.fInitialPressure
        else:
            if self.toManips.volume.bCompressible:
                fMassSinceUpdate = self.fCurrentTotalMassInOut * (self.oStore.oTimer.fTime - self.fLastMassUpdate)
                return self.fMassToPressure * (self.fMass + fMassSinceUpdate)
            else:
                return self.toManips.volume.oCompressibleManip.oPhase.fPressure
