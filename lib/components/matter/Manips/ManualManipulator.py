class ManualManipulator:
    """
    This manipulator allows the user to define desired flow rates using the setFlowRate function.
    It ensures that the flow rates add up to zero and adjusts if necessary.
    """

    def __init__(self, oParent, sName, oPhase, bAutoAdjustFlowRates=False):
        """
        Initialize the ManualManipulator.

        Args:
            oParent: The parent system reference.
            sName: Name of the manipulator.
            oPhase: The phase the manipulator belongs to.
            bAutoAdjustFlowRates: Whether to always auto-adjust flow rates.
        """
        self.oParent = oParent
        self.sName = sName
        self.oPhase = oPhase
        self.bAlwaysAutoAdjustFlowRates = bAutoAdjustFlowRates

        # Properties
        self.afManualFlowRates = [0] * oPhase.oMT.iSubstances  # [kg/s]
        self.aarManualFlowsToCompound = [[0] * oPhase.oMT.iSubstances for _ in range(oPhase.oMT.iSubstances)]
        self.bMassTransferActive = False
        self.fMassTransferStartTime = None
        self.fMassTransferTime = None
        self.fMassTransferFinishTime = None

        # Timer binding for mass transfer checks
        self.setMassTransferTimeStep = self.oPhase.oTimer.bind(self.checkMassTransfer, 0)
        self.setMassTransferTimeStep(float('inf'), True)

    def setFlowRate(self, afFlowRates, aarFlowsToCompound=None, bAutoAdjustFlowRates=None):
        """
        Set flow rates for the manipulator.

        Args:
            afFlowRates: List of flow rates for each substance [kg/s].
            aarFlowsToCompound: Matrix for flows to compound.
            bAutoAdjustFlowRates: Whether to auto-adjust flow rates.
        """
        if bAutoAdjustFlowRates is None:
            bAutoAdjustFlowRates = self.bAlwaysAutoAdjustFlowRates

        if self.bMassTransferActive:
            print("Warning: A mass transfer is currently in progress.")

        # Check and adjust flow rates if necessary
        fError = sum(afFlowRates)
        if abs(fError) > 1e-6:
            if bAutoAdjustFlowRates:
                fPositiveFlowRate = sum(flow for flow in afFlowRates if flow > 0)
                fNegativeFlowRate = abs(sum(flow for flow in afFlowRates if flow < 0))

                if fPositiveFlowRate > fNegativeFlowRate:
                    fDifference = fPositiveFlowRate - fNegativeFlowRate
                    arRatios = [flow / fPositiveFlowRate for flow in afFlowRates if flow > 0]
                    for i, flow in enumerate(afFlowRates):
                        if flow > 0:
                            afFlowRates[i] -= fDifference * arRatios.pop(0)
                else:
                    fDifference = fNegativeFlowRate - fPositiveFlowRate
                    arRatios = [abs(flow) / fNegativeFlowRate for flow in afFlowRates if flow < 0]
                    for i, flow in enumerate(afFlowRates):
                        if flow < 0:
                            afFlowRates[i] += fDifference * arRatios.pop(0)
            else:
                raise ValueError("Flow rates do not sum to zero and auto-adjustment is disabled.")

        self.afManualFlowRates = afFlowRates
        if aarFlowsToCompound:
            self.aarManualFlowsToCompound = aarFlowsToCompound
        else:
            self.aarManualFlowsToCompound = [[0] * self.oPhase.oMT.iSubstances for _ in range(self.oPhase.oMT.iSubstances)]

        # Trigger phase mass update
        self.oPhase.registerMassupdate()

    def setMassTransfer(self, afPartialMasses, fTime, aarFlowsToCompound=None):
        """
        Set a specific mass transfer over a given time.

        Args:
            afPartialMasses: List of partial masses [kg].
            fTime: Time over which the transfer occurs [s].
            aarFlowsToCompound: Matrix for flows to compound.
        """
        if fTime <= 0:
            raise ValueError("Time for mass transfer must be greater than zero.")

        if self.bMassTransferActive:
            print("Warning: A mass transfer is currently in progress.")

        self.bMassTransferActive = True
        self.fMassTransferStartTime = self.oPhase.oTimer.fTime
        self.fMassTransferTime = fTime
        self.fMassTransferFinishTime = self.fMassTransferStartTime + fTime

        self.afManualFlowRates = [mass / fTime for mass in afPartialMasses]
        self.setMassTransferTimeStep(fTime, True)

        if aarFlowsToCompound:
            self.aarManualFlowsToCompound = aarFlowsToCompound
        else:
            self.aarManualFlowsToCompound = [[0] * self.oPhase.oMT.iSubstances for _ in range(self.oPhase.oMT.iSubstances)]

        # Trigger phase mass update
        self.oPhase.registerMassupdate()

    def checkMassTransfer(self):
        """
        Check and update the mass transfer progress.
        """
        if self.bMassTransferActive:
            remaining_time = self.fMassTransferFinishTime - self.oPhase.oTimer.fTime
            if remaining_time < self.oPhase.oTimer.fMinimumTimeStep:
                # End mass transfer
                self.afManualFlowRates = [0] * self.oPhase.oMT.iSubstances
                self.aarManualFlowsToCompound = [[0] * self.oPhase.oMT.iSubstances for _ in range(self.oPhase.oMT.iSubstances)]
                self.bMassTransferActive = False
                self.setMassTransferTimeStep(float('inf'), True)
                self.oPhase.registerMassupdate()
            else:
                # Update time step
                self.setMassTransferTimeStep(remaining_time, True)

    def update(self):
        """
        Update the flow rates for the manipulator.
        """
        self.oPhase.update_substance_flow(self.afManualFlowRates, self.aarManualFlowsToCompound)
