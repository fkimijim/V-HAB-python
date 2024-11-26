from abc import ABC
import numpy as np
from .. import StepVolumeManipulator

StepVolumeManipulator = StepVolumeManipulator()

class CompressibleMedium(StepVolumeManipulator, ABC):
    """
    This volume manipulator identifies a phase as compressible and
    handles the required volume calculations with respect to other phases
    in the store to respect the compressible nature of this phase.
    """

    # Identifies this manipulator as a stationary volume manipulator
    bCompressible = True

    def __init__(self, sName, oPhase):
        """
        Class constructor for CompressibleMedium.

        Parameters:
        - sName: str, Name for this manipulator.
        - oPhase: Phase, The phase object where this manipulator is located.
        """
        super().__init__(sName, oPhase)

    def reattach_manip(self, oPhase):
        """
        Reattach the manipulator to a phase, binding necessary triggers.

        Parameters:
        - oPhase: Phase, The phase object to reattach to.
        """
        super().reattach_manip(oPhase)

        # Bind the update function to the phase's update_post trigger
        self.oPhase.bind("update_post", self.update)

    def update(self, fNewVolume=None, fNewPressure=None):
        """
        Calculate or set the new volume and pressure of the compressible phase.

        Parameters:
        - fNewVolume: float, The new volume for the phase in m^3 (optional).
        - fNewPressure: float, The new pressure for the phase in Pa (optional).
        """
        fElapsedTime = self.oTimer.fTime - self.fLastExec

        if fElapsedTime > 0:
            if fNewVolume is not None and fNewPressure is not None:
                # If new volume and pressure are provided, set them directly
                super().update(fNewVolume, fNewPressure)
            elif self.oPhase.bUpdateRegistered:
                # Gather information from all phases in the store
                afDensityIncompressiblePhase = np.zeros(self.oPhase.oStore.iPhases)
                afVolumeIncompressiblePhase = np.zeros(self.oPhase.oStore.iPhases)
                abCompressiblePhase = np.zeros(self.oPhase.oStore.iPhases, dtype=bool)

                for iPhase, oOtherPhase in enumerate(self.oPhase.oStore.aoPhases):
                    if not oOtherPhase.toManips.volume.bCompressible:
                        afDensityIncompressiblePhase[iPhase] = oOtherPhase.fDensity
                        afVolumeIncompressiblePhase[iPhase] = (
                            oOtherPhase.fMass / afDensityIncompressiblePhase[iPhase]
                        )
                    else:
                        abCompressiblePhase[iPhase] = True

                fRemainingVolume = self.oPhase.oStore.fVolume - sum(afVolumeIncompressiblePhase)

                if fRemainingVolume < 0:
                    raise ValueError(
                        f"Time step too large in store {self.sName}: compressible volume became negative."
                    )

                iCompressiblePhases = np.sum(abCompressiblePhase)
                if iCompressiblePhases > 1:
                    # Handle multiple compressible phases
                    aiCompressiblePhase = np.where(abCompressiblePhase)[0]

                    afDensityCompressiblePhase = np.zeros(iCompressiblePhases)
                    afMassCompressiblePhase = np.zeros(iCompressiblePhases)
                    afVolumeCompressiblePhase = np.zeros(iCompressiblePhases)
                    afPressureCompressiblePhase = np.zeros(iCompressiblePhases)

                    for idx, phase_idx in enumerate(aiCompressiblePhase):
                        oCompressiblePhase = self.oPhase.oStore.aoPhases[phase_idx]
                        afDensityCompressiblePhase[idx] = self.oMT.calculate_density(oCompressiblePhase)
                        afMassCompressiblePhase[idx] = oCompressiblePhase.fMass
                        afVolumeCompressiblePhase[idx] = (
                            oCompressiblePhase.fMass / afDensityCompressiblePhase[idx]
                        )
                        afPressureCompressiblePhase[idx] = oCompressiblePhase.fPressure

                    # Initial volume distribution
                    afVolumesBoundary1 = (
                        afVolumeCompressiblePhase / sum(afVolumeCompressiblePhase)
                    ) * fRemainingVolume

                    afError1 = np.zeros_like(afVolumesBoundary1)
                    afError2 = np.copy(afError1)
                    iCounter = 0
                    iMaxIterations = 100

                    # Iteratively adjust volumes
                    while any(np.sign(afError1) == np.sign(afError2)) and iCounter < iMaxIterations:
                        aiSigns = np.sign(afError2)
                        aiPositiveSigns = np.where(aiSigns > 0)[0]
                        aiNegativeSigns = np.where(aiSigns < 0)[0]

                        afVolumesBoundary2 = np.copy(afVolumesBoundary1)
                        afVolumesBoundary2[aiPositiveSigns] *= 1.00001
                        afVolumesBoundary2[aiNegativeSigns] *= 0.99999

                        afVolumesBoundary2 = (
                            afVolumesBoundary2 / sum(afVolumesBoundary2)
                        ) * fRemainingVolume

                        afNewDensities = afMassCompressiblePhase / afVolumesBoundary2

                        afNewPressure = np.array([
                            self.oMT.calculate_pressure(
                                self.oPhase.sType,
                                self.oPhase.afMass,
                                self.oPhase.fTemperature,
                                density,
                            )
                            for density in afNewDensities
                        ])
                        afError2 = afNewPressure - np.mean(afNewPressure)

                        iCounter += 1

                    if iCounter >= iMaxIterations:
                        raise ValueError("Compressible medium calculation exceeded max iterations.")

                    # Final volume assignment for this phase
                    fVolumeThisPhase = afVolumesBoundary2[aiCompressiblePhase.index(self.oPhase)]
                    super().update(fVolumeThisPhase)
                else:
                    # Single compressible phase: remaining volume is assigned to it
                    fVolumeThisPhase = fRemainingVolume
                    super().update(fVolumeThisPhase)
