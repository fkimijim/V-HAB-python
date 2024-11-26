import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.f2f.f2f import F2F

f2f = F2F()

class Temp_Dummy(f2f):
    """
    Temp_Dummy calculates the necessary heat flow to keep all fluid passing
    through it at the specified temperature. It does not directly set the
    temperature but computes the heat flow required to maintain it.
    """

    def __init__(self, oMT, sName, fTemperature, fMaxHeatFlow=float('inf')):
        """
        Constructor for Temp_Dummy.

        Args:
            oMT: Material table object.
            sName: Name of the component.
            fTemperature: Target temperature [K].
            fMaxHeatFlow: Maximum allowable heat flow [W] (default: inf).
        """
        super().__init__(oMT, sName)
        self.fHydrDiam = 1  # Hydraulic diameter, irrelevant for manual solver
        self.fHydrLength = 0  # Hydraulic length, irrelevant for manual solver
        self.fDeltaTemp = 0  # Temperature difference in [K]
        self.fTemperature = fTemperature
        self.fMaxHeatFlow = fMaxHeatFlow
        self.bActiveTemperatureRegulation = True

        self.supportSolver("manual", True, self.updateManualSolver)
        self.supportSolver("callback", self.solverDeltas)

    def updateManualSolver(self):
        """
        Placeholder for the manual solver update.
        """
        pass

    def solverDeltas(self, _):
        """
        Callback solver for the delta pressure.

        Returns:
            float: Delta pressure (always 0 for this component).
        """
        return 0

    def updateThermal(self):
        """
        Update the heat flow required to maintain the target temperature.
        """
        if not self.bActiveTemperatureRegulation:
            self.fHeatFlow = 0
        else:
            try:
                # Determine the flow direction and pick the inflow
                Flow1, Flow2 = self.getFlows()

                if Flow1.fFlowRate > 0:
                    inFlow = Flow1
                else:
                    inFlow = Flow2
            except:
                # Fallback to the first flow if the above fails
                inFlow = self.aoFlows[0]

            # Calculate the temperature difference and heat flow
            self.fDeltaTemp = self.fTemperature - inFlow.fTemperature
            self.fHeatFlow = (inFlow.fFlowRate * inFlow.fSpecificHeatCapacity) * self.fDeltaTemp

            # Apply the maximum heat flow limit
            if self.fHeatFlow > self.fMaxHeatFlow:
                self.fHeatFlow = self.fMaxHeatFlow

    def setActive(self, bActive, _=None):
        """
        Activate or deactivate temperature regulation.

        Args:
            bActive: Boolean indicating if temperature regulation is active.
        """
        self.bActiveTemperatureRegulation = bActive
