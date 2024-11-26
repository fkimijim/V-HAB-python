import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.f2f.f2f import F2F

f2f = F2F()

class Valve(f2f):
    """
    A simple valve that can open and close branches.
    Works with interval and multi-branch iterative solvers.
    """

    def __init__(self, oContainer, sName, bOpen=True):
        """
        Constructor for the valve.

        Args:
            oContainer: The container object this valve belongs to.
            sName: Name of the valve [string].
            bOpen: Initial value of the valve setting [boolean].
        """
        super().__init__(oContainer, sName)

        # Initialize valve state
        if isinstance(bOpen, bool):
            self.bOpen = bool(bOpen)
        else:
            self.bOpen = True  # Default state is open

        # Set initial pressure drop based on valve state
        self.fDeltaPressure = 0 if self.bOpen else float('inf')

        # Supporting solvers
        self.supportSolver("callback", self.solverDeltas)
        self.supportSolver("manual", False)
        self.supportSolver("coefficient", self.calculatePressureDropCoefficient)

    def calculatePressureDropCoefficient(self, _):
        """
        Calculate the pressure drop coefficient for the valve.

        Returns:
            float: Pressure drop coefficient.
        """
        if self.bOpen:
            return 0
        else:
            # Returning the equivalent of uint64 maximum value as in MATLAB
            return 1.8446744073709552e+19

    def solverDeltas(self, _):
        """
        Solver for calculating delta pressure.

        Returns:
            float: Delta pressure across the valve.
        """
        if not self.bOpen:
            self.fDeltaPressure = float('inf')
            return float('inf')
        else:
            self.fDeltaPressure = 0
            return 0

    def setOpen(self, bOpen):
        """
        Set the state of the valve (open or closed).

        Args:
            bOpen: Boolean indicating whether the valve should be open.
        """
        self.bOpen = bool(bOpen)

        # Update delta pressure based on the state
        self.fDeltaPressure = 0 if self.bOpen else float('inf')

        # Mark the branch as outdated to recalculate flows
        self.oBranch.setOutdated()
