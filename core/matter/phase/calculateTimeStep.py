import numpy as np

def calculate_time_step(self):
    """
    Calculates the next timestep for the phase.
    Determines the new timestep based on mass changes, inflows, outflows, and various constraints.
    """
    # Get total mass change and details
    afChange, mfDetails, self.arInFlowCompoundMass = self.get_total_mass_change()
    afTmpCurrentTotalInOuts = self.afCurrentTotalInOuts

    # Update current inflow/outflow properties
    self.afCurrentTotalInOuts = afChange
    self.mfCurrentInflowDetails = mfDetails

    # Include substance manipulators if applicable
    if self.iSubstanceManipulators != 0:
        afPartialFlows = self.afCurrentTotalInOuts + self.toManips.substance.afPartialFlows
    else:
        afPartialFlows = self.afCurrentTotalInOuts

    # For boundary phases, use the maximum timestep
    if self.bBoundary:
        fNewStep = self.fMaxStep
    else:
        # Maximum timestep to avoid negative masses
        abOutFlows = afPartialFlows < 0
        fMaxFlowStep = min(abs((self.fMassErrorLimit + self.afMass[abOutFlows]) / afPartialFlows[abOutFlows]))

        if self.fFixedTimeStep is not None:
            fNewStep = self.fFixedTimeStep
        elif self.bFlow:
            fNewStep = self.fMaxStep
        else:
            # Calculate partial mass changes per second
            abChange = afPartialFlows != 0
            arPartialsChange = abs(afPartialFlows[abChange] / self.round_prec(self.fMass, self.iTimeStepPrecision))
            rPartialsPerSecond = max(arPartialsChange[~np.isinf(arPartialsChange)]) if arPartialsChange.size > 0 else 0

            # Total mass change per second
            fChange = sum(afPartialFlows)
            rTotalPerSecond = abs(self.round_prec(fChange, self.iTimeStepPrecision) / self.fMass) if fChange != 0 else 0

            # Partial mass changes compared to individual masses
            if self.bHasSubstanceSpecificMaxChangeValues:
                afCurrentMass = np.copy(self.afMass)
                afCurrentMass[self.afMass < 10 ** (-self.iTimeStepPrecision)] = 10 ** (-self.iTimeStepPrecision)
                arPartialChangeToPartials = abs(afPartialFlows / self.round_prec(afCurrentMass, self.iTimeStepPrecision))
                arPartialChangeToPartials[self.afMass == 0] = 0
                afNewStepPartialChangeToPartials = self.arMaxChange / arPartialChangeToPartials
                afNewStepPartialChangeToPartials[self.arMaxChange == 0] = float('inf')
                fNewStepPartialChangeToPartials = min(afNewStepPartialChangeToPartials)
            else:
                fNewStepPartialChangeToPartials = float('inf')

            # Calculate the new timestep
            fNewStepTotal = self.rMaxChange / rTotalPerSecond
            fNewStepPartials = self.rMaxChange / rPartialsPerSecond
            fNewStep = min(fNewStepTotal, fNewStepPartials, fNewStepPartialChangeToPartials)

            # Handle special cases for zero mass phases
            if self.fMass == 0:
                if fChange < 0:
                    fNewStep = abs(self.fMassErrorLimit / fChange)
                else:
                    fNewStep = abs(self.fMaximumInitialMass / fChange)

    # Ensure timestep is within allowable bounds
    if fNewStep > self.fMaxStep:
        fNewStep = self.fMaxStep
        self.log_debug(2, "max-time-step", f"Setting maximum timestep: {fNewStep:.16f}s")

    elif fNewStep < self.fMinStep:
        fNewStep = self.fMinStep
        self.log_debug(2, "min-time-step", f"Setting minimum timestep: {fNewStep:.16f}s")

    # Debugging outputs
    self.log_debug(1, "new-timestep", f"New timestep: {fNewStep:.16f}s")
    self.log_debug(1, "mass-changes", f"Mass: {self.fMass:.16f} kg, Change Rate: {sum(self.afCurrentTotalInOuts):.16f} kg/s")

    # Compare with the maximum flow timestep
    if fNewStep > fMaxFlowStep:
        fNewStep = fMaxFlowStep
        if fNewStep < self.fMinStep:
            fNewStep = self.fMinStep

    # Update the phase's timestep
    if self.fLastUpdate == self.oTimer.fTime or self.bFlow:
        self.set_time_step(fNewStep, reset_last_exec=True)
    else:
        self.set_time_step(fNewStep)

    # Cache the timestep for logging or further processing
    self.fTimeStep = fNewStep
