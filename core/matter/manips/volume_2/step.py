from abc import ABC
from volume_1 import VolumeManipulator

VolumeManipulator = VolumeManipulator()

class StepVolumeManipulator(VolumeManipulator, ABC):
    """
    A stationary volume manipulator changes the volume by fixed values, not flows.
    Different from the substance manipulator, the separation into stationary 
    and flow manipulators for volumes has nothing to do with flow phases but 
    is purely used to describe manipulators which describe volume change rates (flow) 
    or change the volume by fixed values (stationary).
    """

    # Identifies this manipulator as a stationary volume manipulator
    bStepVolumeProcessor = True

    def __init__(self, sName, oPhase, sRequiredType=None):
        """
        Constructor for StepVolumeManipulator.

        Parameters:
        - sName: str, Name of this manipulator.
        - oPhase: Phase, The phase object where this manipulator is located.
        - sRequiredType: str (optional), Specifies the phase type required (e.g., 'gas' or 'liquid').
        """
        super().__init__(sName, oPhase, sRequiredType)
