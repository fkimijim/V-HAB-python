from .. import StepVolumeManipulator

StepVolumeManipulator = StepVolumeManipulator()

class IncompressibleMedium(StepVolumeManipulator):
    """
    This volume manipulator identifies a phase as incompressible.
    Incompressible in this context means the volume change from pressure changes 
    is negligible compared to compressible phases. However, density is still 
    calculated considering compression using the matter table.
    """

    # Identifies this manipulator as a stationary volume manipulator
    bCompressible = False

    def __init__(self, sName, oPhase, oCompressibleManip):
        """
        Class constructor for IncompressibleMedium.

        Parameters:
        - sName: str, Name for this manipulator.
        - oPhase: Phase, The phase object where this manipulator is located.
        - oCompressibleManip: CompressibleMedium, A reference to the associated compressible manipulator.
        """
        super().__init__(sName, oPhase)
        self.oCompressibleManip = oCompressibleManip

    def update(self, fNewVolume=None, fNewPressure=None):
        """
        Update method for IncompressibleMedium.

        This method sets the volume and pressure for the incompressible phase
        based on the calculations performed by a compressible manipulator.

        Parameters:
        - fNewVolume: float, New volume for the phase in m^3 (optional).
        - fNewPressure: float, New pressure for the phase in Pa (optional).
        """
        if fNewVolume is not None and fNewPressure is not None:
            super().update(fNewVolume, fNewPressure)
