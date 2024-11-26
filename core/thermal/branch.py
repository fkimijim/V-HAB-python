import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "base")))
from branch import Branch

BaseBranch = Branch()

class Branch(BaseBranch):
    """
    Thermal branch class.
    Defines basic properties and methods required for all thermal branches.
    """

    def __init__(self, oContainer, xLeft, csProcs, xRight, sCustomName=None, oMatterObject=None):
        """
        Initialize a thermal branch.

        Args:
            oContainer: The container in which the branch is placed.
            xLeft: Left side capacity or interface.
            csProcs: List of conductor names in the branch.
            xRight: Right side capacity or interface.
            sCustomName: Optional custom name for the branch.
            oMatterObject: Optional matter object associated with this branch.
        """
        super().__init__(oContainer, xLeft, csProcs, xRight, sCustomName, "thermal")
        
        self.fConductivity = None  # [W/K] or [W/K^4]
        self.bRadiative = False
        self.bNoConductor = False
        self.fHeatFlow = 0  # [W]
        self.afTemperatures = []
        self.coConductors = []
        self.iConductors = 0
        self.oMatterObject = oMatterObject
        self.bTriggersetHeatFlowCallbackBound = False
        self.iIfConductors = None
        self.bActive = True

        if csProcs:
            self.create_procs(csProcs)

        try:
            self.bRadiative = self.coConductors[0].bRadiative
        except IndexError:
            self.bNoConductor = True

        self.oContainer.add_thermal_branch(self)
        self.iConductors = len(self.coConductors)

    def create_procs(self, csProcs):
        """
        Create conductor processors for the branch.

        Args:
            csProcs: List of conductor names to add to the branch.

        Raises:
            Exception: If a conductor is not found in the container.
        """
        for sProc in csProcs:
            if sProc not in self.oContainer.toProcsConductor:
                raise Exception(f"Conductor {sProc} not found on the system this branch belongs to!")
            self.coConductors.append(self.oContainer.toProcsConductor[sProc])

    def set_outdated(self):
        """
        Mark the branch as outdated, triggering recalculations.
        """
        if not self.bOutdated or self.oTimer.fTime > self.oHandler.fLastUpdate:
            self.bOutdated = True
            self.trigger("outdated")

    def set_if_length(self, iLength):
        """
        Set the interface length for system-subsystem connections.

        Args:
            iLength: Number of conductors in the interface branch.
        """
        self.iIfConductors = iLength

    def set_conductors(self, coConductors):
        """
        Combine conductors from the interface branch.

        Args:
            coConductors: List of conductors to assign to this branch.
        """
        self.coConductors = coConductors
        self.iConductors = len(self.coConductors)

    def bind(self, sType, callBack):
        """
        Bind a callback to a specific event type.

        Args:
            sType: Type of event to bind.
            callBack: Callback function to execute.

        Returns:
            tuple: Self and the unbind callback function.
        """
        self, unbindCallback = super().bind(sType, callBack)
        if sType == "setHeatFlow":
            self.bTriggersetHeatFlowCallbackBound = True
        return self, unbindCallback

    def set_active(self, bActive):
        """
        Activate or deactivate heat transfer for this branch.

        Args:
            bActive: Boolean indicating activation status.
        """
        self.bActive = bActive
        self.set_outdated()

    def set_heat_flow(self, fHeatFlow, afTemperatures):
        """
        Set the heat flow and temperature values for the branch.

        Args:
            fHeatFlow: Heat flow in watts.
            afTemperatures: List of temperatures across the branch.

        Raises:
            Exception: If the left side of the branch is an interface.
        """
        if self.abIf[0]:
            raise Exception("Cannot set flowrate on this branch object; left side is an interface.")

        self.fHeatFlow = fHeatFlow
        self.afTemperatures = afTemperatures
        self.bOutdated = False

        if self.bTriggersetHeatFlowCallbackBound:
            self.trigger("setHeatFlow")

    def seal(self):
        """
        Seal the branch, finalizing its configuration.

        Raises:
            Exception: If the branch is already sealed.
        """
        if self.bSealed:
            raise Exception("Already sealed")

        for conductor in self.coConductors:
            conductor.seal(self)

        self.hGetBranchData = None
        self.bSealed = True
