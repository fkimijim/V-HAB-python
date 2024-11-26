import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.p2ps.stationary.stationary import StationaryP2P

StationaryP2P = StationaryP2P()

class Filter(StationaryP2P):
    """
    Filter for the CAMRAS CO2 absorption subsystem.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sType, fCycleTime, fVacuumTime, fPressureCompensationTime, sCase):
        """
        Initialize the filter.

        :param oStore: The store the filter belongs to.
        :param sName: Name of the filter.
        :param sPhaseIn: Phase input.
        :param sPhaseOut: Phase output.
        :param sType: Type of filter ('CO2' or 'H2O').
        :param fCycleTime: Total cycle time for adsorption/desorption.
        :param fVacuumTime: Time to create vacuum during desorption.
        :param fPressureCompensationTime: Time to equalize pressure.
        :param sCase: Case type (e.g., 'nominal', 'exercise', 'sleep').
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

        self.sType = sType
        self.fCycleTime = fCycleTime
        self.fVacuumTime = fVacuumTime
        self.sCase = sCase
        self.fPressureCompensationTime = fPressureCompensationTime

        self.sSpecies = None
        self.arExtractPartials = None

        if sType == "CO2":
            self.arExtractPartials = [0] * self.oMT.iSubstances
            self.arExtractPartials[self.oMT.tiN2I['CO2']] = 1
            self.sSpecies = "CO2"
        elif sType == "H2O":
            self.arExtractPartials = [0] * self.oMT.iSubstances
            self.arExtractPartials[self.oMT.tiN2I['H2O']] = 1
            self.sSpecies = "H2O"
        else:
            raise ValueError(
                "No data available for the specified filter type. Add the required data and filter type to enable calculations."
            )

        # Initialize properties
        self.fFlowRateFilter = 0
        self.sFilterMode = None
        self.fEfficiency = 0
        self.fEfficiencyAveraged = 0
        self.fMassRatioSpecies = 0
        self.fDesorbMass = 0
        self.fLastExec = 0
        self.fInternalTime = 0
        self.iOn = 0
        self.iOff = 0

    def setCycleTime(self, fCycleTime):
        self.fCycleTime = fCycleTime

    def setCase(self, sCase):
        self.sCase = sCase

    def setOn(self):
        self.iOff = 0

    def setOff(self):
        self.iOff = 1

    def setFilterMode(self, sFilterMode):
        """
        Set the filter mode to 'absorb' or 'desorb'.
        """
        self.sFilterMode = sFilterMode

    def update(self):
        """
        Update the filter state and processing logic.
        """
        # Update internal time and cycle time
        self.fInternalTime = self.oStore.oContainer.fInternalTime
        fCurrentCycleTime = self.fInternalTime % self.fCycleTime

        # Get species index
        iSpecies = self.oMT.tiN2I[self.sSpecies]

        # Calculate the time step
        fTimeStep = self.oStore.oTimer.fTime - self.fLastExec
        if fTimeStep <= 0:
            return

        # System is off, no processing occurs
        if self.oStore.oContainer.fFlowrateMain == 0:
            self.fFlowRateFilter = 0
            self.setMatterProperties(self.fFlowRateFilter, self.arExtractPartials)
            return

        # Pressure compensation phase
        if fCurrentCycleTime < self.fPressureCompensationTime:
            self.fEfficiencyAveraged = float('nan')
            self.fEfficiency = float('nan')
            self.fFlowRateFilter = 0
            self.setMatterProperties(self.fFlowRateFilter, self.arExtractPartials)
            return

        # Get inflow rates and mass ratios
        afFlowRate, mrPartials = self.getInFlows()
        if afFlowRate:
            afFlowRateSpecies = [flow * partials[iSpecies] for flow, partials in zip(afFlowRate, mrPartials)]
            fFlowRateSpecies = sum(afFlowRateSpecies)
            fFlowRateTotal = sum(afFlowRate)
            self.fMassRatioSpecies = fFlowRateSpecies / fFlowRateTotal
        else:
            fFlowRateSpecies = 0

        # Process based on filter mode
        if self.sFilterMode == "absorb":
            self._process_absorption(fFlowRateSpecies, fCurrentCycleTime)
        elif self.sFilterMode == "desorb":
            self._process_desorption(iSpecies, fCurrentCycleTime, fTimeStep)

        # Set filter properties
        self.setMatterProperties(self.fFlowRateFilter, self.arExtractPartials)
        self.fLastExec = self.oStore.oTimer.fTime

    def _process_absorption(self, fFlowRateSpecies, fCurrentCycleTime):
        """
        Handle absorption mode logic.
        """
        # Efficiency curves
        if self.sType == "CO2":
            if self.sCase == "nominal":
                self.fEfficiencyAveraged = (-105.26 * self.fMassRatioSpecies + 86.121) / 100
            elif self.sCase == "exercise":
                self.fEfficiencyAveraged = (-5690.5 * self.fMassRatioSpecies + 90.067) / 100
            elif self.sCase == "sleep":
                self.fEfficiencyAveraged = (284.45 * self.fMassRatioSpecies + 88.173) / 100
            elif self.sCase == "off":
                self.fEfficiencyAveraged = 0
        elif self.sType == "H2O":
            if self.sCase == "nominal":
                self.fEfficiencyAveraged = (1000 * self.fMassRatioSpecies + 87.2) / 100
            elif self.sCase == "exercise":
                self.fEfficiencyAveraged = (490.12 * self.fMassRatioSpecies + 83.895) / 100
            elif self.sCase == "sleep":
                self.fEfficiencyAveraged = (1049.5 * self.fMassRatioSpecies + 88.936) / 100
            elif self.sCase == "off":
                self.fEfficiencyAveraged = 0

        # Account for degradation
        fDegrad = self._calculate_degradation(fCurrentCycleTime)
        self.fEfficiency = fDegrad * self.fEfficiencyAveraged
        self.fEfficiency = max(0, min(1, self.fEfficiency))

        # Calculate flow rate for absorption
        self.fFlowRateFilter = self.fEfficiency * fFlowRateSpecies
        self.fDesorbMass = 0

    def _process_desorption(self, iSpecies, fCurrentCycleTime, fTimeStep):
        """
        Handle desorption mode logic.
        """
        if self.oOut.oPhase.afMass[iSpecies] > self.fDesorbMass:
            self.fDesorbMass = self.oOut.oPhase.afMass[iSpecies]

        if fCurrentCycleTime > (self.fVacuumTime + self.fPressureCompensationTime):
            fEfficiencyFactor = (
                2.985
                * (1 - (fCurrentCycleTime - (self.fVacuumTime + self.fPressureCompensationTime)) ** 0.5)
                / (self.fCycleTime - (self.fVacuumTime + self.fPressureCompensationTime)) ** 0.5
            )
            self.fFlowRateFilter = (
                -1 * (self.fDesorbMass - 0.002) / (self.fCycleTime - (self.fVacuumTime + self.fPressureCompensationTime))
            ) * fEfficiencyFactor

            if self.oOut.oPhase.afMass[iSpecies] < 0.002:
                self.fFlowRateFilter = 0
        else:
            self.fFlowRateFilter = 0

        # Ensure flow rate does not exceed available mass
        fAvailableMassFlow = self.oOut.oPhase.afMass[self.arExtractPartials != 0] / fTimeStep
        self.fFlowRateFilter = min(self.fFlowRateFilter, fAvailableMassFlow)

    def _calculate_degradation(self, fCurrentCycleTime):
        """
        Calculate degradation over cycle time.
        """
        if self.sType == "CO2":
            return -0.6 / (self.fCycleTime - self.fPressureCompensationTime) * (
                fCurrentCycleTime - self.fPressureCompensationTime
            ) + 1.3
        elif self.sType == "H2O":
            return -0.3 / (self.fCycleTime - self.fPressureCompensationTime) * (
                fCurrentCycleTime - self.fPressureCompensationTime
            ) + 1.15
        return 1
