import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "matter")))
import Flow

MatterFlow = Flow()

class F2F:
    """
    F2F (Flow-to-Flow) Processor

    Manipulates a matter flow or stream. Connected to two different flows:
    left and right. Depending on the flow rate, the left is the inflow and
    the right is the outflow (positive flow rate), or vice versa for negative 
    flow rate. Can manipulate the pressure or temperature of the flow but NOT 
    the composition. For processes like adsorption, use P2Ps.
    """

    def __init__(self, oContainer, sName):
        """
        Initializes the F2F processor.

        Args:
            oContainer (object): Container (vsys) where the F2F is located.
            sName (str): Name of the F2F processor.
        """
        self.sName = sName
        self.oContainer = oContainer
        self.oContainer.addProcF2F(self)

        self.oMT = self.oContainer.oMT
        self.oTimer = self.oContainer.oTimer

        self.aoFlows = [None, None]
        self.abSetFlows = [False, False]

        self.oBranch = None
        self.bSealed = False
        self.toSolve = {}

        self.fHeatFlow = 0
        self.bActive = False
        self.bCheckValve = False
        self.bThermalActive = hasattr(self, "updateThermal")
        self.bFlowRateDependPressureDrop = True
        self.fDeltaPressure = 0

    def seal(self, oBranch):
        """
        Seals the F2F processor and sets the branch property.

        Args:
            oBranch (object): Reference to the branch object.
        """
        if self.bSealed:
            raise RuntimeError("The F2F processor is already sealed!")
        self.oBranch = oBranch
        self.bSealed = True

    def addFlow(self, oFlow, iFlowID=None):
        """
        Adds a flow to the F2F processor. Called during branch construction.

        Args:
            oFlow (object): The matter flow object to connect.
            iFlowID (int, optional): Flow ID (1 for left, 2 for right). Auto-detected if not provided.

        Raises:
            ValueError: If the flow is invalid or already registered.
        """
        if not isinstance(oFlow, MatterFlow):
            raise ValueError("The provided flow object must be an instance of MatterFlow.")

        if oFlow in self.aoFlows:
            raise ValueError("The provided flow object is already registered.")

        if iFlowID is None:
            iFlowID = self.abSetFlows.index(False) + 1

        if iFlowID < len(self.aoFlows) and self.aoFlows[iFlowID - 1] is not None:
            raise ValueError(
                f"The F2F processor '{self.sName}' is already in use by another branch."
            )

        self.aoFlows[iFlowID - 1] = oFlow
        self.abSetFlows[iFlowID - 1] = True

        oFlow.addProc(self, lambda: self._removeFlow(oFlow))

    def supportSolver(self, sType, *args):
        """
        Provides compatibility with specific solver types.

        Args:
            sType (str): Type of the solver (e.g., 'callback', 'manual').
            *args: Arguments for the specific solver type.
        """
        solver_class = getattr(solver.matter.base.type, sType)
        self.toSolve[sType] = solver_class(*args)

    def getFlows(self, fFlowRate=None):
        """
        Gets the current inflow and outflow based on the flow rate.

        Args:
            fFlowRate (float, optional): Defined flow rate. Defaults to the flow rate of the left flow.

        Returns:
            tuple: Inflow and outflow objects.
        """
        if fFlowRate is None:
            fFlowRate = self.aoFlows[0].fFlowRate

        if fFlowRate >= 0:
            return self.aoFlows[0], self.aoFlows[1]
        else:
            return self.aoFlows[1], self.aoFlows[0]

    def _removeFlow(self):
        """
        Removes the flows from this F2F processor.

        Necessary to reconnect the F2F to another flow and branch.
        """
        self.aoFlows = [None, None]
        self.oBranch = None
