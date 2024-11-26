from abc import ABC, abstractmethod

class VolumeManipulator(ABC):
    """
    Abstract base class for volume manipulators.
    Allows the model to change the volume (and correspondingly the pressure) of a phase.
    This is the base class, providing a common parent class for all volume manipulators.
    """

    def __init__(self, sName, oPhase, sRequiredType=None):
        """
        Constructor for VolumeManipulator.
        Inputs:
        - sName: Name for this manipulator.
        - oPhase: Phase object in which this manipulator is located.
        - sRequiredType: Optional. Specifies a required phase type (e.g., 'gas', 'liquid').
        """
        self.sName = sName
        self.oPhase = oPhase
        self.sRequiredType = sRequiredType

        # Function handles for setting properties
        self.hSetVolume = None
        self.hSetMassToPressure = None

        # Time of the last update
        self.fLastExec = 0

        # Register update function for post-tick execution
        self.hBindPostTickUpdate = self.oPhase.oMT.oTimer.registerPostTick(
            self.update, "matter", "volumeManips"
        )

    def detachManip(self):
        """
        Detaches the manipulator from its current phase.
        This resets the handles `hSetVolume` and `hSetMassToPressure` to None.
        """
        self.hSetVolume = None
        self.hSetMassToPressure = None

    def reattachManip(self, oPhase):
        """
        Reattaches the manipulator to a new phase.
        Inputs:
        - oPhase: The phase object to which the manipulator should be reattached.
        """
        self.oPhase = oPhase
        self.hSetVolume = self.oPhase.bindSetProperty("fVolume")
        self.hSetMassToPressure = self.oPhase.bindSetProperty("fMassToPressure")

    @abstractmethod
    def update(self, fVolume, fPressure=None):
        """
        Updates the volume and optionally the pressure of the associated phase.
        Should be overridden by child classes to calculate new values and call this method.
        Inputs:
        - fVolume: New volume in m^3.
        - fPressure: Optional. New pressure in Pa. If not provided, pressure is calculated.
        """
        # Set the volume
        self.hSetVolume(fVolume)

        # Set the pressure, if provided
        if fPressure is not None:
            self.hSetMassToPressure(fPressure / self.oPhase.fMass)

        # Update the last execution time
        self.fLastExec = self.oPhase.oMT.oTimer.fTime
