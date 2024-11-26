import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "base")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "event")))
from base import Base
from event.source import Source

EventSource = Source()

class Capacity(Base, EventSource):
    """
    A thermal capacity object that holds thermal energy and performs all thermal calculations for an associated phase.
    """

    def __init__(self, oPhase, fTemperature, bFlow=False):
        """
        Initialize a Capacity object.

        Args:
            oPhase: Associated phase object.
            fTemperature: Initial temperature of the capacity.
            bFlow: Boolean indicating if the capacity represents a flow.
        """
        super().__init__()

        # Basic properties
        self.bSynced = False
        self.fTemperature = fTemperature
        self.fSpecificHeatCapacity = 0  # [J/(K*kg)]
        self.fTotalHeatCapacity = 0  # [J/K]
        self.fTotalHeatSourceHeatFlow = 0  # [W]
        self.fCurrentHeatFlow = 0  # [W]
        self.sName = oPhase.sName
        self.bBoundary = False
        self.bFlow = bFlow

        # Associated objects
        self.oPhase = oPhase
        self.oContainer = oPhase.oStore.oContainer
        self.coHeatSource = []
        self.toHeatSources = {}
        self.iHeatSources = 0
        self.aoExmes = []
        self.toProcsEXME = {}
        self.iProcsEXME = 0
        self.oMT = oPhase.oMT
        self.oTimer = oPhase.oTimer

        # Numerical properties
        self.fTimeStep = None
        self.fLastTemperatureUpdate = -10
        self.fTemperatureUpdateTimeStep = None
        self.rMaxChange = 0.005
        self.fMinimumTemperatureForTimeStep = None
        self.fMaximumTemperatureForTimeStep = None
        self.fMaxTemperatureChange = np.inf
        self.fMaxStep = 60
        self.fMinStep = 1e-8
        self.fFixedTimeStep = None
        self.fLastSetOutdated = -1
        self.bRegisteredTemperatureUpdated = False
        self.fLastRegisteredTemperatureUpdated = -1
        self.fLastTotalHeatCapacityUpdate = 0

        # Heat capacity update-related properties
        self.fPressureLastHeatCapacityUpdate = None
        self.fTemperatureLastHeatCapacityUpdate = None
        self.arPartialMassLastHeatCapacityUpdate = None

        # Callback bindings
        self.bTriggerSetCalculateHeatsourcePreCallbackBound = False
        self.bTriggerSetUpdateTemperaturePostCallbackBound = False
        self.bTriggerSetCalculateFlowConstantTemperatureCallbackBound = False

        # Add capacity to container and phase
        self.oContainer.add_capacity(self)
        self.oPhase.set_capacity(self)

        # Initialize heat capacity
        self._initialize_heat_capacity()

    def _initialize_heat_capacity(self):
        """
        Initialize specific and total heat capacities.
        """
        try:
            self.fSpecificHeatCapacity = self.oMT.calculate_specific_heat_capacity(self.oPhase)
            self.fTotalHeatCapacity = sum(self.oPhase.afMass) * self.fSpecificHeatCapacity
        except Exception:
            self.fSpecificHeatCapacity = 1000  # Default value
            self.fTotalHeatCapacity = sum(self.oPhase.afMass) * self.fSpecificHeatCapacity

    def update_specific_heat_capacity(self):
        """
        Update the specific heat capacity based on the current phase properties.
        """
        if (self.fPressureLastHeatCapacityUpdate is None or
                abs(self.fPressureLastHeatCapacityUpdate - self.oPhase.fPressure) > 100 or
                abs(self.fTemperatureLastHeatCapacityUpdate - self.fTemperature) > 1 or
                max(abs(self.arPartialMassLastHeatCapacityUpdate - self.oPhase.arPartialMass)) > 0.01):
            self.fSpecificHeatCapacity = self.oMT.calculate_specific_heat_capacity(self.oPhase)
            self.fPressureLastHeatCapacityUpdate = self.oPhase.fPressure
            self.fTemperatureLastHeatCapacityUpdate = self.fTemperature
            self.arPartialMassLastHeatCapacityUpdate = self.oPhase.arPartialMass

    def set_total_heat_capacity(self, fTotalHeatCapacity):
        """
        Set the total heat capacity of this capacity object.
        """
        if not self.bBoundary:
            self.fTotalHeatCapacity = fTotalHeatCapacity
        self.fLastTotalHeatCapacityUpdate = self.oTimer.fTime

    def set_specific_heat_capacity(self, fSpecificHeatCapacity):
        """
        Set the specific heat capacity and update the total heat capacity accordingly.
        """
        if self.oPhase.bFlow:
            # Handle flow phases
            flow_rates = [exme.oBranch.oMatterObject.fFlowRate * exme.iSign for exme in self.aoExmes]
            specific_heat_capacities = [
                exme.oBranch.oMatterObject.calculate_specific_heat_capacity()
                for exme in self.aoExmes
            ]
            if sum(flow_rates) != 0:
                self.fSpecificHeatCapacity = sum(
                    fr * shc for fr, shc in zip(flow_rates, specific_heat_capacities)
                ) / sum(flow_rates)
        else:
            self.fSpecificHeatCapacity = fSpecificHeatCapacity
            self.set_total_heat_capacity(self.oPhase.fMass * fSpecificHeatCapacity)

    def add_proc_exme(self, oProcEXME):
        """
        Add an EXME processor to this capacity.
        """
        if self.oContainer.bThermalSealed:
            raise Exception("Cannot add EXME to a sealed container.")
        if oProcEXME.sName in self.toProcsEXME:
            raise Exception(f"EXME {oProcEXME.sName} already exists.")
        self.toProcsEXME[oProcEXME.sName] = oProcEXME
        self.aoExmes.append(oProcEXME)
        self.iProcsEXME += 1

    def update_temperature(self):
        """
        Update the temperature of this capacity based on the current heat flow.
        """
        fTime = self.oTimer.fTime
        fLastStep = fTime - self.fLastTemperatureUpdate
        if fLastStep == 0:
            return

        if self.fTotalHeatCapacity <= 1e-15:
            fTemperatureNew = 293  # Default temperature
        else:
            fTemperatureNew = self.fTemperature + (
                (self.fCurrentHeatFlow / self.fTotalHeatCapacity) * fLastStep
            )

        self.fLastTemperatureUpdate = fTime
        self.fTemperatureUpdateTimeStep = fLastStep
        self.set_temperature(fTemperatureNew)
        self.update_specific_heat_capacity()

    def set_temperature(self, fTemperature):
        """
        Set the temperature of this capacity and synchronize with the associated phase.
        """
        self.fTemperature = fTemperature
        self.oPhase.set_temperature(fTemperature)
