import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exme")))
import ExMe

MatterProcsExMe = ExMe()

class MixtureExMe(MatterProcsExMe):
    """
    MixtureExMe: An EXME that interfaces with a mixture phase.

    Provides the method `getExMeProperties` which returns the pressure 
    and temperature of the attached phase.
    """

    def __init__(self, oPhase, sName):
        """
        Initialize the MixtureExMe.

        Args:
            oPhase (object): The phase the EXME is attached to.
            sName (str): The name of the processor.
        """
        super().__init__(oPhase, sName)

    def getExMeProperties(self):
        """
        Returns the EXME properties of the phase.

        Returns:
            tuple:
                - fExMePressure (float): Pressure of the mass passing through this EXME in Pa.
                - fExMeTemperature (float): Temperature of the mass passing through this EXME in K.
        """
        fExMePressure = self.oPhase.fPressure
        fExMeTemperature = self.oPhase.fTemperature
        return fExMePressure, fExMeTemperature
