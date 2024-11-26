import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from conductor import Conductor

ThermalProcsConductor = Conductor()

class Conductive(ThermalProcsConductor):
    """
    Conductive
    A conductor class for modeling heat conduction through a material (e.g., metal).
    """

    def __init__(self, oContainer, sName, fResistance):
        """
        Constructor for the Conductive class.

        Args:
            oContainer (object): The system in which the conductor is placed.
            sName (str): The name of this conductor, making it uniquely identifiable in its system.
            fResistance (float): The thermal resistance of the conductor in [K/W].
        """
        # Call the parent constructor
        super().__init__(oContainer, sName)

        # Set the conductor type to conductive
        self.bConductive = True

        # Set thermal resistance
        self.fResistance = fResistance

    def update(self, *args):
        """
        Update function for the conductor.

        Returns:
            float: The current thermal resistance of the conductor in [K/W].
        """
        # Default update does nothing for basic conductors.
        # Subclasses can override this method to implement resistance recalculation logic.
        return self.fResistance
