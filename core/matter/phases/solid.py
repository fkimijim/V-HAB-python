from .. import Phase

MatterPhase = Phase()

class Solid(MatterPhase):
    """
    Solid class

    Describes an ideally mixed solid phase. Solids assume standard pressure for 
    calculations unless volume manipulators are added to the store. When volume 
    manipulators are present, the solid will receive the pressure from the compressible 
    phases.
    """

    sType = 'solid'

    def __init__(self, oStore, sName, tfMasses, fTemperature, _=None):
        """
        Initializes the solid phase.

        Args:
            oStore (object): Parent store instance.
            sName (str): Name of the phase.
            tfMasses (dict): Dictionary containing mass value for each species.
            fTemperature (float): Temperature of matter in the phase.
        """
        super().__init__(oStore, sName, tfMasses, fTemperature)

        # Initialize to standard pressure
        self.fMassToPressure = self.oMT.Standard.Pressure / self.fMass if self.fMass != 0 else 0
        self.fDensity = self.oMT.calculateDensity(self)
        self.fVolume = self.fMass / self.fDensity if self.fMass != 0 else 0

    def update(self):
        """
        Updates the solid phase properties.

        Sets the mass-to-pressure parameters if corresponding volume manipulators are used.
        """
        super().update()

        self.fDensity = self.fMass / self.fVolume if self.fVolume else 0
        if self.toManips.volume:
            self.fMassToPressure = self.oMT.Standard.Pressure / self.fMass if self.fMass != 0 else 0

    def get_fPressure(self):
        """
        Calculates the pressure of the solid phase.

        Returns:
            float: Pressure of the solid phase.
        """
        if self.iVolumeManipulators == 0:
            # No volume manipulators, assume standard pressure
            return self.oMT.Standard.Pressure
        else:
            if self.toManips.volume.bCompressible:
                fMassSinceUpdate = self.fCurrentTotalMassInOut * (self.oStore.oTimer.fTime - self.fLastMassUpdate)
                return self.fMassToPressure * (self.fMass + fMassSinceUpdate)
            else:
                return self.toManips.volume.oCompressibleManip.oPhase.fPressure
