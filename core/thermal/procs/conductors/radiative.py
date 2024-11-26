import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from conductor import Conductor

ThermalProcsConductor = Conductor()

class Radiative(ThermalProcsConductor):
    """
    A radiative conductor transferring heat through thermal radiation.
    """

    def __init__(self, oContainer, sName, fResistance):
        """
        Initialize a radiative conductor.

        Args:
            oContainer (object): The system in which the conductor is placed.
            sName (str): The unique name of this conductor within the container.
            fResistance (float): The resistance value for this conductor in [K/W].
        """
        super().__init__(oContainer, sName)

        # Set conductor type to radiative
        self.bRadiative = True

        # Set resistance
        self.fResistance = fResistance

    def update(self, *args):
        """
        Update the thermal resistance of this conductor.

        Returns:
            float: The current thermal resistance.
        """
        # Default behavior for radiative conductors with fixed resistance.
        # Override this in subclasses for dynamic behavior.
        return self.fResistance
