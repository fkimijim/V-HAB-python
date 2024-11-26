from .. import Phase

MatterPhase = Phase()

class Liquid(MatterPhase):
    """
    Liquid class

    Describes a volume of ideally mixed liquid. In V-HAB, liquids are generally
    assumed incompressible, though compressible liquids are possible in principle.
    """

    sType = 'liquid'

    def __init__(self, oStore, sName, tfMasses, fTemperature, fPressure=None):
        """
        Initializes the liquid phase.

        Args:
            oStore (object): Parent store instance.
            sName (str): Name of the phase.
            tfMasses (dict): Dictionary containing mass value for each species.
            fTemperature (float): Temperature of matter in the phase.
            fPressure (float, optional): Pressure of matter in the phase. Defaults to standard pressure.
        """
        super().__init__(oStore, sName, tfMasses, fTemperature)

        self.fTemperature = fTemperature

        if fPressure is not None:
            self.fMassToPressure = fPressure / self.fMass if self.fMass != 0 else 0
            self.fInitialPressure = fPressure
        else:
            self.fMassToPressure = self.oMT.Standard.Pressure / self.fMass if self.fMass != 0 else 0
            self.fInitialPressure = self.oMT.Standard.Pressure

        self.fDensity = self.oMT.calculateDensity(self)

        self.fVolume = self.fMass / self.fDensity if self.fMass != 0 else 0

    def update(self):
        """
        Liquid update

        Calls the update methods of external manipulators (EXMEs) as liquids
        can be gravity-driven.
        """
        super().update()

        for exme in self.coProcsEXME:
            exme.update()

    def get_fPressure(self):
        """
        Calculates the pressure of the liquid phase.

        Returns:
            float: Pressure of the liquid phase.
        """
        if self.iVolumeManipulators == 0:
            # No volume manipulators, assume constant initial pressure.
            return self.fInitialPressure
        else:
            if self.toManips.volume.bCompressible:
                fMassSinceUpdate = self.fCurrentTotalMassInOut * (self.oStore.oTimer.fTime - self.fLastMassUpdate)
                return self.fMassToPressure * (self.fMass + fMassSinceUpdate)
            else:
                return self.toManips.volume.oCompressibleManip.oPhase.fPressure
