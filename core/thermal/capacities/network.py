import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from capacity import Capacity

ThermalCapacity = Capacity()

class Network(ThermalCapacity):
    """
    NETWORK
    A capacity intended for use with the advanced thermal multi-branch solver.
    For this capacity, the thermal multi-branch solver handles temperature calculations and other functionalities.
    """

    def __init__(self, oPhase, fTemperature, bBoundary=False):
        """
        Constructor for the Network class.

        Args:
            oPhase (object): Phase object associated with the capacity.
            fTemperature (float): Initial temperature of the network capacity.
            bBoundary (bool): Indicates if the capacity is a boundary.
        """
        super().__init__(oPhase, fTemperature)
        
        if bBoundary:
            self.bBoundary = bBoundary

        self.set_time_step(float('inf'), True)

    def update_temperature(self, fTemperature=None):
        """
        Updates the temperature and time step values for the capacity.

        Args:
            fTemperature (float, optional): New temperature value to set. If None, the temperature remains unchanged.
        """
        fTime = self.oTimer.fTime
        fLastStep = fTime - self.fLastTemperatureUpdate

        self.fLastTemperatureUpdate = fTime
        self.fTemperatureUpdateTimeStep = fLastStep

        # Set temperature only if provided
        if fTemperature is not None:
            self.set_temperature(fTemperature)

        # Trigger the post temperature update event if bound
        if self.bTriggerSetUpdateTemperaturePostCallbackBound:
            self.trigger("updateTemperature_post")

    def set_outdated_ts(self):
        """
        Marks the capacity as outdated and informs the thermal multi-branch solver to update.
        """
        # Update the total heat source heat flow property
        afHeatSourceFlows = [
            heat_source.fRequestedHeatFlow for heat_source in self.coHeatSource
        ]
        self.fTotalHeatSourceHeatFlow = sum(afHeatSourceFlows)

        # Set the time step to infinity if not already set
        if self.fTimeStep != float('inf'):
            self.set_time_step(float('inf'), True)

        # Trigger the outdated time step event for the network
        self.trigger("OutdatedNetworkTimeStep")

    def calculate_time_step(self):
        """
        Placeholder for time step calculation.
        """
        pass
