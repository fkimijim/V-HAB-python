import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.f2f import f2f
from lib.functions.calculateDeltaPressure.Pipe import Pipe

f2f = f2f()

class Pipe(f2f):
    """
    Pipe class representing a fluid transport pipe with pressure drop calculations.
    """

    # Constants
    Const = {
        "fReynoldsCritical": 2320,  # Critical Reynolds number
    }

    def __init__(self, oContainer, sName, fLength, fDiameter, fRoughness=0):
        super().__init__(oContainer, sName)

        self.fLength = fLength
        self.fDiameter = fDiameter
        self.fRoughness = fRoughness

        self.fDropCoefficient = 0
        self.fTimeOfLastUpdate = -1
        self.fDynamicViscosity = 17.2e-6
        self.rMaxChange = 0.01

        self.fTemperatureLastUpdate = 0
        self.fPressureLastUpdate = 0

        self.supportSolver("hydraulic", fDiameter, fLength)
        self.supportSolver("callback", self.solverDeltas)
        self.supportSolver("manual", False)
        self.supportSolver("coefficient", self.calculatePressureDropCoefficient)

    def update(self):
        """
        Update function for the hydraulic solver.
        """
        bZeroFlows = any(flow.fFlowRate == 0 for flow in self.aoFlows)
        if bZeroFlows:
            return

        oFlowIn, _ = self.getFlows()

        fDensity = self.oMT.calculateDensity(oFlowIn)
        if self.oTimer.fTime > self.fTimeOfLastUpdate:
            self.fDynamicViscosity = self.oMT.calculateDynamicViscosity(oFlowIn)

        fFlowSpeed = oFlowIn.fFlowRate / (fDensity * (3.14159 * 0.25 * self.fDiameter**2))
        self.fDeltaPressure = Pipe(
            self.fDiameter,
            self.fLength,
            fFlowSpeed,
            self.fDynamicViscosity,
            fDensity,
            self.fRoughness,
            0,
        )

        self.fTimeOfLastUpdate = self.oTimer.fTime

    def calculatePressureDropCoefficient(self, _):
        """
        Calculate the pressure drop coefficient for laminar flow.
        """
        _ = self.solverDeltas(self.aoFlows[0].fFlowRate)
        self.fTimeOfLastUpdate = self.oTimer.fTime
        return self.fDropCoefficient

    def solverDeltas(self, fFlowRate):
        """
        Calculate the pressure drop for the given flow rate.
        """
        if fFlowRate == 0:
            return 0

        oFlowIn, oFlowOut = self.getFlows(fFlowRate)
        iInExme = 1 if fFlowRate >= 0 else 2

        try:
            fDensityIn = oFlowIn.getDensity()
            fDensityOut = oFlowOut.getDensity()
            fDensity = (fDensityIn + fDensityOut) / 2
        except Exception:
            fDensity = self.oBranch.coExmes[iInExme].oPhase.fDensity

        fFlowSpeed = abs(fFlowRate) / ((3.14159 / 4) * self.fDiameter**2 * fDensity)

        if self.oBranch.fFlowRate != 0:
            try:
                if self.oTimer.fTime > self.fTimeOfLastUpdate:
                    rTemperatureChange = abs(
                        1 - self.fTemperatureLastUpdate / oFlowIn.fTemperature
                    )
                    rPressureChange = abs(
                        1 - self.fPressureLastUpdate / oFlowIn.fPressure
                    )
                    if rTemperatureChange > self.rMaxChange or rPressureChange > self.rMaxChange:
                        self.fDynamicViscosity = oFlowIn.getDynamicViscosity()
                        self.fTemperatureLastUpdate = oFlowIn.fTemperature
                        self.fPressureLastUpdate = oFlowIn.fPressure
            except Exception:
                self.fDynamicViscosity = 17.2e-6
                if not base.oDebug.bOff:
                    self.out(
                        3,
                        1,
                        "dynamic-viscosity-fall-back",
                        f"Error calculating dynamic viscosity in pipe ({self.oBranch.sName} - {self.sName}). Using default value instead: {self.fDynamicViscosity} [Pa s].",
                    )
        else:
            self.fDynamicViscosity = 17.2e-6

        if self.fDiameter == 0:
            return float("inf")

        if fDensity == 0 or self.fDynamicViscosity == 0:
            return 0

        self.fDeltaPressure = Pipe(
            self.fDiameter,
            self.fLength,
            fFlowSpeed,
            self.fDynamicViscosity,
            fDensity,
            self.fRoughness,
            0,
        )
        self.fDropCoefficient = self.fDeltaPressure / (fFlowSpeed * 3.14159 * 0.25 * self.fDiameter**2)
        return self.fDeltaPressure
