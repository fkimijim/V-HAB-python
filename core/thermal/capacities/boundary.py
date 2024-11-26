import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from capacity import Capacity

ThermalCapacity = Capacity()

class Boundary(ThermalCapacity):
    """
    BOUNDARY
    A capacity with an infinitely large heat capacity.
    The temperature of this capacity is constant and should only be changed 
    using the set_boundary_temperature() method. The update_temperature() 
    and update_specific_heat_capacity() methods of the parent class are 
    overridden to do nothing.
    """

    def __init__(self, oPhase, fTemperature):
        """
        Constructor for the Boundary class.
        
        Args:
            oPhase (object): Phase object associated with the capacity.
            fTemperature (float): Initial temperature of the boundary.
        """
        super().__init__(oPhase, fTemperature)

        # Since this is a boundary capacity, its temperature should never change.
        # This is equivalent to an infinite heat capacity.
        self.fTotalHeatCapacity = float('inf')

        self.bBoundary = True

    def set_boundary_temperature(self, fTemperature):
        """
        External function to set the boundary temperature.

        Args:
            fTemperature (float): New temperature for the boundary.
        """
        self.set_temperature(fTemperature)

        # Update the specific heat capacity, since this is relevant for changes.
        self.fSpecificHeatCapacity = self.oMT.calculate_specific_heat_capacity(self.oPhase)

    def update_temperature(self, _=None):
        """
        Overridden function to handle time step values and set outdated status.
        """
        fTime = self.oTimer.fTime
        fLastStep = fTime - self.fLastTemperatureUpdate

        self.fLastTemperatureUpdate = fTime
        self.fTemperatureUpdateTimeStep = fLastStep

        # Mark the capacity as outdated for time step purposes
        self.set_outdated_ts()

        if self.bTriggerSetUpdateTemperaturePostCallbackBound:
            self.trigger('updateTemperature_post')

    def update_specific_heat_capacity(self):
        """
        Overridden function. Does nothing in the Boundary class.
        """
        pass
