import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.f2f.f2f import F2F

f2f = F2F()

class Pump(f2f):
    """
    PUMP: Linear, static, RPM independent dummy pump model.
    Multiplies the current delta pressure with a factor derived 
    from the difference between the actual flow rate and the setpoint flow rate.
    """

    def __init__(self, oContainer, sName, fFlowRateSP):
        """
        Constructor for the Pump class.

        Args:
            oContainer: Parent container.
            sName: Name of the pump.
            fFlowRateSP: Flow rate setpoint in kg/s.
        """
        super().__init__(oContainer, sName)

        self.fMaxFlowRate = 1         # Maximum flow rate in kg/s
        self.fMinDeltaP = 1           # Minimum delta pressure the pump must produce
        self.fMaxDeltaP = 8700000     # Maximum delta pressure the pump can produce
        self.fDampeningFactor = 4     # Controls how fast the pump reacts to setpoint changes

        self.fFlowRateSP = fFlowRateSP
        self.fPreviousSetpoint = fFlowRateSP
        self.iDir = 1 if fFlowRateSP > 0 else -1

        self.supportSolver('hydraulic', -5, 0.1, True, self.update)
        self.supportSolver('callback', self.solverDeltas)

        self.bActive = True

    def update(self):
        """
        Update function for the pump in the hydraulic solver.
        """
        if not self.aoFlows or abs(self.aoFlows[0].fFlowRate) == 0:
            # No flow, set maximum delta pressure if setpoint is non-zero
            if self.fFlowRateSP != 0:
                fFlowRate = 0
                self.fDeltaPressure = 1
            else:
                return 0
        else:
            oFlowIn, _ = self.getFlows()
            fFlowRate = oFlowIn.fFlowRate

        if abs(fFlowRate) > self.fMaxFlowRate:
            # Exceeding max flow rate; pump acts as resistance, producing a negative pressure rise.
            fDeltaPressure = self.fDeltaPressure - 100
        else:
            # Adjust delta pressure based on setpoint and current flow rate
            iChangeDir = 1 if self.fFlowRateSP * self.iDir > fFlowRate * self.iDir else -1
            rFactor = (self.fFlowRateSP - fFlowRate) / self.fFlowRateSP
            rFactor = min(max(rFactor, -2), 2)  # Limit rFactor to [-2, 2]
            fDeltaPressure = self.fDeltaPressure * (1 + rFactor * iChangeDir / self.fDampeningFactor)

        # Enforce delta pressure limits
        fDeltaPressure = max(min(fDeltaPressure, self.fMaxDeltaP), self.fMinDeltaP)

        self.fDeltaPressure = fDeltaPressure
        return fDeltaPressure

    def solverDeltas(self, fFlowRate):
        """
        Callback solver function to compute delta pressure.

        Args:
            fFlowRate: Current flow rate.

        Returns:
            fDeltaPressure: Computed delta pressure.
        """
        if not self.bActive:
            self.fHeatFlow = 0
            self.fDeltaPressure = 0
            return 0

        if abs(fFlowRate) > self.fMaxFlowRate:
            fDeltaPressure = self.fMaxDeltaP
        else:
            iChangeDir = 1 if self.fFlowRateSP * self.iDir > fFlowRate * self.iDir else -1
            rFactor = (self.fFlowRateSP - fFlowRate) / self.fFlowRateSP
            rFactor = min(max(rFactor, -2), 2)
            fDeltaPressure = self.fDeltaPressure * (1 + rFactor * iChangeDir / self.fDampeningFactor)

        # Enforce delta pressure limits
        fDeltaPressure = max(min(fDeltaPressure, self.fMaxDeltaP), -self.fMaxDeltaP)
        self.fDeltaPressure = fDeltaPressure
        return fDeltaPressure

    def changeSetpoint(self, fNewSetpoint):
        """
        Change the flow rate setpoint of the pump.

        Args:
            fNewSetpoint: New flow rate setpoint in kg/s.
        """
        self.fFlowRateSP = fNewSetpoint
        self.bActive = fNewSetpoint != 0
