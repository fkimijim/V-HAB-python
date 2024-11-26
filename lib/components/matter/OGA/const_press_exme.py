class ConstPressExme:
    """
    A Python equivalent of the const_press_exme MATLAB class.
    Represents an ExMe (exchange mechanism) with constant pressure for gas phases.
    """

    def __init__(self, oPhase, sName, fPortPressure):
        """
        Initialize the ConstPressExme class.

        Args:
            oPhase: The phase associated with this ExMe.
            sName: Name of the ExMe.
            fPortPressure: Constant pressure at the port in Pa.
        """
        self.oPhase = oPhase
        self.sName = sName
        self.fPortPressure = fPortPressure

    def getExMeProperties(self):
        """
        Retrieve the ExMe properties, including port pressure and phase temperature.

        Returns:
            Tuple of (fExMePressure, fExMeTemperature).
        """
        fExMePressure = self.fPortPressure
        fExMeTemperature = self.oPhase.fTemperature
        return fExMePressure, fExMeTemperature
