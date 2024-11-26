import numpy as np
from math import sin, cos, radians

class Valve:
    def __init__(self, oParent, sName, tParameters):
        # Initialize public properties
        self.fMaximumDeltaPressure = tParameters.get("fMaximumDeltaPressure", 56500)  # [Pa]
        self.fThetaCone = tParameters.get("fThetaCone", 60)  # [deg]
        self.fHeightCone = tParameters.get("fHeightCone", 0.05)  # [m]
        self.fCSpring = tParameters.get("fCSpring", 22187)  # [N/m]
        self.fXSetpoint = 0  # [m]
        self.fPressureSetpoint = tParameters.get("fPressureSetpoint", 28300)  # [Pa]
        self.fMaxValveOpening = tParameters.get("fMaxValveOpening", 0.04)  # [m]
        self.fAreaDiaphragm = tParameters.get("fAreaDiaphragm", 0.0079)  # [m^2]
        self.fMassDiaphragm = tParameters.get("fMassDiaphragm", 0.01)  # [kg]
        self.fElapsedTime = 0  # [s]
        self.fTimeOld = 0  # [s]
        self.fChangeSetpointInterval = 10  # [s]
        self.iI = 1  # [-]
        self.bChangeSetpoint = True  # [-]
        
        # State space system variables
        self.afSSM_VectorXOld = np.zeros(3)
        self.afSSM_VectorXNew = np.zeros(3)
        self.afSSM_VectorU = np.zeros(3)
        self.mfSSM_MatrixA = np.zeros((3, 3))
        self.mfSSM_MatrixB = np.zeros((3, 3))
        self.mfSSM_MatrixE = np.zeros((3, 3))
        self.fTPT1 = tParameters.get("fTPT1", 0.02)  # [s]
        
        # Environment reference phase
        self.oGasPhaseEnvRef = None
        
        # Solver properties
        self.fHydrDiam = 0.0001
        self.fHydrLength = self.fHeightCone / cos(radians(self.fThetaCone / 2))
        self.fDeltaTemp = 0
        
        # Initialize XSetpoint
        if self.fPressureSetpoint <= self.fMaximumDeltaPressure:
            self.fXSetpoint = (self.fPressureSetpoint * self.fAreaDiaphragm) / self.fCSpring
        
        # Initialize matrices for the state-space model
        self.mfSSM_MatrixA[0, 0] = 1
        self.mfSSM_MatrixA[1, 1] = 1
        self.mfSSM_MatrixE[0, 0] = 1
        self.mfSSM_MatrixE[1, 1] = 1
        self.mfSSM_MatrixE[2, 2] = 1

    def set_environment_reference(self, oGasPhaseEnvRef):
        self.oGasPhaseEnvRef = oGasPhaseEnvRef

    def delta_x(self, fPressureChamber):
        fPressureReference = self.oGasPhaseEnvRef.fMass * self.oGasPhaseEnvRef.fMassToPressure
        self.afSSM_VectorU = np.array([fPressureReference, fPressureChamber, self.fXSetpoint])
        
        self.mfSSM_MatrixA[2, 2] = self.fTPT1 / (self.fTPT1 + self.fElapsedTime)
        
        self.mfSSM_MatrixB[1, :] = [
            (self.fAreaDiaphragm * self.fElapsedTime) / self.fMassDiaphragm,
            -(self.fAreaDiaphragm * self.fElapsedTime) / self.fMassDiaphragm,
            (self.fCSpring * self.fElapsedTime) / self.fMassDiaphragm
        ]
        
        self.mfSSM_MatrixE[1, 0] = (self.fCSpring * self.fElapsedTime) / self.fMassDiaphragm
        self.mfSSM_MatrixE[0, 1] = -self.fElapsedTime
        self.mfSSM_MatrixE[2, 0] = -(1 / ((self.fTPT1 / self.fElapsedTime) + 1))
        
        self.afSSM_VectorXNew = np.linalg.solve(self.mfSSM_MatrixE, 
                                                self.mfSSM_MatrixA @ self.afSSM_VectorXOld + 
                                                self.mfSSM_MatrixB @ self.afSSM_VectorU)
        
        if self.afSSM_VectorXNew[2] < 0:
            self.afSSM_VectorXNew[2] = 0
        if self.afSSM_VectorXNew[2] > self.fMaxValveOpening:
            self.afSSM_VectorXNew[2] = self.fMaxValveOpening
        if self.afSSM_VectorXNew[2] == 0 and self.afSSM_VectorXNew[1] < 0:
            self.afSSM_VectorXNew[1] = 0
        
        self.afSSM_VectorXNew[0] = self.afSSM_VectorXNew[2]
        self.afSSM_VectorXOld = self.afSSM_VectorXNew

    def hydr_diam(self):
        fDistanceCones = self.afSSM_VectorXNew[2] * sin(radians(self.fThetaCone / 2))
        fDistanceCones = max(fDistanceCones, 0)
        self.fHydrDiam = 2 * fDistanceCones
        if self.fHydrDiam < 0:
            self.fHydrDiam = 0

    def update(self):
        if not self.oGasPhaseEnvRef:  # Inactive valve
            self.fHydrDiam = 0
            return
        
        self.fElapsedTime = self.oGasPhaseEnvRef.timer.fTime - self.fTimeOld
        if self.fElapsedTime <= 0:
            return
        
        oPhaseLeft = self.oGasPhaseEnvRef.left_phase
        fChamberPressureLeft = oPhaseLeft.fMass * oPhaseLeft.fMassToPressure
        oPhaseRight = self.oGasPhaseEnvRef.right_phase
        fChamberPressureRight = oPhaseRight.fMass * oPhaseRight.fMassToPressure
        
        fChamberPressure = min(fChamberPressureLeft, fChamberPressureRight)
        self.delta_x(fChamberPressure)
        self.hydr_diam()
        self.fTimeOld = self.oGasPhaseEnvRef.timer.fTime

    def solver_deltas(self, fFlowRate):
        self.update()
        fCoeff = self.fHydrDiam * 0.00000133 * 20 / self.fHydrLength
        
        oPhaseLeft = self.oGasPhaseEnvRef.left_phase
        fChamberPressureLeft = oPhaseLeft.fMass * oPhaseLeft.fMassToPressure
        oPhaseRight = self.oGasPhaseEnvRef.right_phase
        fChamberPressureRight = oPhaseRight.fMass * oPhaseRight.fMassToPressure
        
        fTargetFlowRate = fCoeff * (fChamberPressureLeft - fChamberPressureRight)
        return (fFlowRate / fTargetFlowRate) * (fChamberPressureLeft - fChamberPressureRight)

    def change_setpoint(self, fPressureSetpoint):
        self.fPressureSetpoint = fPressureSetpoint
        self.fXSetpoint = (fPressureSetpoint * self.fAreaDiaphragm) / self.fCSpring
