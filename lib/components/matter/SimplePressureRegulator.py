import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.f2f.f2f import F2F

f2f = F2F()

class SimplePressureRegulator(f2f):
    """
    SimplePressureRegulator: Reduces the pressure in the branch to a specified
    value as long as a higher inlet pressure is available.
    """

    def __init__(self, oContainer, sName, fLimitPressure):
        """
        Constructor for SimplePressureRegulator.

        Args:
            oContainer: Parent container.
            sName: Name of the regulator.
            fLimitPressure: Target pressure limit in the branch.
        """
        super().__init__(oContainer, sName)
        
        self.fLimitPressure = fLimitPressure
        
        self.supportSolver('callback', self.solverDeltas)
        self.supportSolver('manual', False)

    def solverDeltas(self, _):
        """
        Update function for the callback solver.

        Args:
            _: Unused parameter (flow rate).

        Returns:
            fDeltaPressure: Calculated delta pressure to regulate flow.
        """
        if self.oBranch.fFlowRate > 0:
            fInletPressure = self.oBranch.coExmes[0].getExMeProperties()
        else:
            fInletPressure = self.oBranch.coExmes[1].getExMeProperties()
        
        if fInletPressure > self.fLimitPressure:
            fDeltaPressure = fInletPressure - self.fLimitPressure
        else:
            fDeltaPressure = 0
        
        self.fDeltaPressure = fDeltaPressure
        return fDeltaPressure

    def setLimitPressure(self, fLimitPressure):
        """
        Sets a new limit pressure for the regulator.

        Args:
            fLimitPressure: New pressure limit.
        """
        self.fLimitPressure = fLimitPressure
