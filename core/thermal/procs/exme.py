import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from branch import Branch
from conductors.fluidic import Fluidic

ThermalBranch = Branch()
ThermalManualBranch = Branch()
FluidicConductor = Fluidic()

class ExMe:
    """
    Extract/Merge (ExMe) processor for thermal systems.
    Extracts thermal energy from and merges thermal energy into a capacity.
    """

    def __init__(self, oCapacity, sName):
        """
        Constructor for the ExMe thermal processor class.

        Args:
            oCapacity: The capacity the ExMe belongs to.
            sName: Name of the processor.
        """
        self.sName = sName
        self.oMT = oCapacity.oMT
        self.oTimer = oCapacity.oTimer
        self.oCapacity = oCapacity
        self.oBranch = None
        self.iSign = None
        self.fHeatFlow = 0

        # Internal properties for reconnection
        self.oNewCapacity = None
        self.hReconnectExme = self.oTimer.register_post_tick(
            self.reconnect_exme_post_tick, 'thermal', 'post_capacity_temperatureupdate'
        )

        # Register with the capacity
        self.oCapacity.add_proc_exme(self)

    def add_branch(self, oBranch):
        """
        Assign a branch to this ExMe.

        Args:
            oBranch: The thermal branch to connect.

        Raises:
            Exception: If the branch cannot be added due to various conditions.
        """
        if self.oCapacity.oContainer.bThermalSealed:
            raise Exception("The container is sealed; no ports can be added.")
        elif self.oBranch is not None and oBranch != self.oBranch.coBranches[0]:
            raise Exception("A branch is already connected to this ExMe.")
        elif not isinstance(oBranch, ThermalBranch):
            raise Exception("The provided branch is not a ThermalBranch!")

        self.oBranch = oBranch

        if oBranch.coExmes[0] == self:
            self.iSign = -1
        else:
            self.iSign = 1

    def set_heat_flow(self, fHeatFlow):
        """
        Set the heat flow for this ExMe.

        Args:
            fHeatFlow: Heat flow in watts (W).
        """
        self.fHeatFlow = fHeatFlow

    def reconnect_exme(self, oNewCapacity, bMatterExmeCaller=False):
        """
        Change the capacity to which this ExMe is connected.

        Args:
            oNewCapacity: The new capacity to connect to.
            bMatterExmeCaller: Whether this is being called by a matter ExMe.

        Raises:
            Exception: If the operation is not allowed or inconsistent.
        """
        if oNewCapacity == self.oCapacity:
            return

        self.oNewCapacity = oNewCapacity
        self.hReconnectExme()

        if not isinstance(self.oBranch.oHandler, ThermalManualBranch) and \
           isinstance(self.oBranch.coConductors[0], FluidicConductor) and \
           not bMatterExmeCaller:
            raise Exception(
                f"Reconnecting a thermal ExMe ({self.sName}) modeling mass-bound energy transfer must be done through the matter ExMe!"
            )

    def reconnect_exme_post_tick(self):
        """
        Reconnect the ExMe to the new capacity during the post-tick phase.
        """
        if self.oBranch.coExmes[0] == self and \
           self.oNewCapacity.oContainer != self.oCapacity.oContainer:
            raise Exception(
                f"Cannot change the left-hand ExMe ({self.sName}) to a capacity in a different system!"
            )

        oOldCapacity = self.oCapacity
        self.oCapacity = self.oNewCapacity
        oOldCapacity.remove_exme(self)
        self.oCapacity.add_exme(self)
        self.oNewCapacity = None

    def disconnect_branch(self):
        """
        Disconnect the ExMe from its branch, breaking references.
        """
        self.oBranch = None

    def reconnect_branch(self, oBranch):
        """
        Reconnect the ExMe to a branch.

        Args:
            oBranch: The branch to reconnect to.
        """
        self.oBranch = oBranch
