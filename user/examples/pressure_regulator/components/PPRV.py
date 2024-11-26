import numpy as np
from math import cos, radians

class PPRV:
    """
    PPRV - Pressure Relief Valve class
    """

    def __init__(self, oParent, sName, fDeltaPressureMaxValve, fThetaCone, fHeightCone,
                 fCSpring, fXSetpoint, fMaxValveOpening, fAreaDiaphragm, fMassDiaphragm, fTPT1, bChangeSetpoint):
        """
        Valve Constructor
        """
        self.oParent = oParent
        self.sName = sName

        # Initialize properties
        self.fDeltaPressureMaxValve = fDeltaPressureMaxValve
        self.fThetaCone = fThetaCone
        self.fHeightCone = fHeightCone
        self.fCSpring = fCSpring
        self.fXSetpoint = fXSetpoint
        self.fMaxValveOpening = fMaxValveOpening
        self.fAreaDiaphragm = fAreaDiaphragm
        self.fMassDiaphragm = fMassDiaphragm
        self.fTPT1 = fTPT1
        self.bChangeSetpoint = bChangeSetpoint

        # Additional initializations
        self.bActive = True
        self.fSpringCoeff = self.fDeltaPressureMaxValve * self.fAreaDiaphragm
        self.fHydrDiam = 0
        self.fHydrLength = self.fHeightCone / cos(radians(self.fThetaCone / 2))
        self.fDeltaTemp = 0
        self.fTimeStep = 0
        self.fTimeOld = 0

        # State-space matrices
        self.afSSM_VectorXOld = np.zeros(2)
        self.afSSM_VectorXNew = np.zeros(2)
        self.afSSM_VectorU = np.zeros(3)
        self.mfSSM_MatrixA = np.array([[1, 0], [0, -1]])
        self.mfSSM_MatrixB = np.zeros((2, 3))
        self.mfSSM_MatrixE = np.eye(2)

        # Solver support
        self.support_solver("hydraulic", self.fHydrDiam, self.fHydrLength, True, self.update)
        self.support_solver("callback", self.solver_deltas)

    def support_solver(self, solver_type, *args):
        """
        Stub method for solver support.
        """
        pass

    def set_environment_reference(self, oGasPhaseEnvRef):
        """
        Set environment reference phase.
        """
        self.oGasPhaseEnvRef = oGasPhaseEnvRef

    def delta_x(self, fPressureChamber):
        """
        Calculate valve dislocation.
        """
        fPressureReference = self.oGasPhaseEnvRef.fMass * self.oGasPhaseEnvRef.fMassToPressure
        self.afSSM_VectorU = [fPressureChamber, fPressureReference, self.fSpringCoeff]

        self.mfSSM_MatrixB[1, :] = [
            (self.fAreaDiaphragm * self.fTimeStep) / self.fMassDiaphragm,
            -(self.fAreaDiaphragm * self.fTimeStep) / self.fMassDiaphragm,
            -self.fTimeStep / self.fMassDiaphragm
        ]
        self.mfSSM_MatrixE[1, 0] = (self.fCSpring * self.fTimeStep) / self.fMassDiaphragm
        self.mfSSM_MatrixE[0, 1] = -self.fTimeStep

        # Solve implicit linear equation system E*x_n+1 = A*x_n + B*u
        self.afSSM_VectorXNew = np.linalg.solve(
            self.mfSSM_MatrixE,
            np.dot(self.mfSSM_MatrixA, self.afSSM_VectorXOld) +
            np.dot(self.mfSSM_MatrixB, self.afSSM_VectorU)
        )

        # Apply physical constraints
        self.afSSM_VectorXNew[0] = max(0, min(self.afSSM_VectorXNew[0], self.fMaxValveOpening))
        if self.afSSM_VectorXNew[0] == 0 and self.afSSM_VectorXNew[1] < 0:
            self.afSSM_VectorXNew[1] = 0

        # Update state vector for the next iteration
        self.afSSM_VectorXOld = self.afSSM_VectorXNew

    def hydr_diam(self):
        """
        Calculate hydraulic diameter.
        """
        self.fHydrDiam = max(0, 2 * self.afSSM_VectorXNew[0])

    def update(self):
        """
        Update parameters during simulation.
        """
        self.fTimeStep = self.oBranch.oContainer.oTimer.fTime - self.fTimeOld
        oPhase = self.oBranch.coExmes[0].oPhase
        fChamberPressure = oPhase.fMass * oPhase.fMassToPressure

        # Update valve state and hydraulic diameter
        self.delta_x(fChamberPressure)
        self.hydr_diam()

        # Save current time for the next timestep
        self.fTimeOld = self.oBranch.oContainer.oTimer.fTime

        # Adjust diaphragm mass based on valve displacement
        if self.afSSM_VectorXNew[0] > self.fMaxValveOpening * 0.01:
            self.fMassDiaphragm = 0.0079 * 2
        else:
            self.fMassDiaphragm = 0.0079

        self.toSolve.hydraulic.fHydrDiam = self.fHydrDiam

    def solver_deltas(self, fFlowRate):
        """
        Calculate pressure difference for the given flow rate.
        """
        self.update()

        fCoeff = self.fHydrDiam * 0.00000133 * 20 / self.fHydrLength
        oPhaseLeft = self.oBranch.coExmes[0].oPhase
        fChamberPressureLeft = oPhaseLeft.fMass * oPhaseLeft.fMassToPressure
        oPhaseRight = self.oBranch.coExmes[1].oPhase
        fChamberPressureRight = oPhaseRight.fMass * oPhaseRight.fMassToPressure

        fTargetFlowRate = fCoeff * (fChamberPressureLeft - fChamberPressureRight)
        fDeltaPressure = (fFlowRate / fTargetFlowRate) * (fChamberPressureLeft - fChamberPressureRight)

        return fDeltaPressure
