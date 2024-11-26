import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exme")))
import ExMe

MatterProcsExMe = ExMe()

class GasExMe(MatterProcsExMe):
    """
    GasExMe: An EXME that interfaces with a gaseous phase.

    This class provides the method `getExMeProperties()` which returns the 
    pressure and temperature of the attached gaseous phase.
    """

    def __init__(self, oPhase, sName):
        """
        Initializes the GasExMe.

        Args:
            oPhase (object): The phase the EXME is attached to.
            sName (str): The name of the processor.
        """
        super().__init__(oPhase, sName)

    def getExMeProperties(self):
        """
        Returns the properties of the EXME for a gaseous phase.

        Returns:
            tuple:
                - fExMePressure (float): Pressure of the mass passing through this EXME in Pa.
                - fExMeTemperature (float): Temperature of the mass passing through this EXME in K.
        """
        fExMeTemperature = self.oPhase.fTemperature
        fExMePressure = self.oPhase.fPressure
        return fExMePressure, fExMeTemperature
