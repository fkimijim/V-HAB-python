class ConstPressExme:
    def __init__(self, oPhase, sName, fPortPressure):
        self.oPhase = oPhase
        self.sName = sName
        self.fPortPressure = fPortPressure

    def get_exme_properties(self):
        """
        Returns the properties of the ExMe.

        Returns:
            fExMePressure: The port pressure.
            fExMeTemperature: The temperature of the associated phase.
        """
        fExMePressure = self.fPortPressure
        fExMeTemperature = self.oPhase.fTemperature
        return fExMePressure, fExMeTemperature
