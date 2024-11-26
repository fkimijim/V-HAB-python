class VolumeChanger(matter.manips.volume.Continuous):
    """
    VOLUMECHANGER: Changes the volume of a phase.

    A simple volume manipulator that compresses the volume of the phase
    to which it is added. It inherits from the base class
    matter.manips.volume.Continuous. The other available base class is 
    matter.manips.volume.Step. The difference between these two classes
    is that the Continuous manip uses a volume change rate per second,
    while the Step manip uses an absolute volume by which the phase
    volume instantly changes.
    """

    def __init__(self, sName, oPhase):
        super().__init__(sName, oPhase)

    def update(self):
        """
        Compresses the volume of the phase by 1% per 10 seconds.
        """
        fVolumeChangeRate = -(self.oPhase.fVolume / 100) / 10
        super().update(fVolumeChangeRate)
