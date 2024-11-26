from abc import ABC
from volume_1 import VolumeManipulator

VolumeManipulator = VolumeManipulator()

class ContinuousVolumeManipulator(VolumeManipulator, ABC):
    """
    A continuous volume manipulator changes the volume with a change rate in m^3/s.
    Different from the substance manipulator, the separation into stationary 
    and flow manipulators for volumes is purely used to describe manipulators 
    which describe volume change rates (flow) or change the volume by fixed values (stationary).
    """

    def __init__(self, sName, oPhase, sRequiredType=None):
        """
        Constructor for ContinuousVolumeManipulator.

        Parameters:
        - sName: str, Name of this manipulator.
        - oPhase: Phase, The phase object where this manipulator is located.
        - sRequiredType: str (optional), Specifies the phase type required (e.g., 'gas' or 'liquid').
        """
        super().__init__(sName, oPhase, sRequiredType)
        self.fVolumeChangeRate = 0  # [m^3/s]
        self.fTimeStep = None
        self.rMaxVolumeChange = 0.1
        self.bStepVolumeProcessor = False
        self.setTimeStep = None

    def detach_manip(self):
        """
        Detach the manipulator from its associated phase and reset specific handles.
        """
        super().detach_manip()
        self.setTimeStep = None

    def reattach_manip(self, oPhase):
        """
        Reattach the manipulator to a new phase and bind related handles.

        Parameters:
        - oPhase: Phase, The new phase to attach this manipulator to.
        """
        super().reattach_manip(oPhase)

        self.setTimeStep = self.oTimer.bind(
            lambda: self.oPhase.register_update(),
            0,
            {
                "sMethod": "update",
                "sDescription": "The .register_update method of the phase of this volume manipulator",
                "oSrcObj": self,
            },
        )

        self.oPhase.bind("update_post", lambda: self.reset_time_step())

    def update(self, fVolumeChangeRate):
        """
        Update the volume change rate of the manipulator.

        Parameters:
        - fVolumeChangeRate: float, Rate of volume change in m^3/s.
        """
        fElapsedTime = self.oTimer.fTime - self.fLastExec

        if fElapsedTime > 0:
            fVolumeChange = self.fVolumeChangeRate * fElapsedTime
            fNewPhaseVolume = self.oPhase.fVolume + fVolumeChange
            super().update(fNewPhaseVolume)

        self.fVolumeChangeRate = fVolumeChangeRate

        self.fTimeStep = abs((self.rMaxVolumeChange * self.oPhase.fVolume) / self.fVolumeChangeRate)
        self.setTimeStep(self.fTimeStep)

    def reset_time_step(self):
        """
        Reset the last time the time step of this manipulator was set.
        This is triggered when the phase updates due to other calculations.
        """
        if self.setTimeStep is not None:
            self.setTimeStep(self.fTimeStep, True)
