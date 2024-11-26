import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from conductor import Conductor

ThermalProcsConductor = Conductor()

class Convective(ThermalProcsConductor):
    """
    A general conductor for convective heat transfer.
    This class cannot work on its own. You must create a child class
    and implement the `update_heat_transfer_coefficient` method,
    as it is highly use-case dependent.
    """

    def __init__(self, oContainer, sName, fArea, oMassBranch, iFlow):
        """
        Constructor for Convective.

        Args:
            oContainer (object): The system in which the conductor is placed.
            sName (str): A name for the conductor, unique within oContainer.
            fArea (float): Area of heat transfer in m^2.
            oMassBranch (object): The matter branch modeling the mass flow.
            iFlow (int): The number of the flow within this branch to model.
        """
        super().__init__(oContainer, sName)

        # Set conductor type to convective
        self.bConvective = True

        self.fArea = fArea
        self.oMassBranch = oMassBranch
        self.iFlow = iFlow

        # Bind the mass branch to detect flow rate changes
        self.oMassBranch.bind('setFlowRate', lambda _: self.set_outdated())

        # Initialize properties
        self.fResistance = 0
        self.fHeatTransferCoefficient = 0
        self.bSetOutdated = False

    def update(self, *args):
        """
        Update the thermal resistance of the conductor.
        This requires the `update_heat_transfer_coefficient` method
        to be implemented in the subclass.
        
        Returns:
            float: The updated thermal resistance.
        """
        self.fHeatTransferCoefficient = self.update_heat_transfer_coefficient()
        self.fResistance = 1 / (self.fHeatTransferCoefficient * self.fArea)
        self.bSetOutdated = False
        return self.fResistance

    def set_outdated(self, *args):
        """
        Mark the conductor as outdated, indicating the need for recalculation.
        Notifies the thermal branch to trigger updates.
        """
        if not self.bSetOutdated:
            self.oThermalBranch.set_outdated()
            self.bSetOutdated = True

    def update_heat_transfer_coefficient(self):
        """
        Abstract method to update the heat transfer coefficient.
        Must be implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")
