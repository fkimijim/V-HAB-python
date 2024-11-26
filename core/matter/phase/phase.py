from abc import ABC, abstractmethod
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "store")))
from store import Store

Store = Store()

class Phase(ABC):
    """
    Phase with isotropic properties (abstract class).
    Represents a matter phase with homogeneous mass distribution.
    Should be subclassed for specific types (e.g., gas, liquid).
    """

    sObjectType = 'phase'  # Object type identifier for all derived classes

    @abstractmethod
    def __init__(self, oStore, sName, tfMass=None, fTemperature=None):
        """
        Phase Class Constructor.
        Initializes properties and validates input parameters.
        """
        if not isinstance(oStore, Store):
            raise ValueError("oStore must be an instance of Store.")

        self.sName = sName
        self.oStore = oStore
        self.oStore.add_phase(self)

        self.oMT = oStore.oMT
        self.oTimer = oStore.oTimer

        self.afMass = [0] * self.oMT.iSubstances
        self.arPartialMass = [0] * self.oMT.iSubstances
        self.arCompoundMass = [[0] * self.oMT.iSubstances for _ in range(self.oMT.iSubstances)]
        self.arInFlowCompoundMass = [[0] * self.oMT.iSubstances for _ in range(self.oMT.iSubstances)]
        self.afEmptyCompoundMassArray = [[0] * self.oMT.iSubstances for _ in range(self.oMT.iSubstances)]
        self.fMinStep = self.oTimer.fMinimumTimeStep

        if tfMass and isinstance(tfMass, dict):
            if not fTemperature or fTemperature <= 0:
                raise ValueError("fTemperature must be provided and greater than zero when tfMass is specified.")

            self._initialize_mass(tfMass)
            self.set_temperature(fTemperature)
        else:
            self.fMass = 0
            self.arPartialMass = self.afMass

            self.set_temperature(self.oMT.Standard.Temperature)

        self.fMolarMass = self.oMT.calculate_molar_mass(self.afMass)
        self.fMass = sum(self.afMass)
        self.afMassGenerated = [0] * self.oMT.iSubstances
        self.fMassToPressure = 0  # Will be set later

        self.fMassLastUpdate = 0
        self.afMassLastUpdate = [0] * self.oMT.iSubstances

        self.hBindPostTickMassUpdate = self.oTimer.register_post_tick(self.massupdate, 'matter', 'phase_massupdate')
        self.hBindPostTickUpdate = self.oTimer.register_post_tick(self.update, 'matter', 'phase_update')
        self.hBindPostTickTimeStep = self.oTimer.register_post_tick(self.calculate_time_step, 'post_physics', 'timestep')

    def _initialize_mass(self, tfMass):
        """
        Initializes the mass properties based on the input mass dictionary.
        """
        for substance, mass in tfMass.items():
            if substance not in self.oMT.tiN2I:
                raise ValueError(f"Substance {substance} not recognized in matter table.")
            idx = self.oMT.tiN2I[substance]
            self.afMass[idx] = mass

            if self.oMT.abCompound[idx]:
                self._handle_compound_mass(substance, mass)

        self.fMass = sum(self.afMass)
        self.arPartialMass = [m / self.fMass if self.fMass > 0 else 0 for m in self.afMass]

    def _handle_compound_mass(self, substance, mass):
        """
        Handles initialization for compound masses.
        """
        idx = self.oMT.tiN2I[substance]
        compound = self.oMT.ttxMatter[substance]

        for component, ratio in compound.trBaseComposition.items():
            comp_idx = self.oMT.tiN2I[component]
            self.arCompoundMass[idx][comp_idx] = ratio

    def set_temperature(self, fTemperature):
        """
        Sets the temperature for the phase.
        """
        self.fTemperature = fTemperature

    def massupdate(self):
        """
        Updates the mass-related properties of the phase.
        Should be called in the post-tick.
        """
        fTime = self.oTimer.fTime
        fLastStep = fTime - self.fLastMassUpdate

        if fLastStep == 0:
            self.set_outdated_ts()
            self.set_p2ps_and_manips_outdated()
            return

        self.fLastMassUpdate = fTime
        self.fMassUpdateTimeStep = fLastStep

        afTotalInOuts = self.afCurrentTotalInOuts
        afTotalInOuts = [flow * fLastStep for flow in afTotalInOuts]

        for i, mass in enumerate(self.afMass):
            self.afMass[i] += afTotalInOuts[i]
            if self.afMass[i] < 0:
                self.afMassGenerated[i] -= self.afMass[i]
                self.afMass[i] = 0

        self.fMass = sum(self.afMass)
        self.arPartialMass = [m / self.fMass if self.fMass > 0 else 0 for m in self.afMass]

        self.set_branches_outdated()
        self.set_p2ps_and_manips_outdated()
        self.set_outdated_ts()

    def set_branches_outdated(self):
        """
        Sets branches connected to this phase as outdated.
        """
        for exme in self.coProcsEXME:
            branch = exme.oFlow.oBranch
            branch.set_outdated()

    def set_p2ps_and_manips_outdated(self):
        """
        Sets manipulators and P2Ps connected to the phase as outdated.
        """
        if self.iSubstanceManipulators > 0:
            self.toManips.substance.register_update()
        if self.iVolumeManipulators > 0:
            self.toManips.volume.register_update()

    def set_outdated_ts(self):
        """
        Marks the phase's timestep as outdated for recalculation.
        """
        self.hBindPostTickTimeStep()

    @property
    def fPressure(self):
        """
        Calculates and returns the current pressure in the phase.
        """
        fMassSinceUpdate = self.fCurrentTotalMassInOut * (self.oTimer.fTime - self.fLastMassUpdate)
        return self.fMassToPressure * (self.fMass + fMassSinceUpdate)
