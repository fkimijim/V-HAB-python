import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from capacity import Capacity

ThermalCapacity = Capacity()

class Flow(ThermalCapacity):
    """
    FLOW
    A capacity intended for use with flow matter phases modeled to not contain any mass.
    The capacity only consists of heat capacity flows, and changes in heat flow 
    directly impact the temperature of the capacity.
    """

    def __init__(self, oPhase, fTemperature):
        """
        Constructor for the Flow class.

        Args:
            oPhase (object): Phase object associated with the capacity.
            fTemperature (float): Initial temperature of the flow capacity.
        """
        super().__init__(oPhase, fTemperature, True)

    def update_temperature(self, _=None):
        """
        Updates the temperature of the flow capacity using heat flows and capacities.
        """

        # Getting the current time and calculating the last time step
        fTime = self.oTimer.fTime
        fLastStep = fTime - self.fLastTemperatureUpdate

        # Initializing arrays to store information from exmes
        afMatterFlowRate = [0] * self.iProcsEXME
        afSpecificHeatCapacity = [0] * self.iProcsEXME
        afTemperature = [0] * self.iProcsEXME

        # We cannot use the fCurrentHeatFlow property directly because it 
        # would contain mass-based heat flows, which are invalid for flow phases
        fSolverHeatFlow = 0

        # Looping through all thermal exmes
        for iExme in range(self.iProcsEXME):
            exme = self.aoExmes[iExme]

            if exme.oBranch.oHandler.bFluidicSolver:
                # Determining branch direction and corresponding indices
                if exme.oBranch.oMatterObject.coExmes[0].oPhase == self.oPhase:
                    iMatterExme, iOtherExme = 0, 1
                else:
                    iMatterExme, iOtherExme = 1, 0

                # Determining the flow rate and its direction
                fFlowRate = (
                    exme.oBranch.oMatterObject.fFlowRate *
                    exme.oBranch.oMatterObject.coExmes[iMatterExme].iSign
                )

                # Considering only inflows
                if fFlowRate > 0:
                    afMatterFlowRate[iExme] = fFlowRate
                    afSpecificHeatCapacity[iExme] = (
                        exme.oBranch.oMatterObject.coExmes[iOtherExme].oFlow.fSpecificHeatCapacity
                    )

                    # Obtaining the temperature from the thermal branch
                    if iMatterExme == 0:
                        afTemperature[iExme] = exme.oBranch.afTemperatures[0]
                    else:
                        afTemperature[iExme] = exme.oBranch.afTemperatures[-1]
            else:
                # Handling heat flow for non-fluidic solvers
                fSolverHeatFlow += exme.iSign * exme.fHeatFlow

        # Calculating overall heat capacity flow into the phase
        fOverallHeatCapacityFlow = sum(
            mf * shc for mf, shc in zip(afMatterFlowRate, afSpecificHeatCapacity)
        )

        # Trigger event if needed
        if self.bTriggerSetCalculateFlowConstantTemperatureCallbackBound:
            self.trigger("calculateFlowConstantTemperature")

        # If no inflow, maintain the previous temperature; otherwise, calculate the new temperature
        if fOverallHeatCapacityFlow == 0:
            fTemperatureNew = self.fTemperature
        else:
            # Summing up heat flows from sources
            fSourceHeatFlow = sum(source.fHeatFlow for source in self.coHeatSource)

            # Calculating the new temperature
            fTemperatureNew = (
                sum(mf * shc * temp for mf, shc, temp in zip(
                    afMatterFlowRate, afSpecificHeatCapacity, afTemperature
                )) / fOverallHeatCapacityFlow
            ) + (fSourceHeatFlow + fSolverHeatFlow) / fOverallHeatCapacityFlow

        # Updating properties
        self.fLastTemperatureUpdate = fTime
        self.fTemperatureUpdateTimeStep = fLastStep

        # Ensuring phase and capacity temperatures remain synchronized
        self.set_temperature(fTemperatureNew)

        # Updating specific heat capacity if heat capacity flow is nonzero
        if fOverallHeatCapacityFlow != 0:
            self.update_specific_heat_capacity()

        # Marking the capacity as outdated for the next time step
        self.set_outdated_ts()

        # Trigger post-update event if bound
        if self.bTriggerSetUpdateTemperaturePostCallbackBound:
            self.trigger("updateTemperature_post")

        self.bRegisteredTemperatureUpdated = False
