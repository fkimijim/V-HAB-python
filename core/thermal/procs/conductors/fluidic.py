import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from conductor import Conductor

ThermalProcsConductor = Conductor()

class Fluidic(ThermalProcsConductor):
    """
    A fluidic conductor modeling the mass-bound heat transfer.
    """

    def __init__(self, oContainer, sName, oMatterObject):
        """
        Initialize a Fluidic conductor.

        Args:
            oContainer (object): The system in which the conductor is placed.
            sName (str): A unique name for the conductor within the container.
            oMatterObject (object): The matter object modeling the mass flow
                                    (branch or P2P processor).
        """
        super().__init__(oContainer, sName)

        # Set reference to the matter object
        self.oMatterObject = oMatterObject

        # Determine if the object is a branch and has processors
        self.bNoMatterProcessor = True
        self.oMatterProcessor = None
        if getattr(oMatterObject, "sObjectType", "") == "branch":
            if oMatterObject.aoFlowProcs:
                self.oMatterProcessor = next(
                    (proc for proc in oMatterObject.aoFlowProcs if proc.sName == sName),
                    None,
                )
                self.bNoMatterProcessor = self.oMatterProcessor is None

        # Initialize properties
        self.fResistance = 0  # Thermal resistance in [K/W]
        self.fSpecificHeatCapacity = 0
        self.fPressureLastHeatCapacityUpdate = None
        self.fTemperatureLastHeatCapacityUpdate = None
        self.arPartialMassLastHeatCapacityUpdate = None
        self.iFailedHeatCapacityUpdates = 0

    def update(self, *args):
        """
        Update the thermal resistance of this conductor.

        Returns:
            float: The updated thermal resistance.
        """
        if self.oMatterObject.fFlowRate == 0:
            self.fResistance = float("inf")
            return self.fResistance

        # Determine the specific heat capacity
        if self.oThermalBranch.oHandler.bP2P:
            self.fSpecificHeatCapacity = self.oMatterObject.fSpecificHeatCapacity
        else:
            # Handle branches or processors
            if self.bNoMatterProcessor:
                iFlowIndex = (
                    self.oMatterObject.iFlows
                    if self.oMatterObject.fFlowRate >= 0
                    else 1
                )
                oFlow = self.oMatterObject.aoFlows[iFlowIndex - 1]
            else:
                iFlowIndex = 1 if self.oMatterObject.fFlowRate > 0 else 2
                oFlow = self.oMatterProcessor.aoFlows[iFlowIndex - 1]

            # Update specific heat capacity if conditions changed
            if (
                self.fPressureLastHeatCapacityUpdate is None
                or abs(self.fPressureLastHeatCapacityUpdate - oFlow.fPressure) > 100
                or abs(self.fTemperatureLastHeatCapacityUpdate - oFlow.fTemperature) > 1
                or max(
                    abs(
                        self.arPartialMassLastHeatCapacityUpdate - oFlow.arPartialMass
                    )
                )
                > 0.01
            ):
                try:
                    self.fSpecificHeatCapacity = self.oMT.calculate_specific_heat_capacity(
                        oFlow
                    )
                    self.iFailedHeatCapacityUpdates = 0
                except Exception as e:
                    self.iFailedHeatCapacityUpdates += 1
                    if self.iFailedHeatCapacityUpdates > 2:
                        branch_name = getattr(
                            self.oMatterObject, "sCustomName", self.oMatterObject.sName
                        )
                        raise RuntimeError(
                            f"Heat capacity update failed for branch: {branch_name}. "
                            f"Flow Rate: {self.oMatterObject.fFlowRate} [kg/s], "
                            f"Heat Capacity: {self.fSpecificHeatCapacity} [J/(kgK)]"
                        ) from e

                # Store the state for the next update
                self.fPressureLastHeatCapacityUpdate = oFlow.fPressure
                self.fTemperatureLastHeatCapacityUpdate = oFlow.fTemperature
                self.arPartialMassLastHeatCapacityUpdate = oFlow.arPartialMass

        # Calculate thermal resistance
        self.fResistance = 1 / abs(
            self.oMatterObject.fFlowRate * self.fSpecificHeatCapacity
        )
        return self.fResistance

    def update_connected_matter_branch(self, oMassBranch):
        """
        Update the matter object associated with this conductor.

        Args:
            oMassBranch (object): The new matter branch to associate.
        """
        self.oMatterObject = oMassBranch
