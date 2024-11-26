import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "base")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "event")))
from base import Base
from event.source import Source

BaseBranch = Base()
EventSource = Source()

class Conductor(BaseBranch, EventSource):
    """
    A thermal connection between two capacity objects.

    This base class can be used to model any thermal conduction interface
    between two capacities. Child classes providing radiative, convective,
    or conductive heat transport should inherit from this class.
    """

    def __init__(self, oContainer, sName):
        """
        Initialize a conductor instance.

        Args:
            oContainer (object): The system in which the conductor is located.
            sName (str): The name of the conductor, usually a combination of its associated capacity objects' names.
        """
        super().__init__()
        
        self.sName = sName
        self.oContainer = oContainer
        
        # Add the conductor to the thermal container
        self.oContainer.add_proc_conductor(self)
        
        # Reference to matter table and timer
        self.oMT = self.oContainer.oMT
        self.oTimer = self.oContainer.oTimer
        
        # Initialize properties
        self.oLeft = None
        self.oRight = None
        self.oThermalBranch = None
        self.bSealed = False
        
        # Conductor type flags
        self.bRadiative = False
        self.bConvective = False
        self.bConductive = False

    def seal(self, oThermalBranch):
        """
        Seal the conductor to prevent further changes and ensure consistency.

        Args:
            oThermalBranch (object): The thermal branch in which this conductor is placed.

        Raises:
            Exception: If the conductor is already sealed or improperly configured.
        """
        if self.bSealed:
            raise Exception(f"Conductor '{self.sName}' is already sealed.")

        # Ensure that the conductor is correctly configured as one type
        if sum([self.bRadiative, self.bConductive, self.bConvective]) > 1:
            raise Exception(
                f"Conductor '{self.sName}' is configured as multiple types. It must be one of radiative, conductive, or convective."
            )
        
        self.oThermalBranch = oThermalBranch
        self.bSealed = True

    @property
    def fResistance(self):
        """
        Abstract property for thermal resistance.

        Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must define the 'fResistance' property.")
